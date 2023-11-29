from abc import ABC, abstractmethod
from typing import Any, Set, Union, List, Tuple

from metagame_balance.hearthstone.balance import DeltaRoster
from metagame_balance.hearthstone.balance.meta import MetaData
from metagame_balance.hearthstone.balance.restriction import HSDesignConstraints
from metagame_balance.hearthstone.datatypes.Objects import HsTeamPrediction, HsFullTeam, GameStateView, HsFullTeamView, HsRosterView, \
    HsTemplate


class Behaviour(ABC):

    @abstractmethod
    def get_action(self, s) -> Any:
        pass

    def requires_encode(self) -> bool:
        return False

    @abstractmethod
    def close(self):
        pass


class BattlePolicy(Behaviour):

    @abstractmethod
    def get_action(self, s: Union[List[float], GameStateView]) -> int:
        pass


class TeamSelectionPolicy(Behaviour):

    @abstractmethod
    def get_action(self, s: Tuple[HsFullTeamView, HsFullTeamView]) -> Set[int]:
        pass


class TeamBuildPolicy(Behaviour):

    @abstractmethod
    def get_action(self, s: Tuple[MetaData, HsFullTeam, HsRosterView]) -> HsFullTeam:
        pass


class TeamPredictor(Behaviour):

    @abstractmethod
    def get_action(self, s: Tuple[HsFullTeamView, MetaData]) -> HsTeamPrediction:
        pass


class BalancePolicy(Behaviour):

    @abstractmethod
    def get_action(self, s: Tuple[Set[HsTemplate], MetaData, HSDesignConstraints]) -> DeltaRoster:
        pass
