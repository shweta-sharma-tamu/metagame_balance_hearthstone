from typing import Dict

from metagame_balance.hearthstone.datatypes.Objects import HsRoster, HsMove, HsTemplate
from metagame_balance.hearthstone.datatypes.Types import HsType


class DeltaHs:

    def __init__(self, max_hp: float, hs_type: HsType, dpm: Dict[int, HsMove]):
        self.max_hp = max_hp
        self.type = hs_type
        self.dpm = dpm

    def apply(self, hs: HsTemplate):
        hs.max_hp = self.max_hp
        hs.type = self.type
        for idx, move in enumerate(hs.move_roster):
            if idx in self.dpm.keys():
                dpm = self.dpm[idx]
                move.__dict__.update(dpm.__dict__)


class DeltaRoster:

    def __init__(self, dp: Dict[int, DeltaHs]):
        self.dp = dp

    def apply(self, roster: HsRoster):
        for hs in roster:
            if hs.hs_id in self.dp.keys():
                self.dp[hs.hs_id].apply(hs)
