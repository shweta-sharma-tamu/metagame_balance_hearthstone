from copy import deepcopy
from typing import Dict, List

import numpy as np

from metagame_balance.entropy_fns import true_entropy
from metagame_balance.hearthstone.balance import DeltaRoster
from metagame_balance.hearthstone.balance.meta import MetaData, HsId
from metagame_balance.hearthstone.datatypes.Constants import get_state_size
from metagame_balance.hearthstone.datatypes.Objects import HsTemplate, HsMove, HsFullTeam, HsRoster
from metagame_balance.hearthstone.team import HSTeam, predict
from metagame_balance.hearthstone.util.RosterParsers import MetaRosterStateParser


class PolicyEntropyMetaData(MetaData):

    def __init__(self, team_size: int):
        # listings - moves, hs, teams
        self.init_state = None
        self.parser = None
        self._moves: List[HsMove] = []
        self._hs: List[HsTemplate] = []

        self._hs_wins: Dict[HsId, int] = {}
        self.current_policy = None # I don't see another way to do, rather than taking input as P(A_j) as input in evaluate

        self.reg_weights = np.zeros(())
        self.update_params = ['policy', 'delta']
        self.team_size = team_size
        self.state_dim = get_state_size(team_size)

    def set_mask_weights(self, w):
        """
        Consider adding utility functions that go like
        ``mask hs idx, move idx etc.
        """
        self.reg_weights = w

    def set_moves_and_hs(self, roster: HsRoster):
        self._hs = list(roster)
        self._moves = []
        for hs in self._hs:
            self._moves += list(hs.move_roster)

        init_metadata = deepcopy(self)
        self.parser = MetaRosterStateParser(len(self._hs))
        self.init_state = self.parser.metadata_to_state(init_metadata)
        self.init_reg_weights(self.parser.length_state_vector())

    def init_reg_weights(self, size):

        self.set_mask_weights(np.zeros(size))

    def clear_stats(self) -> None:
        for hs in self._hs:
            self._hs_wins[hs.hs_id] = 0

    def update_with_delta_roster(self, delta: DeltaRoster):
        return

    def update_metadata(self, **kwargs):
        assert(sum([k not in self.update_params for k in kwargs.keys()]) == 0)
        if 'delta' in kwargs.keys():
            self.update_with_delta_roster(kwargs['delta'])

        if 'policy' in kwargs.keys():
            self.update_with_policy(kwargs['policy'])
        #stage 2 policy
        #delta roster

    def update_with_policy(self, policy):

        self.current_policy = policy

    def update_with_team(self, team: HsFullTeam, won: bool):

        for hs in team.hs_list:
            if won:
                self._hs_wins[hs.hs_id] += 1
        """
        update the meta with team if required in future
        """

    def distance_from_init_meta(self):
        """
        Returns L2 distance from inital meta scaled with reg weights
        """
        state = self.parser.metadata_to_state(self)

        return ((self.reg_weights * (state - self.init_state)) ** 2).mean(axis=0) / 100 ##something reasonable

    def to_dict(self) -> dict:
        return {
            "hearthstone": [p.to_dict() for p in self._hs]
        }

    def entropy(self) -> float:
        u = self.current_policy.get_u_fn()
        return true_entropy(HSTeam, predict(u, self._hs, self.state_dim, self.team_size),
                            len(self._hs), self.team_size)

    def evaluate(self) -> float:
        # A: set of all hearthstone statistics
        # does this actually need the whole policy
        # needs the winrate
        # won't sample from the policy
        # we would have to do importance sampling over the historical trajectories

        #TODO: write a function here, so that I don't have to create numpy arrays in object
        entropy_loss = self.entropy()

        return entropy_loss + self.distance_from_init_meta()
