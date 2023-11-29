from metagame_balance.hearthstone.behaviour import BattlePolicy
from metagame_balance.hearthstone.behaviour.BalancePolicies import BalancePolicy
from metagame_balance.policies.CMAESBalancePolicy import CMAESBalancePolicy
from metagame_balance.hearthstone.competition.Competitor import Competitor


class ProposedCompetitor(Competitor):
    def __init__(self, num_hs, name: str = "Policy"):
        self._name = name
        self.num_hs = num_hs
        self._balance_policy = CMAESBalancePolicy(num_hs)

    @property
    def name(self):
        return self._name

    @property
    def battle_policy(self) -> BattlePolicy:
        return self._battle_policy

    @property
    def balance_policy(self) -> BalancePolicy:
        return self._balance_policy
