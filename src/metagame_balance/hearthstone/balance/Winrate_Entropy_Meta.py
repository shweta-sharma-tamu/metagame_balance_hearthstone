import copy
from typing import Dict, List

from scipy.stats import entropy

from metagame_balance.hearthstone.balance import DeltaRoster
from metagame_balance.hearthstone.balance.meta import MetaData, HsId
from metagame_balance.hearthstone.datatypes.Objects import HsTemplate, HsMove, HsFullTeam, HsRoster
from metagame_balance.hearthstone.util.RosterParsers import MetaRosterStateParser


class WinrateEntropyMetaData(MetaData):

    def __init__(self):
        # listings - moves, hs, teams
        self._moves: List[HsMove] = []
        self._hs: List[HsTemplate] = []

        self._hs_wins: Dict[HsId, int] = {}

    def set_moves_and_hs(self, roster: HsRoster):
        self._hs = list(roster)
        self._moves = []
        for hs in self._hs:
            self._moves += list(hs.move_roster)

        init_metadata = copy.deepcopy(self)
        self.parser = MetaRosterStateParser(len(self._hs))
        self.init_state = self.parser.metadata_to_state(init_metadata)


    def clear_stats(self):
        for hs in self._hs:
            self._hs_wins[hs.hs_id] = 0

    def update_with_delta_roster(self, delta: DeltaRoster):
        return

    def update_metadata(self, **kwargs):

        self.update_with_delta_roster(kwargs['delta'])
        #stage 2 policy
        #delta roster

    def update_with_policy(self, policy):
        raise NotImplementedError

    def update_with_team(self, team: HsFullTeam, won: bool):

        for hs in team.hs_list:
            if won:
                self._hs_wins[hs.hs_id] += 1
        """
        update the meta with team if required in future
        """

    def distance_from_init_meta(self):

        state = self.parser.metadata_to_state(self)

        return ((state - self.init_state) ** 2).mean(axis=0) / 100 ##something reasonable


    def evaluate(self, distance_loss = False) -> float:
        loss = -entropy([x / sum(self._hs_wins.values())  for x in self._hs_wins.values()])
        if distance_loss:
            return loss + self.distance_from_init_meta()
        return loss
