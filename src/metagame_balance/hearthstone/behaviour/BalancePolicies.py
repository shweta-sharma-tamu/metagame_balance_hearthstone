from typing import Tuple

from metagame_balance.hearthstone.balance import DeltaRoster
from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.balance.restriction import DesignConstraints
from metagame_balance.hearthstone.behaviour import BalancePolicy
from metagame_balance.hearthstone.datatypes.Objects import HsRoster


class IdleBalancePolicy(BalancePolicy):

    def __init__(self):
        self.dr = DeltaRoster({})

    def close(self):
        pass

    def get_action(self, d: Tuple[HsRoster, MetaData, DesignConstraints]) -> DeltaRoster:
        return self.dr
