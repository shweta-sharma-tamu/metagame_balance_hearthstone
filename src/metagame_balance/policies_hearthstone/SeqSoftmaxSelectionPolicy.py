from typing import List, Tuple, Optional
from scipy.special import softmax
import numpy as np

from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.behaviour import TeamBuildPolicy
from metagame_balance.hearthstone.datatypes.Constants import NUM_TYPES, get_state_size
from metagame_balance.hearthstone.datatypes.Objects import HsFullTeam, HsRoster, Hs, HsTemplate
from metagame_balance.hearthstone.datatypes.Constants import STATS_OPT_2_PER_MOVE
from metagame_balance.utility import UtilityFunctionManager


class SeqSoftmaxSelectionPolicy(TeamBuildPolicy):
    """
    Ignore S_g as of now
    """

    def __init__(self, utility_manager: UtilityFunctionManager, get_u_fn, update_policy: bool, team_size: int,
                 update_after: int):
        self.team_size = team_size
        self.get_u_fn = get_u_fn  ### This should be function pointer
        self.utility_manager = utility_manager
        self._updatable = update_policy
        self.update_after = update_after  #### perform an update after completion of certain number of episode, hacks for on-policy learning
        self.buffer = {'x': [],
                       'y': []}  # NOT replay buffer, just because neural networks don't work well with small batch sizes
        self.greedy = False

    def set_greedy(self, greedy: bool):
        self.greedy = greedy

    def get_action(self, d: Tuple[MetaData, Optional[HsFullTeam], HsRoster]) -> HsFullTeam:
        team: List[Hs] = []
        team_idxs: List[int] = []
        roster = list(d[2])
        size = self._size_state_vector()
        base_team_state = np.zeros(size)
        u = self.get_u_fn()
        for i in range(self.team_size):

            S = np.repeat(base_team_state.reshape(1, -1), len(roster), axis=0)
            for j, hs in enumerate(roster):
                s = self._mark(S[j, :], team, hs)
                S[j, :] = s
            utilities = u.predict(S)

            # avoid selecting the same team
            for idx in team_idxs:
                utilities[idx] = -float("inf")

            if self.greedy:
                selection_idx = np.argmax(utilities)
            else:
                selection_idx = np.random.choice(range(len(roster)), p=softmax(utilities))
            selected_hs = roster[selection_idx]

            # mark before you append
            team_idxs.append(selection_idx)
            self._mark(base_team_state, team, selected_hs)
            team.append(selected_hs.gen_hs())
        return HsFullTeam(team)

    def _size_state_vector(self):
        return get_state_size(self.team_size)

    def _mark(self, state: np.ndarray, team: list, hs) -> np.ndarray:
        """
        Function marks team and the new one vector
        TODO: make this static
        """
        """
        maybe use parser?
        """

        def get_moves(hs):
            if isinstance(hs, HsTemplate):
                return hs.move_roster
            elif isinstance(hs, Hs):
                return hs.moves
            else:
                raise Exception("Unrecognized hs object type: " + str(hs))

        def type_to_idx(type_):
            return int(type_)

        idx_to_move_stat_map = {0: lambda hs: hs.power, 1: lambda hs: hs.acc, 2: lambda hs: hs.max_pp}
        stats_per_hs = self._size_state_vector() // self.team_size
        base_idx = len(team) * stats_per_hs
        state[base_idx] = hs.max_hp
        state[base_idx + 1 + type_to_idx(hs.type)] = 1
        base_idx += 1 + NUM_TYPES

        for i, move in enumerate(get_moves(hs)):
            for j in range(len(idx_to_move_stat_map)):
                move_idx = i * STATS_OPT_2_PER_MOVE + j
                state[base_idx + move_idx] = idx_to_move_stat_map[j](move)
            state[base_idx + move_idx + type_to_idx(move.type) + 1] = 1
            # print(hs.max_hp, hs.type, move.power, move.acc, move.max_pp, move.type, int(move.type))
        return state

    def update(self, team: HsFullTeam,
               reward: float) -> None:  # do we want to use metadata to get reward? do we assume meta data doesn't change across iterations?
        def team_to_state(team: HsFullTeam):
            state = np.zeros((self._size_state_vector()))
            for i, hs in enumerate(team):
                self._mark(state, team[:i], hs)
            return state

        def team_to_states(team: HsFullTeam):

            states = []
            for i in range(len(team)):
                states.append(team_to_state(team[i:]))
            return states

        if self._updatable is False:
            return
        states = team_to_states(team)
        get_target_wrapper = lambda s: self._get_target(s, reward)
        targets = map(get_target_wrapper, states)
        self.buffer['x'] += states
        self.buffer['y'] += targets
        if len(self.buffer['x']) > self.update_after:
            u = self.get_u_fn()
            u.run_epoch(np.array(self.buffer['x']), np.array(self.buffer['y']), verbose=0)
            self.buffer = {'x': [], 'y': []}
        return

    def _get_target(self, state, reward) -> float:
        """
        couuld be either just reward
        or alpha * self.u.predict(state) + (1 - alpha) reward
        """
        return reward

    def close(self) -> None:
        """
        considering dumping the recent neural network to a file here
        """
        return
