import copy
import itertools
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List

from math import exp

from metagame_balance.hearthstone.balance import DeltaRoster
from metagame_balance.hearthstone.balance.archtype import std_move_dist, std_hs_dist, std_team_dist
from metagame_balance.hearthstone.datatypes.Objects import HsTemplate, HsMove, HsFullTeam, HsRoster


class MetaData(ABC):

    @abstractmethod
    def update_with_team(self, team: HsFullTeam, won: bool):
        pass

    @abstractmethod
    def update_with_delta_roster(self, delta: DeltaRoster):
        pass

    @abstractmethod
    def evaluate(self) -> float:
        pass

    @abstractmethod
    def set_moves_and_hs(self, roster: HsRoster) -> None:
        pass

    @abstractmethod
    def update_metadata(self, **kwargs):
        """
        Update the meta data following an iteration of stage 2 optimization
        """
        pass

    @abstractmethod
    def clear_stats(self):
        pass

HsId = int

class StandardMetaData(MetaData):

    def __init__(self, _max_history_size: int = 1e5, unlimited: bool = False):
        # listings - moves, hs, teams
        self._moves: List[HsMove] = []
        self._hs: List[HsTemplate] = []
        # global usage rate - moves, hs
        self._move_usage: Dict[HsMove, int] = {}
        self._hs_usage: Dict[HsId, int] = {}
        # global win rate - moves, hs
        self._move_wins: Dict[HsMove, int] = {}
        self._hs_wins: Dict[HsId, int] = {}
        # similarity matrix - moves, hs
        self._d_move: Dict[Tuple[HsMove, HsMove], float] = {}
        self._d_hs: Dict[Tuple[HsId, HsId], float] = {}
        self._d_overall_team = 0.0
        # history buffer - moves, hs, teams
        self._move_history: List[HsMove] = []
        self._hs_history: List[HsId] = []
        self._teammates_history: Dict[Tuple[HsId, HsId], int] = {}
        self._team_history: List[Tuple[HsFullTeam, bool]] = []
        # total usage count - moves, hs, teams
        self._total_move_usage = 0
        self._total_hs_usage = 0
        # if meta history size
        self._max_move_history_size: int = _max_history_size * 12
        self._max_hs_history_size: int = _max_history_size * 3
        self._max_team_history_size: int = _max_history_size
        self._unlimited = unlimited


    def update_metadata(self, **kwargs):
        self.update_with_delta_roster(kwargs['delta'])

    def set_moves_and_hs(self, roster: HsRoster):
        self._hs = list(roster)
        self._moves = []
        for hs in self._hs:
            self._moves += list(hs.move_roster)
        for m0, m1 in itertools.product(self._moves, self._moves):
            self._d_move[(m0, m1)] = std_move_dist(m0, m1)
        self.clear_stats()

    def clear_stats(self):
        for hs in self._hs:
            self._hs_usage[hs.hs_id] = 0
            self._hs_wins[hs.hs_id] = 0
        for move in self._moves:
            self._move_usage[move] = 0
            self._move_wins[move] = 0
        for m0, m1 in itertools.product(self._moves, self._moves):
            self._d_move[(m0, m1)] = 0 #std_move_dist(m0, m1)
        for p0, p1 in itertools.product(self._hs, self._hs):
            self._d_hs[(p0.hs_id, p1.hs_id)] = std_hs_dist(p0, p1, move_distance=lambda x, y: self._d_move[x, y])
        self._move_history = []
        self._hs_history = []
        self._teammates_history = {}
        self._team_history = []
        self._d_overall_team = 0.0
        # total usage count - moves, hs, teams
        self._total_move_usage = 0
        self._total_hs_usage = 0

    def update_with_delta_roster(self, delta: DeltaRoster):

        d_move_copy = copy.deepcopy(self._d_move)
        for idx in delta.dp.keys():
            for m_idx in delta.dp[idx].dpm.keys():
                for move_pair in self._d_move.keys():
                    if self._moves[idx * 4 + m_idx] in move_pair:
                        d_move_copy[(move_pair[0], move_pair[1])] = std_move_dist(move_pair[0], move_pair[1])
            for hs_pair in self._d_hs.keys():
                if self._hs[idx].hs_id in hs_pair:
                    self._d_hs[(hs_pair[0], hs_pair[1])] = std_hs_dist(self._hs[hs_pair[0]],
                                                                           self._hs[hs_pair[1]])
        self._d_move = d_move_copy

    def update_with_team(self, team: HsFullTeam, won: bool):
        self._team_history.append((team.get_copy(), won))
        # update distance
        for _team in self._team_history:
            self._d_overall_team = std_team_dist(team, _team[0],
                                                 pokemon_distance=lambda x, y: self._d_hs[x.hs_id, y.hs_id])
        # update usages
        for hs in team.hs_list:
            self._hs_usage[hs.hs_id] += 1
            if won:
                self._hs_wins[hs.hs_id] += 1
            for move in hs.moves:
                self._move_usage[move] += 1
                if won:
                    self._move_wins[move] += 1
        for hs0, hs1 in itertools.product(team.hs_list, team.hs_list):
            if hs0 != hs1:
                pair = (hs0.hs_id, hs1.hs_id)
                if pair not in self._teammates_history.keys():
                    self._teammates_history[pair] = 1
                else:
                    self._teammates_history[pair] += 1
        # update total usages
        self._total_hs_usage += 3
        self._total_move_usage += 12
        # remove from history past defined maximum length
        if len(self._team_history) > self._max_team_history_size and not self._unlimited:
            team, won = self._team_history.pop(0)
            if won:
                for hs in team.hs_list:
                    self._hs_wins[hs.hs_id] -= 1
                    for move in hs.moves:
                        self._move_wins[move] -= 1
            for hs0, hs1 in itertools.product(team.hs_list, team.hs_list):
                if hs0 != hs1:
                    self._teammates_history[(hs0.hs_id, hs1.hs_id)] -= 1
            for _team in self._team_history:
                self._d_overall_team -= std_team_dist(team, _team[0], pokemon_distance=lambda x, y: self._d_hs[x, y])
        if len(self._hs_history) > self._max_hs_history_size and not self._unlimited:
            for _ in range(3):
                old_hs = self._hs_history.pop(0)
                self._hs_usage[old_hs] -= 1
            self._total_hs_usage -= 3
        if len(self._move_history) > self._max_move_history_size and not self._unlimited:
            for _ in range(12):
                old_move = self._move_history.pop(0)
                self._move_usage[old_move] -= 1
            self._total_move_usage -= 12

    def get_global_hs_usage(self, hs_id: HsId) -> float:
        return self._hs_usage[hs_id] / self._total_hs_usage

    def get_global_hs_winrate(self, hs_id: HsId) -> float:
        return self._hs_wins[hs_id] / self._hs_usage[hs_id]

    def get_global_move_usage(self, move: HsMove) -> float:
        return self._move_usage[move] / self._total_move_usage

    def get_global_move_winrate(self, move: HsMove) -> float:
        return self._move_wins[move] / self._move_usage[move]

    def get_pair_usage(self, pair: Tuple[HsId, HsId]) -> float:
        if pair not in self._teammates_history.keys():
            return 0.0
        return self._teammates_history[pair] / self._hs_usage[pair[0]]

    def get_team(self, t) -> Tuple[HsFullTeam, bool]:
        return self._team_history[t][0], self._team_history[t][1]

    def get_n_teams(self) -> int:
        return len(self._team_history)

    def evaluate(self) -> float:
        d = [0., 0., 0., 0., 0.]
        # Overall number of different Hs (templates).
        for hs0, hs1 in itertools.product(self._hs, self._hs):
            d[0] += - self._hs_usage[hs1.hs_id] * exp(-self._d_hs[(hs0.hs_id, hs1.hs_id)]) + 1
        d[0] /= 2
        # Overall number of different Hs moves.
        for move0, move1 in itertools.product(self._moves, self._moves):
            d[1] += - self._move_usage[move1] * exp(-self._d_move[(move0, move1)]) + 1
        d[1] /= 2
        # Overall number of different Hs teams.
        d[2] = self._d_overall_team
        for team, win in self._team_history:
            # Difference over moves on same Hs.
            moves = []
            for hs in team.hs_list:
                moves.extend(hs.moves)
            for move0, move1 in itertools.product(moves, moves):
                d[3] += - exp(-self._d_move[(move0, move1)]) + 1
            # Difference over Hs on same team.
            for hs0, hs1 in itertools.product(team.hs_list, team.hs_list):
                d[4] += - exp(-self._d_hs[(hs0.hs_id, hs1.hs_id)]) + 1
        d[3] /= 2
        d[4] /= 2
        return sum(d)
