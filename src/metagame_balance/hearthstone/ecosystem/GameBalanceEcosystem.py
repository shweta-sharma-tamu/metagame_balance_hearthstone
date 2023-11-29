from copy import deepcopy
from typing import List

from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.balance.restriction import HSDesignConstraints
from metagame_balance.hearthstone.competition import CompetitorManager
from metagame_balance.hearthstone.competition import Competitor
from metagame_balance.hearthstone.datatypes.Constants import DEFAULT_MATCH_N_BATTLES
from metagame_balance.hearthstone.datatypes.Objects import HsRoster
from metagame_balance.hearthstone.ecosystem.BattleEcosystem import Strategy
from metagame_balance.hearthstone.ecosystem.ChampionshipEcosystem import ChampionshipEcosystem


class GameBalanceEcosystem:

    def __init__(self, competitor: Competitor, surrogate_agent: List[CompetitorManager],
                 constraints: HSDesignConstraints, base_roster: HsRoster, meta_data: MetaData, debug=False,
                 render=False, n_battles=DEFAULT_MATCH_N_BATTLES, strategy: Strategy = Strategy.RANDOM_PAIRING):
        self.c = competitor
        self.constraints = constraints
        self.meta_data = meta_data
        self.rewards = []
        self.hs: ChampionshipEcosystem = ChampionshipEcosystem(base_roster, meta_data, debug, render, n_battles,
                                                                strategy=strategy)
        for c in surrogate_agent:
            self.hs.register(c)

    def run(self, n_epochs, n_hs_epochs: int, n_league_epochs: int) -> List:
        epoch = 0
        while epoch < n_epochs:
            self.meta_data.clear_stats()  #consider doing it inside the league as well! or
            self.hs.run(n_hs_epochs, n_league_epochs)
            """
            Hacky way to get the policy. TODO Structure it
            Probably have a function in league to return the agent and advserial agent
            """
            agent = list(filter(lambda agent: agent.competitor.name == "agent", self.hs.league.competitors))[0]

            self.meta_data.update_metadata(policy=agent.competitor.team_build_policy)

            self.rewards += [self.meta_data.evaluate()]
            delta_roster = self.c.balance_policy.get_action((self.hs.roster, self.meta_data,
                                                             self.constraints))
            copy_roster = deepcopy(self.hs.roster)
            delta_roster.apply(copy_roster)
            violated_rules = self.constraints.check_every_rule(copy_roster)
            if len(violated_rules) == 0:
                delta_roster.apply(self.hs.roster)
                self.meta_data.update_metadata(delta=delta_roster)
            else:
                raise AssertionError
            print('-' * 30 + "HS EPOCH " + str(epoch) + " DONE" + '-' * 30)
            for hs in self.hs.roster:
                print(hs)
                for move in hs.move_roster:
                    print(move.power, move.acc, move.max_pp)
            epoch += 1
