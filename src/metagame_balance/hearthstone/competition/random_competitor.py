from typing import Tuple, Optional, List
import random

from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.behaviour import TeamSelectionPolicy, BattlePolicy, TeamBuildPolicy
from metagame_balance.hearthstone.behaviour.BattlePolicies import BetterRandomBattlePolicy
from metagame_balance.hearthstone.behaviour.TeamSelectionPolicies import RandomTeamSelectionPolicy
from metagame_balance.hearthstone.competition.Competitor import Competitor
from metagame_balance.hearthstone.datatypes.Objects import HsFullTeam, HsRosterView, HsRoster, Hs


class FixedSizeRandomTeamBuildPolicy(TeamBuildPolicy):
    """
    Picks a random team from the full roster.
    """
    def __init__(self, team_size: int):
        super(FixedSizeRandomTeamBuildPolicy, self).__init__()
        self.team_size = team_size

    def get_action(self, s: Tuple[MetaData, Optional[HsFullTeam], HsRoster]) -> HsFullTeam:
        roster = s[2]
        selected = random.sample(list(roster), self.team_size)
        team: List[Hs] = [s.gen_hs() for s in selected]
        return HsFullTeam(team)

    def close(self):
        pass


class RandomTeamSelectionCompetitor(Competitor):
    def __init__(self, team_size: int):
        self.team_size = team_size
        self._team_build_policy = FixedSizeRandomTeamBuildPolicy(team_size)
        self._team_selection_policy = RandomTeamSelectionPolicy(teams_size=team_size, selection_size=team_size)
        self._battle_policy = BetterRandomBattlePolicy()

    @property
    def team_build_policy(self) -> TeamBuildPolicy:
        return self._team_build_policy

    @property
    def team_selection_policy(self) -> TeamSelectionPolicy:
        return self._team_selection_policy

    @property
    def name(self):
        return "RandomTeamSelectionCompetitor"

    @property
    def battle_policy(self) -> BattlePolicy:
        return self._battle_policy
