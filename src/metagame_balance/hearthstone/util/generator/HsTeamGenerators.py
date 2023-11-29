import random
from abc import ABC, abstractmethod
from typing import List

import numpy as np

from metagame_balance.hearthstone.datatypes.Constants import MAX_HIT_POINTS, MOVE_POWER_MAX, MOVE_POWER_MIN, BASE_HIT_POINTS, \
    DEFAULT_PKM_N_MOVES, MAX_TEAM_SIZE, DEFAULT_TEAM_SIZE, DEFAULT_N_MOVES_PKM
from metagame_balance.hearthstone.datatypes.Objects import Hs, HsMove, HsFullTeam, HsRoster, HsTemplate, HsTeam
from metagame_balance.hearthstone.datatypes.Types import HsType
from metagame_balance.hearthstone.util import softmax

LIST_OF_TYPES: List[HsType] = list(HsType)
DELTA_HIT_POINTS = MAX_HIT_POINTS - BASE_HIT_POINTS
DELTA_MOVE_POWER = MOVE_POWER_MAX - MOVE_POWER_MIN


class HsTeamGenerator(ABC):

    @abstractmethod
    def get_team(self) -> HsFullTeam:
        pass


# Example generators
class RandomTeamGenerator(HsTeamGenerator):

    def __init__(self, party_size: int = MAX_TEAM_SIZE - 1):
        self.party_size = party_size
        self.base_stats = np.array([120., 30., 30., 30., 30.])

    def get_team(self) -> HsFullTeam:
        team: List[Hs] = []
        for i in range(self.party_size + 1):
            evs = np.random.multinomial(10, softmax(np.random.normal(0, 1, 5)), size=None) * 36 + self.base_stats
            p_type: HsType = random.choice(LIST_OF_TYPES)
            max_hp: float = evs[0]
            moves: List[HsMove] = []
            for i in range(DEFAULT_PKM_N_MOVES):
                m_type: HsType = random.choice(LIST_OF_TYPES)
                m_power: float = evs[i + 1]
                moves.append(HsMove(m_power, move_type=m_type))
            moves[0].type = p_type
            # random.shuffle(moves)
            team.append(Hs(p_type, max_hp, move0=moves[0], move1=moves[1], move2=moves[2], move3=moves[3]))
        return HsFullTeam(team)


class RandomTeamFromRoster(HsTeamGenerator):

    def __init__(self, roster: HsRoster, team_size=DEFAULT_TEAM_SIZE, n_moves_hs=DEFAULT_N_MOVES_PKM):
        self.roster = list(roster)
        self.team_size = team_size
        self.n_moves_hs = n_moves_hs

    def get_team(self) -> HsFullTeam:
        hss = []
        templates: List[HsTemplate] = random.sample(self.roster, self.team_size)
        for template in templates:
            move_combination = random.sample(range(self.n_moves_hs), 4)
            hss.append(template.gen_hs(move_combination))
        return HsFullTeam(hss)


class RandomHsTeam(HsTeam):

    def __init__(self, team_gen: HsTeamGenerator, size=3):
        super().__init__()
        self.gen: HsTeamGenerator = team_gen
        self.reset()
        self.size = size

    def reset(self):
        self.reset_team_members(self.gen.get_team().hs_list)
