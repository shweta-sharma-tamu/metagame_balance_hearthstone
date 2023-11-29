from typing import List, Tuple, Optional

from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.behaviour import TeamBuildPolicy
from metagame_balance.hearthstone.datatypes.Constants import DEFAULT_TEAM_SIZE
from metagame_balance.hearthstone.datatypes.Objects import Hs, HsRoster, HsFullTeam


class RandomTeamBuildPolicy(TeamBuildPolicy):

    def close(self):
        pass

    def get_action(self, d: Tuple[MetaData, Optional[HsFullTeam], HsRoster]) -> HsFullTeam:
        roster = d[2]
        """
        Removed views (access the roster's directly!)
        """
        import random
        pre_selection = random.sample(list(roster), DEFAULT_TEAM_SIZE)
        team: List[Hs] = []
        for pt in pre_selection:
            team.append(pt.gen_hs())
        return HsFullTeam(team)
