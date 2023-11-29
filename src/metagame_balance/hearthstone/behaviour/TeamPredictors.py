from typing import Tuple

from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.behaviour import TeamPredictor
from metagame_balance.hearthstone.datatypes.Objects import HsTeamPrediction, HsTeamView


class NullTeamPredictor(TeamPredictor):
    null_team_prediction = HsTeamPrediction()

    def close(self):
        pass

    def get_action(self, d: Tuple[HsTeamView, MetaData]) -> HsTeamPrediction:
        return NullTeamPredictor.null_team_prediction
