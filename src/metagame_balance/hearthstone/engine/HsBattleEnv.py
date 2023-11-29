import random
from multiprocessing.connection import Client
from typing import List, Tuple

import gym
import numpy as np
from gym import spaces

from metagame_balance.hearthstone.competition.StandardHsMoves import Struggle
from metagame_balance.hearthstone.datatypes.Constants import DEFAULT_PKM_N_MOVES, MAX_HIT_POINTS, STATE_DAMAGE, SPIKES_2, SPIKES_3, \
    TYPE_CHART_MULTIPLIER, DEFAULT_N_ACTIONS
from metagame_balance.hearthstone.datatypes.Objects import HsTeam, Hs, get_game_state_view, GameState, Weather
from metagame_balance.hearthstone.datatypes.Types import WeatherCondition, HsEntryHazard, HsType, HsStatus, HsStat, N_HAZARD_STAGES, \
    MIN_STAGE, MAX_STAGE
from metagame_balance.hearthstone.util.Encoding import GAME_STATE_ENCODE_LEN, partial_encode_game_state


class HsBattleEnv(gym.Env):

    def __init__(self, teams: Tuple[HsTeam, HsTeam] = None, debug: bool = False, team_prediction=None,
                 conn: Client = None):
        # random active pokemon
        self.n_turns_no_clear = None
        if team_prediction is None:
            team_prediction = [None, None]
        if teams is None:
            self.teams: Tuple[HsTeam, HsTeam] = (HsTeam(), HsTeam())
        else:
            self.teams: Tuple[HsTeam, HsTeam] = teams
        self.team_prediction = team_prediction
        self.weather = Weather()
        self.switched = [False, False]
        self.turn = 0
        self.move_view = self.__create_hs_move_view()
        self.game_state = [GameState([self.teams[0], self.teams[1]], self.weather),
                           GameState([self.teams[1], self.teams[0]], self.weather)]
        self.game_state_view = [get_game_state_view(self.game_state[0], team_prediction=self.team_prediction[0]),
                                get_game_state_view(self.game_state[1], team_prediction=self.team_prediction[1])]
        self.debug = debug
        self.log = ''
        self.commands = []
        self.conn = conn
        self.action_space = spaces.Discrete(DEFAULT_N_ACTIONS)
        self.observation_space = spaces.Discrete(GAME_STATE_ENCODE_LEN)
        self.winner = -1

    def step(self, actions):

        # Reset variables
        r = [0., 0.]
        t = [False, False]
        if self.debug:
            self.turn += 1
            self.log = f'TURN {self.turn}\n\n'
            self.commands.append(('event', ['log', f'Turn {self.turn}.']))

        # switch hs
        self.__process_switch_hss(actions)

        # set trainer attack order
        first, second = self.__get_attack_order(actions)
        first_team = self.teams[first]
        first_hs = first_team.active
        second_team = self.teams[second]
        second_hs = second_team.active

        # get entry hazard damage
        dmg_2_first = self.__get_entry_hazard_damage(first)
        dmg_2_second = self.__get_entry_hazard_damage(second)

        r[first] = (dmg_2_second - dmg_2_first) / MAX_HIT_POINTS
        r[second] = (dmg_2_first - dmg_2_second) / MAX_HIT_POINTS

        active_not_fainted = not (first_hs.fainted() or second_hs.fainted())

        # process all pre battle effects
        self.__process_pre_battle_effects()

        # confusion state damage
        dmg_2_first = self.__get_pre_combat_damage(first) if active_not_fainted else 0.
        dmg_2_second = self.__get_pre_combat_damage(second) if active_not_fainted else 0.

        first_confusion_damage = dmg_2_first > 0.
        second_confusion_damage = dmg_2_second > 0.

        r[first] += (dmg_2_second - dmg_2_first) / MAX_HIT_POINTS
        r[second] += (dmg_2_first - dmg_2_second) / MAX_HIT_POINTS

        active_not_fainted = not (first_hs.fainted() or second_hs.fainted())

        # battle
        first_can_attack = active_not_fainted and not first_hs.paralyzed() and not first_hs.asleep() and not \
            first_confusion_damage
        if self.debug and not first_can_attack:
            self.log += f'CANNOT MOVE: Trainer {first} cannot move\n'
            self.commands.append(('event', ['log', f'Trainer {first} cannot move.']))
        dmg_2_second, hp_2_first = self.__perform_hs_attack(first, actions[first]) if first_can_attack else (0., 0.)

        active_not_fainted = not (first_hs.fainted() or second_hs.fainted())

        second_can_attack = active_not_fainted and not second_hs.paralyzed() and not second_hs.asleep() and not \
            second_confusion_damage
        if self.debug and not second_can_attack:
            self.log += f'CANNOT MOVE: Trainer {second} cannot move\n'
            self.commands.append(('event', ['log', f'Trainer {second} cannot move.']))
        dmg_2_first, hp_2_second = self.__perform_hs_attack(second, actions[second]) if second_can_attack else (0., 0.)

        r[first] += (dmg_2_second + hp_2_first - dmg_2_first) / MAX_HIT_POINTS + float(second_hs.fainted())
        r[second] += (dmg_2_first + hp_2_second - dmg_2_second) / MAX_HIT_POINTS + float(first_hs.fainted())

        # get post battle effects damage
        dmg_2_first = self.__get_post_battle_damage(first) if first_can_attack else 0.
        dmg_2_second = self.__get_post_battle_damage(second) if second_can_attack else 0.

        r[first] += (dmg_2_second - dmg_2_first) / MAX_HIT_POINTS
        r[second] += (dmg_2_first - dmg_2_second) / MAX_HIT_POINTS

        # process all post battle effects
        self.__process_post_battle_effects()

        # switch fainted hs
        dmg_2_first, dmg_2_second = self.__switch_fainted_hs()

        r[first] += (dmg_2_second - dmg_2_first) / MAX_HIT_POINTS
        r[second] += (dmg_2_first - dmg_2_second) / MAX_HIT_POINTS

        # check if battle ended
        t[first] = first_team.fainted()
        t[second] = second_team.fainted()

        r[first] += float(t[first])
        r[second] += float(t[second])

        finished = t[0] or t[1]

        if finished:
            self.winner = 1 if t[0] else 0

            if self.debug:
                outcome0 = 'Lost' if self.teams[0].fainted() else 'Won'
                outcome1 = 'Lost' if self.teams[1].fainted() else 'Won'
                self.log += f'\nTrainer 0 {outcome0}\n'
                self.log += f'Trainer 1 {outcome1}\n'
                self.commands.append(('event', ['log', f'Trainer 0 {outcome0}.']))

        e0, e1 = [], []
        partial_encode_game_state(e0, self.game_state[0])
        partial_encode_game_state(e1, self.game_state[1])
        return [e0, e1], r, finished, self.game_state_view

    def reset(self):
        self.weather.condition = WeatherCondition.CLEAR
        self.weather.n_turns_no_clear = 0
        self.turn = 0
        self.winner = -1
        self.switched = [False, False]

        for team in self.teams:
            team.reset()

        if self.debug:
            self.log = 'Trainer 0\n' + str(self.teams[0])
            self.log += '\nTrainer 1\n' + str(self.teams[1])
            del self.commands[:]
            self.commands.append(('init', [self.teams[0].active.type.value,
                                           self.teams[0].party[0].type.value,
                                           self.teams[0].party[1].type.value,
                                           self.teams[0].active.hp,
                                           self.teams[0].active.moves[0].power,
                                           self.teams[0].active.moves[1].power,
                                           self.teams[0].active.moves[2].power,
                                           self.teams[0].active.moves[3].power,
                                           self.teams[1].active.type.value,
                                           self.teams[1].party[0].type.value,
                                           self.teams[1].party[1].type.value,
                                           self.teams[1].active.hp]))

        e0, e1 = [], []
        partial_encode_game_state(e0, self.game_state[0], self.team_prediction[0])
        partial_encode_game_state(e1, self.game_state[1], self.team_prediction[1])
        return [e0, e1]

    def render(self, mode='console'):
        if mode == 'console':
            print(self.log)
        elif mode == 'ux' and self.conn is not None:
            while len(self.commands) > 0:
                self.conn.send(self.commands.pop(0))

    def __process_switch_hss(self, actions: List[int]):
        """
        Switch hs if players chosen to do so.

        :param actions: players actions
        :return:
        """
        for i, team in enumerate(self.teams):
            pos = actions[i] - DEFAULT_PKM_N_MOVES
            if 0 <= pos < (team.size() - 1):
                if not team.party[pos].fainted():
                    new_active, old_active, _ = team.switch(pos)
                    self.switched[i] = True
                    if self.debug:
                        self.log += f'SWITCH: Trainer {i} switches {old_active} with {new_active} in party\n'
                        self.commands.append(('switch', [i, pos, new_active.hp,
                                                         new_active.moves[0].power,
                                                         new_active.moves[1].power,
                                                         new_active.moves[2].power,
                                                         new_active.moves[3].power]))
                elif self.debug:
                    self.log += f'SWITCH FAILED: Trainer {i} fails to switch\n'
                    self.commands.append(('event', ['log', f'Trainer {i} fails to switch.']))
            elif self.debug and pos >= (team.size() - 1):
                self.log += f'INVALID SWITCH: Trainer {i} fails to switch\n'
                self.commands.append(('event', ['log', f'Trainer {i} fails to switch.']))

    def __get_entry_hazard_damage(self, t_id: int) -> float:
        """
        Get triggered damage to be dealt to a switched hs.

        :param: t_id: owner trainer
        :return: damage to first hs, damage to second hs
        """
        damage = 0.
        team = self.teams[t_id]
        hs = team.active
        spikes = team.entry_hazard[HsEntryHazard.SPIKES]

        # Spikes damage
        if spikes and hs.type != HsType.FLYING and self.switched[t_id]:
            before_hp = hs.hp
            hs.hp -= STATE_DAMAGE if spikes <= 1 else SPIKES_2 if spikes == 2 else SPIKES_3
            hs.hp = 0. if hs.hp < 0. else hs.hp
            damage = before_hp - hs.hp
            self.switched[t_id] = False
            if self.debug and damage > 0.:
                self.log += f'ENTRY HAZARD DAMAGE: {str(hs)} takes {damage} entry hazard damage from spikes, ' \
                            f'hp reduces from {before_hp} to {hs.hp}\n '
                self.commands.append(('event', ['log', f'Trainer {team} takes {damage} damage from spikes.']))
                self.commands.append(('event', ['hp', team, hs.hp]))

        return damage

    def __process_pre_battle_effects(self):
        """
        Process all pre battle effects.

        """
        # for all trainers
        for i in range(len(self.teams)):

            team = self.teams[i]
            hs = team.active

            # check if active hs should be no more confused
            if team.confused:
                team.n_turns_confused += 1
                if random.uniform(0, 1) <= 0.5 or team.n_turns_confused == 4:
                    team.confused = False
                    team.n_turns_confused = 0
                    if self.debug:
                        self.log += f'STATUS: Trainer {i}\'s {str(hs)} is no longer confused\n'
                        self.commands.append(('event', ['log', f'Trainer {i} active is no longer confused.']))

            # check if active hs should be no more asleep
            if hs.asleep():
                hs.n_turns_asleep += 1
                if random.uniform(0, 1) <= 0.5 or hs.n_turns_asleep == 4:
                    hs.status = HsStatus.NONE
                    hs.n_turns_asleep = 0
                    if self.debug:
                        self.log += f'STATUS: Trainer {i}\'s {str(hs)} is no longer asleep\n'
                        self.commands.append(('event', ['log', f'Trainer {i} active is no longer asleep.']))

    def __process_post_battle_effects(self):
        """
        Process all post battle effects.

        """
        if self.weather.condition != WeatherCondition.CLEAR:
            self.n_turns_no_clear += 1

            # clear weather if appropriated
            if self.n_turns_no_clear > 5:
                self.weather.condition = WeatherCondition.CLEAR
                self.n_turns_no_clear = 0
                if self.debug:
                    self.log += 'STATE: The weather is clear\n'
                    self.commands.append(('event', ['log', f'The weather is clear.']))

    def __get_post_battle_damage(self, t_id: int) -> float:
        """
        Get triggered damage to be dealt to switched hs.

        :param: t_id: owner trainer
        :return: damage to hs
        """
        hs = self.teams[t_id].active
        state_damage = 0.

        if self.weather.condition == WeatherCondition.SANDSTORM and (
                hs.type != HsType.ROCK and hs.type != HsType.GROUND and hs.type != HsType.STEEL):
            state_damage = STATE_DAMAGE
        elif self.weather.condition == WeatherCondition.HAIL and (hs.type != HsType.ICE):
            state_damage = STATE_DAMAGE

        before_hp = hs.hp
        hs.hp -= state_damage
        hs.hp = 0. if hs.hp < 0. else hs.hp
        damage = before_hp - hs.hp

        if self.debug and state_damage > 0.:
            self.log += 'STATE DAMAGE: %s takes %s weather damage from sandstorm/hail hp reduces from %s to %s\n' % (
                str(hs), damage, before_hp, hs.hp)
            self.commands.append(('event', ['log', f'Trainer {t_id} takes {damage} damage from sandstorm/hail.']))
            self.commands.append(('event', ['hp', t_id, hs.hp]))

        if hs.status == HsStatus.POISONED or hs.status == HsStatus.BURNED:
            state_damage = STATE_DAMAGE

            before_hp = hs.hp
            hs.hp -= state_damage
            hs.hp = 0. if hs.hp < 0. else hs.hp
            damage = before_hp - hs.hp

            if self.debug and damage > 0.:
                self.log += 'STATE DAMAGE: %s takes %s state damage from %s, hp reduces from %s to %s\n' % (
                    str(hs), damage, 'poison' if hs.status == HsStatus.POISONED else 'burn', before_hp, hs.hp)
                self.commands.append(('event', ['log', f'Trainer {t_id} takes {damage} damage from poison/burn.']))
                self.commands.append(('event', ['hp', t_id, hs.hp]))

        return damage

    def __get_attack_order(self, actions) -> Tuple[int, int]:
        """
        Get attack order for this turn.
        Priority is given to the hs with highest speed_stage. Otherwise random.

        :return: tuple with first and second trainer to perform attack
        """
        action0 = actions[0]
        action1 = actions[1]
        speed0 = self.teams[0].stage[HsStat.SPEED] + (
            self.teams[0].active.moves[action0].priority if action0 < DEFAULT_PKM_N_MOVES else 0)
        speed1 = self.teams[1].stage[HsStat.SPEED] + (
            self.teams[1].active.moves[action1].priority if action1 < DEFAULT_PKM_N_MOVES else 0)
        if speed0 > speed1:
            order = [0, 1]
        elif speed1 < speed0:
            order = [1, 0]
        else:
            # random attack order
            order = [0, 1]
            np.random.shuffle(order)

        return order[0], order[1]

    class HsMoveView:

        def __init__(self, engine):
            self.__engine = engine
            self._damage: float = 0.
            self._recover: float = 0.
            self._team: List[HsTeam] = []
            self._active: List[Hs] = []

        def set_weather(self, weather: WeatherCondition):
            if weather != self.__engine.weather.condition:
                self.__engine.weather.condition = weather
                self.__engine.n_turns_no_clear = 0
                if self.__engine.debug:
                    self.__engine.log += f'STATE: The weather is now {weather.name}\n'
                    self.__engine.commands.append(('event', ['log', f'The weather is now {weather.name}.']))

        def set_fixed_damage(self, damage: float):
            self._damage = damage

        def set_recover(self, recover: float):
            self._recover = recover

        def set_status(self, status: HsStatus, t_id: int = 1):
            hs = self._active[t_id]
            team = self._team[t_id]
            if status == HsStatus.PARALYZED and hs.type != HsType.ELECTRIC and hs.type != HsType.GROUND and \
                    hs.status != HsStatus.PARALYZED:
                hs.status = HsStatus.PARALYZED
                if self.__engine.debug:
                    self.__engine.log += f'STATUS: {str(hs)} was paralyzed\n'
                    self.__engine.commands.append(('event', ['log', f'Trainer {t_id} is now paralyzed.']))
            elif status == HsStatus.POISONED and hs.type != HsType.POISON and hs.type != HsType.STEEL and \
                    hs.status != HsStatus.POISONED:
                hs.status = HsStatus.POISONED
                if self.__engine.debug:
                    self.__engine.log += f'STATUS: {str(hs)} was poisoned\n'
                    self.__engine.commands.append(('event', ['log', f'Trainer {t_id} is now poisoned.']))
            elif status == HsStatus.SLEEP and hs.status != HsStatus.SLEEP:
                hs.status = HsStatus.SLEEP
                hs.n_turns_asleep = 0
                if self.__engine.debug:
                    self.__engine.log += f'STATUS: {str(hs)} is now asleep\n'
                    self.__engine.commands.append(('event', ['log', f'Trainer {t_id} is now asleep.']))
            elif not team.confused:
                team.confused = True
                if self.__engine.debug:
                    self.__engine.log += f'STATUS: {str(hs)} is now confused\n'
                    self.__engine.commands.append(('event', ['log', f'Trainer {t_id} is now confused.']))

        def set_stage(self, stat: HsStat = HsStat.ATTACK, delta_stage: int = 1, t_id: int = 1):
            if delta_stage != 0:
                team = self._team[t_id]
                if MIN_STAGE < team.stage[stat] < MAX_STAGE:
                    team.stage[stat] += delta_stage
                    if team.stage[stat] < MIN_STAGE:
                        team.stage[stat] = MIN_STAGE
                    elif team.stage[stat] > MAX_STAGE:
                        team.stage[stat] = MAX_STAGE
                    if self.__engine.debug:
                        self.__engine.log += 'STAGE: %s %s %s\n' % (
                            str(team.active), stat.name, 'increased' if delta_stage > 0 else 'decreased')
                        self.__engine.commands.append(('event', [stat.name, t_id, team.stage[stat]]))

        def set_entry_hazard(self, hazard: HsEntryHazard = HsEntryHazard.SPIKES, t_id: int = 1):
            team = self.__engine.teams[t_id]
            team.entry_hazard[hazard] += 1
            if team.entry_hazard[hazard] >= N_HAZARD_STAGES:
                team.entry_hazard[hazard] = N_HAZARD_STAGES - 1
            elif self.__engine.debug:
                self.__engine.log += f'ENTRY HAZARD: Trainer {t_id} gets spikes\n'
                self.__engine.commands.append(('event', ['log', f'Trainer {t_id} gets spikes.']))

        @property
        def recover(self):
            return self._recover

        @property
        def damage(self):
            return self._damage

    def __get_fixed_damage(self) -> float:
        damage = self.move_view.damage
        self.move_view._damage = 0.
        return damage

    def __get_recover(self) -> float:
        recover = self.move_view.recover
        self.move_view._recover = 0.
        return recover

    def __create_hs_move_view(self):
        return HsBattleEnv.HsMoveView(self)

    def __get_attack_dmg_rcvr(self, t_id: int, m_id: int) -> Tuple[float, float]:
        """
        Get damage and recover done by an attack m_id of active hs of trainer t_id

        :param t_id: trainer of the active hs
        :param m_id: move of the active hs
        :return: damage, recover
        """

        team = self.teams[t_id]
        hs = team.active
        move = hs.moves[m_id]

        if move.pp > 0:
            move.pp -= 1
        else:
            move = Struggle

        if move.acc <= random.random():
            if self.debug:
                self.log += 'MOVE FAILS: Trainer %s with %s fails %s\n' % (t_id, str(hs), str(move))
                self.commands.append(('event', ['log', f'Trainer {t_id} active fails its move.']))
            return 0., 0.

        opp = not t_id
        opp_team = self.teams[opp]
        opp_hs = opp_team.active

        if self.debug:
            self.log += 'MOVE: Trainer %s with %s uses %s\n' % (t_id, str(hs), str(move))
            self.commands.append(('attack', [t_id, move.type.value, move.power > 0.]))

        self.move_view._team = [team, opp_team]
        self.move_view._active = [hs, opp_hs]
        move.effect(self.move_view)

        # set recover
        recover = self.__get_recover()

        # calculate damage
        fixed_damage = self.__get_fixed_damage()
        if fixed_damage > 0. and TYPE_CHART_MULTIPLIER[move.type][opp_hs.type] > 0.:
            damage = fixed_damage
        else:
            stab = 1.5 if move.type == hs.type else 1.
            if (move.type == HsType.WATER and self.weather.condition == WeatherCondition.RAIN) or (
                    move.type == HsType.FIRE and self.weather.condition == WeatherCondition.SUNNY):
                weather = 1.5
            elif (move.type == HsType.WATER and self.weather.condition == WeatherCondition.SUNNY) or (
                    move.type == HsType.FIRE and self.weather.condition == WeatherCondition.RAIN):
                weather = .5
            else:
                weather = 1.
            stage_level = team.stage[HsStat.ATTACK] - opp_team.stage[HsStat.DEFENSE]
            stage = (stage_level + 2.) / 2 if stage_level >= 0. else 2. / (np.abs(stage_level) + 2.)
            multiplier = TYPE_CHART_MULTIPLIER[move.type][opp_hs.type] if move != Struggle else 1.0
            damage = multiplier * stab * weather * stage * move.power

        return round(damage), round(recover)

    def __perform_hs_attack(self, t_id: int, m_id: int) -> Tuple[float, float]:
        """
        Perform a hs attack

        :param t_id: trainer
        :param m_id: move
        :return: reward, recover
        """
        damage, recover = 0., 0.

        if m_id < DEFAULT_PKM_N_MOVES:
            opponent = not t_id
            hs = self.teams[t_id].active
            before_hp = hs.hp
            opp_hs = self.teams[opponent].active
            before_opp_hp = opp_hs.hp

            # get damage and recover values from attack
            damage_2_deal, health_2_recover = self.__get_attack_dmg_rcvr(t_id, m_id)

            # perform recover
            hs.hp += health_2_recover
            hs.hp = MAX_HIT_POINTS if hs.hp > MAX_HIT_POINTS else hs.hp
            recover = hs.hp - before_hp
            if self.debug and recover > 0.:
                self.log += f'RECOVER: recovers {recover}\n'
                self.commands.append(('event', ['log', f'Trainer {t_id} active recovers.']))
                self.commands.append(('event', ['hp', t_id, hs.hp]))
            elif self.debug and recover < 0.:
                self.log += f'RECOIL DAMAGE: gets {-recover} recoil damage\n'
                self.commands.append(('event', ['log', f'Trainer {t_id} active takes recoil damage.']))
                self.commands.append(('event', ['hp', t_id, hs.hp]))

            # perform damage
            opp_hs.hp -= damage_2_deal
            opp_hs.hp = 0. if opp_hs.hp < 0. else opp_hs.hp
            damage = before_opp_hp - opp_hs.hp
            if self.debug and damage > 0.:
                self.log += 'DAMAGE: deals %s damage, hp reduces from %s to %s for %s\n' % (
                    damage, before_opp_hp, opp_hs.hp, str(opp_hs))
                self.commands.append(('event', ['log', f'Trainer {1 if opponent else 0} active takes damage.']))
                self.commands.append(('event', ['hp', 1 if opponent else 0, opp_hs.hp]))

        return damage, recover

    def __get_pre_combat_damage(self, t_id: int) -> float:
        """
        Check if trainer t_id active hs is confused this turn and cannot move and take damage.

        :param t_id: trainer
        :return: 0. if not confused or damage to take if confused
        """
        return STATE_DAMAGE if self.teams[t_id].confused and random.uniform(0, 1) <= 0.33 else 0.

    def __switch_fainted_hs(self) -> Tuple[float, float]:
        """
        Recursive damage dealt to fainted switched hs, while faiting for entry hazard.

        :return: damage to hs 0, damage to hs 1
        """
        damage0, damage1 = 0., 0.
        self.switched = [False, False]
        team0 = self.teams[0]
        team1 = self.teams[1]
        hs0 = self.teams[0].active
        hs1 = self.teams[1].active
        if hs0.fainted():
            if self.debug:
                self.log += 'FAINTED: %s\n' % (str(hs0))
                self.commands.append(('event', ['log', f'Trainer 0 active fainted.']))
            new_active, _, pos = team0.switch(-1)
            if self.debug:
                if pos != -1:
                    self.commands.append(('switch', [0, pos, new_active.hp,
                                                     new_active.moves[0].power,
                                                     new_active.moves[1].power,
                                                     new_active.moves[2].power,
                                                     new_active.moves[3].power]))
        if hs1.fainted():
            if self.debug:
                self.log += 'FAINTED: %s\n' % (str(hs1))
                self.commands.append(('event', ['log', f'Trainer 1 active fainted.']))
            new_active, _, pos = team1.switch(-1)
            if self.debug:
                if pos != -1:
                    self.commands.append(('switch', [1, pos, new_active.hp]))
        if not hs0.fainted():
            damage0 = self.__get_entry_hazard_damage(0)
        if not hs1.fainted():
            damage1 = self.__get_entry_hazard_damage(1)
        d0, d1 = 0., 0.
        if (hs0.fainted() or hs1.fainted()) and (not team0.fainted() and not team1.fainted()):
            d0, d1 = self.__switch_fainted_hs()
        return damage0 + d0, damage1 + d1

    def close(self):
        if self.conn is not None:
            self.conn.close()
