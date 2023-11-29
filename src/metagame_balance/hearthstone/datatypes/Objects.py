import random
from abc import ABC, abstractmethod
from copy import deepcopy
from math import isclose
from typing import List, Tuple, Set, Union, Mapping, Text, Dict, Any, Type

import numpy as np

from metagame_balance.hearthstone.datatypes.Constants import MOVE_MED_PP, MAX_HIT_POINTS
from metagame_balance.hearthstone.datatypes.Types import HsType, HsStatus, N_STATS, N_ENTRY_HAZARD, HsStat, WeatherCondition, \
    HsEntryHazard


JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]

class HsMove:

    def __init__(self, power: float = 30., acc: float = 1., max_pp: int = MOVE_MED_PP,
                 move_type: HsType = HsType.NORMAL, name: str = None, priority: bool = False,
                 prob=0.0, target=1, recover=0.0, status: HsStatus = HsStatus.NONE,
                 stat: HsStat = HsStat.ATTACK, stage: int = 0, fixed_damage: float = 0.0,
                 weather: WeatherCondition = WeatherCondition.CLEAR, hazard: HsEntryHazard = HsEntryHazard.NONE):
        """
        Pokemon move data structure.

        :param power: move power
        :param acc: move accuracy
        :param max_pp: move max power points
        :param move_type: move type
        :param name: move name
        :param priority: move priority
        :param prob: move effect probability (only moves with probability greater than zero perform effects)
        :param target: move effect target, zero for self and 1 for opponent
        :param recover: move recover quantity, how much hit points to recover
        :param status: status the move effect changes
        :param stage: stage the move effect adds/subtracts from the status
        :param fixed_damage: effect fixed_damage to apply, not affected by resistance or weakness (if greater than zero)
        :param weather: effect activates a weather condition
        :param hazard: effect deploys and hazard enter condition on the opponent field
        """
        self.power = power
        self.acc = acc
        self.max_pp = max_pp
        self.pp = max_pp
        self.type = move_type
        self.name = name
        self.priority = priority
        self.prob = prob
        self.target = target
        self.recover = recover
        self.status = status
        self.stat = stat
        self.stage = stage
        self.fixed_damage = fixed_damage
        self.weather = weather
        self.hazard = hazard
        self.public = False
        self.owner = None

    def to_dict(self) -> Mapping[Text, JSON]:
        return {
            "power": self.power,
            "acc": self.acc,
            "max_pp": self.max_pp,
            "type": self.type.name,
            "name": self.name or "unknown_move",
            "priority": self.priority,
            "prob": self.prob,
            "target": self.target,
            "recover": self.recover,
            "status": self.status.name,
            "stage": self.stage,
            "fixed_damage": self.fixed_damage,
            "weather": self.weather.name,
            "hazard": self.hazard.name
        }

    def __eq__(self, other):
        """
        Moves equal if name is equal (use name as id)
        """
        return self.name == other.name

    def __hash__(self):
        """
        Just hash based on name for meta balance!
        """
        if self.name == None:
            print(self)
        return hash(self.name)

    def __str__(self):
        if self.name:
            return self.name
        name = "HsMove(Power=%f, Acc=%f, PP=%d, Type=%s" % (self.power, self.acc, self.pp, self.type.name)
        if self.priority > 0:
            name += ", Priority=%d" % self.priority
        if self.prob > 0.:
            if self.prob < 1.:
                name += ", Prob=%f" % self.prob
            name += ", Target=Self" if self.target == 0 else ", Target=Opp"
            if self.recover > 0.:
                name += ", Recover=%f" % self.recover
            if self.status != HsStatus.NONE:
                name += ", Status=%s" % self.status.name
            if self.stage != 0.:
                name += ", Stat=%s, Stage=%d" % (self.stat.name, self.stage)
            if self.fixed_damage > 0.:
                name += ", Fixed=%f" % self.fixed_damage
            if self.weather != self.weather.CLEAR:
                name += ", Weather=%s" % self.weather.name
            if self.hazard != HsEntryHazard.NONE:
                name += ", Hazard=%s" % self.hazard.name
        return name + ")"

    def set_owner(self, hs):
        self.owner = hs

    def reset(self):
        self.pp = self.max_pp

    def effect(self, v):
        self.reveal()
        if random.random() < self.prob:
            v.set_recover(self.recover)
            v.set_fixed_damage(self.fixed_damage)
            if self.stage != 0:
                v.set_stage(self.stat, self.stage, self.target)
            if self.status != self.status.NONE:
                v.set_status(self.status, self.target)
            if self.weather != self.weather.CLEAR:
                v.set_weather(self.weather)
            if self.hazard != HsEntryHazard.NONE:
                v.set_entry_hazard(self.hazard, self.target)

    def reveal(self):
        self.public = True

    def hide(self):
        self.public = False

    @property
    def revealed(self) -> bool:
        if self.owner is not None:
            return self.owner.revealed and self.public
        return self.public


class MoveView(ABC):

    @property
    @abstractmethod
    def power(self) -> float:
        pass

    @property
    @abstractmethod
    def acc(self) -> float:
        pass

    @property
    @abstractmethod
    def pp(self) -> int:
        pass

    @property
    @abstractmethod
    def max_pp(self) -> int:
        pass

    @property
    @abstractmethod
    def type(self) -> HsType:
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        pass

    @property
    @abstractmethod
    def prob(self) -> float:
        pass

    @property
    @abstractmethod
    def target(self) -> int:
        pass

    @property
    @abstractmethod
    def recover(self) -> float:
        pass

    @property
    @abstractmethod
    def status(self) -> HsStatus:
        pass

    @property
    @abstractmethod
    def stat(self) -> HsStat:
        pass

    @property
    @abstractmethod
    def stage(self) -> int:
        pass

    @property
    @abstractmethod
    def fixed_damage(self) -> float:
        pass

    @property
    @abstractmethod
    def weather(self) -> WeatherCondition:
        pass

    @property
    @abstractmethod
    def hazard(self) -> HsEntryHazard:
        pass


def get_move_view(move: HsMove) -> MoveView:
    class MoveViewImpl(MoveView):

        @property
        def power(self) -> float:
            return move.power

        @property
        def acc(self) -> float:
            return move.acc

        @property
        def pp(self) -> int:
            return move.pp

        @property
        def max_pp(self) -> int:
            return move.max_pp

        @property
        def type(self) -> HsType:
            return move.type

        @property
        def priority(self) -> int:
            return move.priority

        @property
        def prob(self) -> float:
            return move.prob

        @property
        def target(self) -> int:
            return move.target

        @property
        def recover(self) -> float:
            return move.recover

        @property
        def status(self) -> HsStatus:
            return move.status

        @property
        def stat(self) -> HsStat:
            return move.stat

        @property
        def stage(self) -> int:
            return move.stage

        @property
        def fixed_damage(self) -> float:
            return move.fixed_damage

        @property
        def weather(self) -> WeatherCondition:
            return move.weather

        @property
        def hazard(self) -> HsEntryHazard:
            return move.hazard

        def __eq__(self, other):
            if self.power != other.power:
                return False
            if self.acc != other.acc:
                return False
            if self.max_pp != other.max_pp:
                return False
            if self.type != other.type:
                return False
            if self.priority != other.priority:
                return False
            if self.prob > 0.:
                if self.prob != other.prob:
                    return False
                if self.target != self.target:
                    return False
                if self.recover != self.recover:
                    return False
                if self.status != self.status:
                    return False
                if self.stat != self.stat:
                    return False
                if self.stage != self.stage:
                    return False
                if self.fixed_damage != self.fixed_damage:
                    return False
                if self.weather != self.weather:
                    return False
                if self.hazard != self.hazard:
                    return False
            return True

        def __hash__(self):
            if self.prob == 0.:
                return hash((self.power, self.acc, self.max_pp, self.type, self.priority))
            return hash(
                (self.power, self.acc, self.max_pp, self.type, self.priority, self.prob, self.target, self.recover,
                 self.status, self.stat, self.stage, self.fixed_damage, self.weather, self.hazard))

    return MoveViewImpl()


null_hs_move = HsMove()


def get_partial_move_view(move: HsMove, move_hypothesis: Union[HsMove, None] = None) -> MoveView:
    if move.revealed:
        return get_move_view(move)
    elif move_hypothesis is not None:
        return get_move_view(move_hypothesis)
    return get_move_view(null_hs_move)


HsMoveRoster = Set[HsMove]


class MoveRosterView(ABC):

    @abstractmethod
    def get_move_view(self, idx: int) -> MoveView:
        pass

    @property
    @abstractmethod
    def n_moves(self) -> int:
        pass


def get_hs_move_roster_view(move_roster: HsMoveRoster) -> MoveRosterView:
    class MoveRosterViewImpl(MoveRosterView):

        def get_move_view(self, idx: int) -> MoveView:
            return get_move_view(list(move_roster)[idx])

        @property
        def n_moves(self) -> int:
            return len(move_roster)

        def __eq__(self, other):
            for i in range(len(move_roster)):
                m0, m1 = self.get_move_view(i), other.get_move_view(i)
                if m0 != m1:
                    return False
            return True

        def __hash__(self):
            return hash(move_roster)

    return MoveRosterViewImpl()


class Hs:

    def __init__(self, p_type: HsType = HsType.NORMAL, max_hp: float = MAX_HIT_POINTS,
                 status: HsStatus = HsStatus.NONE, move0: HsMove = HsMove(), move1: HsMove = HsMove(),
                 move2: HsMove = HsMove(), move3: HsMove = HsMove(), hs_id=-1):
        """
        In battle Pokemon base data struct.

        :param p_type: pokemon type
        :param max_hp: max hit points
        :param status: current status (PARALYZED, ASLEEP, etc.)
        :param move0: first move
        :param move1: second move
        :param move2: third move
        :param move3: fourth move
        """
        self.type: HsType = p_type
        self.max_hp: float = max_hp
        self.hp: float = max_hp
        self.status: HsStatus = status
        self.n_turns_asleep: int = 0
        self.moves: List[HsMove] = [move0, move1, move2, move3]
        for move in self.moves:
            move.set_owner(self)
        self.public = False
        self.hs_id = hs_id

    def __eq__(self, other):
        return self.type == other.type and isclose(self.max_hp, other.max_hp) and set(self.moves) == set(other.moves)

    def __hash__(self):
        return hash((self.type, self.max_hp) + tuple(self.moves))

    def __str__(self):
        s = 'Hs(Type=%s, HP=%d' % (self.type.name, self.hp)
        if self.status != HsStatus.NONE:
            s += ', Status=%s' % self.status.name
            if self.status == HsStatus.SLEEP:
                s += ', Turns Asleep=%d' % self.n_turns_asleep
        s += ', Moves={'
        for move in self.moves:
            s += str(move) + ', '
        return s + '})'

    def reset(self):
        """
        Reset Hs stats.
        """
        self.hp = self.max_hp
        self.status = HsStatus.NONE
        self.n_turns_asleep = 0
        for move in self.moves:
            move.reset()

    def fainted(self) -> bool:
        """
        Check if hs is fainted (hp == 0).

        :return: True if hs is fainted
        """
        return self.hp == 0

    def paralyzed(self) -> bool:
        """
        Check if hs is paralyzed this turn and cannot move.

        :return: true if hs is paralyzed and cannot move
        """
        return self.status == HsStatus.PARALYZED and np.random.uniform(0, 1) <= 0.25

    def asleep(self) -> bool:
        """
        Check if hs is asleep this turn and cannot move.

        :return: true if hs is asleep and cannot move
        """
        return self.status == HsStatus.SLEEP

    def frozen(self) -> bool:
        """
        Check if hs is frozen this turn and cannot move.

        :return: true if hs is frozen and cannot move
        """
        return self.status == HsStatus.FROZEN

    def reveal(self):
        self.public = True

    def hide_hs(self):
        self.public = False

    def hide(self):
        self.public = False
        for move in self.moves:
            move.hide()

    @property
    def revealed(self):
        return self.public


class HsView(ABC):

    @abstractmethod
    def get_move_view(self, idx: int) -> MoveView:
        pass

    @property
    @abstractmethod
    def type(self) -> HsType:
        pass

    @property
    @abstractmethod
    def hp(self) -> float:
        pass

    @property
    @abstractmethod
    def status(self) -> HsStatus:
        pass

    @property
    @abstractmethod
    def n_turns_asleep(self) -> int:
        pass


def get_hs_view(hs: Hs, hs_hypothesis: Union[Hs, None] = None, partial=False) -> HsView:
    class HsViewImpl(HsView):

        def get_move_view(self, idx: int) -> MoveView:
            if partial:
                # get opponent pokemon move information with an hypothesis
                if hs_hypothesis is not None and hs.moves[idx] is not None:
                    return get_partial_move_view(hs.moves[idx], hs_hypothesis.moves[idx])
                # get opponent pokemon move information
                return get_partial_move_view(hs.moves[idx])
            # get self pokemon move information
            return get_move_view(hs.moves[idx])

        @property
        def type(self) -> HsType:
            if hs_hypothesis is not None:
                return hs_hypothesis.type
            return hs.type

        @property
        def hp(self) -> float:
            if hs_hypothesis is not None:
                return hs_hypothesis.hp
            return hs.hp

        @property
        def status(self) -> HsStatus:
            return hs.status

        @property
        def n_turns_asleep(self) -> int:
            return hs.n_turns_asleep

    return HsViewImpl()


null_hs = Hs()


def get_partial_hs_view(hs: Hs, hs_hypothesis: Hs = None) -> HsView:
    if hs.revealed:
        return get_hs_view(hs, hs_hypothesis, partial=True)
    return get_hs_view(null_hs, hs_hypothesis)


class HsTemplate:

    def __init__(self, move_roster: HsMoveRoster, hs_type: HsType, max_hp: float, hs_id: int):
        """
        Pokemon specimen definition data structure.

        :param move_roster: set of available moves for Pokemon of this species
        :param hs_type: pokemon type
        :param max_hp: pokemon max_hp
        """
        self.move_roster: HsMoveRoster = move_roster
        self.type: HsType = hs_type
        self.max_hp = max_hp
        self.hs_id = hs_id

    def __eq__(self, other):
        return self.type == other.type and self.max_hp == other.max_hp and self.move_roster == other.move_roster

    def __hash__(self):
        return hash((self.type, self.max_hp) + tuple(self.move_roster))

    def __str__(self):
        s = 'HsTemplate(Type=%s, Max_HP=%d, Moves={' % (HsType(self.type).name, self.max_hp)
        for move in self.move_roster:
            s += str(move) + ', '
        return s + '})'

    def gen_hs(self, moves: List[int] = None) -> Hs:
        """
        Given the indexes of the moves generate a pokemon of this species.

        :param moves: index list of moves
        :return: the requested pokemon
        """
        move_list = list(self.move_roster)

        if moves is None:
            return Hs(p_type=self.type, max_hp=self.max_hp,
                       move0=move_list[0],
                       move1=move_list[1],
                       move2=move_list[2],
                       move3=move_list[3],
                       hs_id=self.hs_id)

        return Hs(p_type=self.type, max_hp=self.max_hp,
                   move0=move_list[moves[0]],
                   move1=move_list[moves[1]],
                   move2=move_list[moves[2]],
                   move3=move_list[moves[3]],
                   hs_id=self.hs_id)

    def is_speciman(self, hs: Hs) -> bool:
        """
        Check if input pokemon is a speciman of this species

        :param hs: pokemon
        :return: if pokemon is speciman of this template
        """
        return hs.type == self.type and hs.max_hp == self.max_hp and set(hs.moves).issubset(self.move_roster)

    def to_dict(self) -> Mapping[Text, JSON]:
        return {
            "type": self.type.name,
            "max_hp": self.max_hp,
            "moves": [m.to_dict() for m in self.move_roster],
            "hs_id": self.hs_id
        }


class HsTemplateView(ABC):

    @abstractmethod
    def get_move_roster_view(self) -> MoveRosterView:
        pass

    @property
    @abstractmethod
    def hs_type(self) -> HsType:
        pass

    @property
    @abstractmethod
    def max_hp(self) -> float:
        pass

    @property
    @abstractmethod
    def hs_id(self) -> int:
        pass


def get_hs_template_view(template: HsTemplate) -> HsTemplateView:
    class HsTemplateViewImpl(HsTemplateView):

        def get_move_roster_view(self) -> MoveRosterView:
            return get_hs_move_roster_view(template.move_roster)

        @property
        def hs_type(self) -> HsType:
            return template.type

        @property
        def max_hp(self) -> float:
            return template.max_hp

        @property
        def hs_id(self) -> int:
            return template.hs_id

        def __eq__(self, other):
            return self.hs_type == other.hs_type and self.max_hp == other.max_hp and self.get_move_roster_view() == \
                   other.get_move_roster_view()

        def __hash__(self):
            return hash((template.type, template.max_hp) + tuple(template.move_roster))

    return HsTemplateViewImpl()


HsRoster = Set[HsTemplate]


class HsRosterView(ABC):

    @abstractmethod
    def get_hs_template_view(self, idx: int) -> HsTemplateView:
        pass

    @property
    @abstractmethod
    def n_hss(self) -> int:
        pass


def get_hs_roster_view(hs_roster: HsRoster) -> HsRosterView:
    class HsRosterViewImpl(HsRosterView):

        def get_hs_template_view(self, idx: int) -> HsTemplateView:
            return get_hs_template_view(list(hs_roster)[idx])

        @property
        def n_hss(self) -> int:
            return len(hs_roster)

    return HsRosterViewImpl()


class HsTeam:

    def __init__(self, hss: List[Hs] = None):
        """
        In battle Hs team.

        :param hss: Chosen pokemon. The first stays the active pokemon.
        """
        if hss is None or hss == []:
            hss = [Hs(), Hs(), Hs()]
        self.active: Hs = hss.pop(0)
        self.active.reveal()
        self.party: List[Hs] = hss
        self.stage: List[int] = [0] * N_STATS
        self.confused: bool = False
        self.n_turns_confused: int = 0
        self.entry_hazard: List[int] = [0] * N_ENTRY_HAZARD

    def __eq__(self, other):
        eq = self.active == other.active and self.stage == other.stage and self.confused == other.confused and \
             self.n_turns_confused == other.n_turns_confused
        if not eq:
            return False
        for i, p in enumerate(self.party):
            if p != other.party[i]:
                return False
        for i, h in enumerate(self.entry_hazard):
            if h != other.entry_hazard[i]:
                return False
        return True

    def __str__(self):
        party = ''
        for i in range(0, len(self.party)):
            party += str(self.party[i]) + '\n'
        return 'Active:\n%s\nParty:\n%s' % (str(self.active), party)

    def reset(self):
        """
        Reset all hs status from team and active hs conditions.
        """
        self.active.reset()
        for hs in self.party:
            hs.reset()
        for i in range(len(self.stage)):
            self.stage[i] = 0
        self.confused = False
        self.n_turns_confused = 0
        for i in range(len(self.entry_hazard)):
            self.entry_hazard[i] = 0

    def reset_team_members(self, hss: List[Hs] = None):
        """
        Reset team members

        :param hss: list of hs members
        """
        if hss is None:
            hss = [Hs()]
        self.active = hss.pop(0)
        self.party = hss
        self.reset()

    def size(self) -> int:
        """
        Get team size.

        :return: Team size. Number of party hs plus 1
        """
        return len(self.party) + 1

    def fainted(self) -> bool:
        """
        Check if team is fainted

        :return: True if entire team is fainted
        """
        for i in range(len(self.party)):
            if not self.party[i].fainted():
                return False
        return self.active.fainted()

    def get_not_fainted(self) -> List[int]:
        """
        Check which pokemon are not fainted in party.

        :return: a list of positions of not fainted hs in party.
        """
        not_fainted = []
        for i, p in enumerate(self.party):
            if not p.fainted():
                not_fainted.append(i)
        return not_fainted

    def switch(self, pos: int) -> Tuple[Hs, Hs, int]:
        """
        Switch active hs with party hs on pos.
        Random party hs if s_pos = -1

        :param pos: to be switch pokemon party position
        :returns: new active hs, old active hs, pos
        """
        if len(self.party) == 0:
            return self.active, self.active, -1

        # identify fainted hs
        not_fainted_hs = self.get_not_fainted()
        all_party_fainted = not not_fainted_hs
        all_fainted = all_party_fainted and self.active.fainted()

        if not all_fainted:
            # select random party hs to switch if needed
            if not all_party_fainted:
                if pos == -1:
                    np.random.shuffle(not_fainted_hs)
                    pos = not_fainted_hs[0]

                # switch party and bench hs
                active = self.active
                self.active = self.party[pos]
                self.party[pos] = active

                # clear
                self.stage = [0] * N_STATS
                self.confused = False

                self.active.reveal()

        return self.active, self.party[pos], pos

    def get_hs_list(self):
        return [self.active] + self.party


class HsTeamView(ABC):

    @property
    @abstractmethod
    def active_hs_view(self) -> HsView:
        pass

    @abstractmethod
    def get_party_hs_view(self, idx: int) -> HsView:
        pass

    @abstractmethod
    def get_stage(self, stat: HsStat) -> int:
        pass

    @property
    @abstractmethod
    def confused(self) -> bool:
        pass

    @property
    @abstractmethod
    def n_turns_confused(self) -> int:
        pass

    @property
    @abstractmethod
    def party_size(self) -> int:
        pass

    @abstractmethod
    def get_entry_hazard(self, hazard: HsEntryHazard) -> int:
        pass


class HsTeamPrediction:

    def __init__(self, team_view: HsTeamView = None):
        self.team_view = team_view
        self.active: Union[Hs, None] = None
        self.party: List[Union[Hs, None]] = []


def get_team_view(team: HsTeam, team_prediction: HsTeamPrediction = None, partial: bool = False) -> HsTeamView:
    class HsTeamViewImpl(HsTeamView):

        @property
        def active_hs_view(self) -> HsView:
            if partial:
                if team_prediction is None:
                    # get partial information without any hypothesis
                    return get_partial_hs_view(team.active)
                # get partial information with  hypothesis
                return get_partial_hs_view(team.active, team_prediction.active)
            # get self active hs information
            return get_hs_view(team.active)

        def get_party_hs_view(self, idx: int) -> HsView:
            if partial:
                if team_prediction is None:
                    # get partial information without any hypothesis
                    return get_partial_hs_view(team.party[idx])
                # get partial information with a hypothesis
                return get_partial_hs_view(team.party[idx], team_prediction.party[idx])
            # get self party hs information
            return get_hs_view(team.party[idx])

        def get_stage(self, stat: HsStat) -> int:
            return team.stage[stat]

        @property
        def confused(self) -> bool:
            return team.confused

        @property
        def n_turns_confused(self) -> int:
            return team.n_turns_confused

        def get_entry_hazard(self, hazard: HsEntryHazard) -> int:
            return team.entry_hazard[hazard]

        @property
        def party_size(self) -> int:
            return team.size() - 1

    return HsTeamViewImpl()


class HsFullTeam:

    def __init__(self, hs_list: List[Hs] = None):
        if hs_list is None:
            hs_list = [deepcopy(null_hs) for _ in range(6)]
        self.hs_list = hs_list[:6]

    def __str__(self):
        team = ''
        for i in range(0, len(self.hs_list)):
            team += str(self.hs_list[i]) + '\n'
        return 'Team:\n%s' % team

    def get_battle_team(self, idx: List[int]) -> HsTeam:
        return HsTeam([self.hs_list[i] for i in idx])

    def reset(self):
        for hs in self.hs_list:
            hs.reset()

    def hide(self):
        for hs in self.hs_list:
            hs.hide()

    def hide_hss(self):
        for hs in self.hs_list:
            hs.hide_hs()

    def reveal(self):
        for hs in self.hs_list:
            hs.reveal()

    def get_copy(self):
        return HsFullTeam(self.hs_list)

    def __len__(self):
        return len(self.hs_list)

    def __getitem__(self, index):
        return self.hs_list[index]

class HsFullTeamView(ABC):

    @abstractmethod
    def get_hs_view(self, idx: int) -> HsView:
        pass

    @property
    @abstractmethod
    def n_hss(self) -> int:
        pass


def get_full_team_view(full_team: HsFullTeam, team_prediction: HsTeamPrediction = None,
                       partial: bool = False) -> HsFullTeamView:
    class HsFullTeamViewImpl(HsFullTeamView):

        def get_hs_view(self, idx: int) -> HsView:
            hs = full_team.hs_list[idx]
            if partial:
                if team_prediction is None:
                    # get partial information without any hypothesis
                    return get_partial_hs_view(hs)
                # get partial information with a hypothesis
                return get_partial_hs_view(hs, team_prediction.active)
            # get self active hs information
            return get_hs_view(hs)

        @property
        def n_hss(self) -> int:
            return len(full_team.hs_list)

    return HsFullTeamViewImpl()


class Weather:

    def __init__(self):
        self.condition: WeatherCondition = WeatherCondition.CLEAR
        self.n_turns_no_clear: int = 0


class GameState:

    def __init__(self, teams: List[HsTeam], weather: Weather):
        self.teams = teams
        self.weather = weather

    def __eq__(self, other):
        for i, team in enumerate(self.teams):
            if team != other.teams[i]:
                return False
        return self.weather.condition == other.weather.condition and self.weather.n_turns_no_clear == other.weather.n_turns_no_clear


class GameStateView(ABC):

    @abstractmethod
    def get_team_view(self, idx: int) -> HsTeamView:
        pass

    @property
    @abstractmethod
    def weather_condition(self) -> WeatherCondition:
        pass

    @property
    @abstractmethod
    def n_turns_no_clear(self) -> int:
        pass


def get_game_state_view(game_state: GameState, team_prediction: HsTeamPrediction = None) -> GameStateView:
    class GameStateViewImpl(GameStateView):

        def __init__(self):
            self._teams = [get_team_view(game_state.teams[0]),
                           get_team_view(game_state.teams[1], team_prediction, partial=True)]

        def get_team_view(self, idx: int) -> HsTeamView:
            return self._teams[idx]

        @property
        def weather_condition(self) -> WeatherCondition:
            return game_state.weather.condition

        @property
        def n_turns_no_clear(self) -> int:
            return game_state.weather.n_turns_no_clear

    return GameStateViewImpl()
