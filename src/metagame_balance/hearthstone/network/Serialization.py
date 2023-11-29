from metagame_balance.hearthstone.datatypes.Objects import GameStateView, HsTeamView, HsView, MoveView, HsRosterView, HsTemplateView, \
    MoveRosterView, HsFullTeamView
from metagame_balance.hearthstone.datatypes.Types import WeatherCondition, HsEntryHazard, HsStat, N_ENTRY_HAZARD, N_STATS, HsStatus, \
    HsType


class SerializedMove(MoveView):

    def __init__(self, mv: MoveView):
        self._power = mv.power
        self._acc = mv.acc
        self._pp = mv.pp
        self._max_pp = mv.max_pp
        self._type = mv.type
        self._priority = mv.priority
        self._prob = mv.prob
        self._target = mv.target
        self._recover = mv.recover
        self._status = mv.status
        self._stat = mv.stat
        self._stage = mv.stage
        self._stage = mv.stage
        self._fixed_damage = mv.fixed_damage
        self._weather = mv.weather
        self._hazard = mv.hazard

    @property
    def power(self) -> float:
        return self._power

    @property
    def acc(self) -> float:
        return self._acc

    @property
    def pp(self) -> int:
        return self._pp

    @property
    def max_pp(self) -> int:
        return self._max_pp

    @property
    def type(self) -> HsType:
        return self._type

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def prob(self) -> float:
        return self._prob

    @property
    def target(self) -> int:
        return self._target

    @property
    def recover(self) -> float:
        return self._recover

    @property
    def status(self) -> HsStatus:
        return self._status

    @property
    def stat(self) -> HsStat:
        return self._stat

    @property
    def stage(self) -> int:
        return self._stage

    @property
    def fixed_damage(self) -> float:
        return self._fixed_damage

    @property
    def weather(self) -> WeatherCondition:
        return self._weather

    @property
    def hazard(self) -> HsEntryHazard:
        return self._hazard


class SerializedHs(HsView):

    def __init__(self, pv: HsView):
        self._move_view = [SerializedMove(pv.get_move_view(i)) for i in range(4)]
        self._type = pv.type
        self._hp = pv.hp
        self._status = pv.status
        self._n_turns_asleep = pv.n_turns_asleep

    def get_move_view(self, idx: int) -> MoveView:
        return self._move_view[idx]

    @property
    def type(self) -> HsType:
        return self._type

    @property
    def hp(self) -> float:
        return self._hp

    @property
    def status(self) -> HsStatus:
        return self._status

    @property
    def n_turns_asleep(self) -> int:
        return self._n_turns_asleep


class SerializedHsTeam(HsTeamView):

    def __init__(self, ptv: HsTeamView):
        self._active_hs_view = SerializedHs(ptv.active_hs_view)
        self._party_hs_view = [SerializedHs(ptv.get_party_hs_view(0)), SerializedHs(ptv.get_party_hs_view(1))]
        self._stage = [0] * N_STATS
        self._stage[HsStat.ATTACK] = ptv.get_stage(HsStat.ATTACK)
        self._stage[HsStat.DEFENSE] = ptv.get_stage(HsStat.DEFENSE)
        self._stage[HsStat.SPEED] = ptv.get_stage(HsStat.SPEED)
        self._confused = ptv.confused
        self._n_turns_confused = ptv.n_turns_confused
        self._entry_hazard = [0] * N_ENTRY_HAZARD
        self._entry_hazard[HsEntryHazard.SPIKES] = ptv.get_entry_hazard(HsEntryHazard.SPIKES)

    @property
    def active_hs_view(self) -> HsView:
        return self._active_hs_view

    def get_party_hs_view(self, idx: int) -> HsView:
        return self._party_hs_view[idx]

    def get_stage(self, stat: HsStat) -> int:
        return self._stage[stat]

    @property
    def confused(self) -> bool:
        return self._confused

    @property
    def n_turns_confused(self) -> int:
        return self._n_turns_confused

    def get_entry_hazard(self, hazard: HsEntryHazard) -> int:
        return self._entry_hazard[hazard]


class SerializedGameState(GameStateView):

    def __init__(self, gsv: GameStateView):
        self._team_views = [SerializedHsTeam(gsv.get_team_view(0)), SerializedHsTeam(gsv.get_team_view(1))]
        self._weather_condition = gsv.weather_condition
        self._n_turns_no_clear = gsv.n_turns_no_clear

    def get_team_view(self, idx: int) -> HsTeamView:
        return self._team_views[idx]

    @property
    def weather_condition(self) -> WeatherCondition:
        return self._weather_condition

    @property
    def n_turns_no_clear(self) -> int:
        return self._n_turns_no_clear


class SerializedMoveRoster(MoveRosterView):

    def __init__(self, mrv: MoveRosterView):
        self._move_view = [SerializedMove(mrv.get_move_view(i)) for i in range(mrv.n_moves)]
        self._n_moves = mrv.n_moves

    def get_move_view(self, idx: int) -> MoveView:
        return self._move_view[idx]

    @property
    def n_moves(self) -> int:
        return self._n_moves


class SerializedHsTemplate(HsTemplateView):

    def __init__(self, ptv: HsTemplateView):
        self._move_roster_view = SerializedMoveRoster(ptv.get_move_roster_view())
        self._hs_type = ptv.hs_type
        self._max_hp = ptv.max_hp
        self._hs_id = ptv.hs_id

    def get_move_roster_view(self) -> MoveRosterView:
        return self._move_roster_view

    @property
    def hs_type(self) -> HsType:
        return self._hs_type

    @property
    def max_hp(self) -> float:
        return self._max_hp

    @property
    def hs_id(self) -> int:
        return self._hs_id


class SerializedHsRoster(HsRosterView):

    def __init__(self, prv: HsRosterView):
        self._hs_template_view = [SerializedHsTemplate(prv.get_hs_template_view(i)) for i in range(prv.n_hss)]
        self._n_hss = prv.n_hss

    def get_hs_template_view(self, idx: int) -> HsTemplateView:
        return self._hs_template_view[idx]

    @property
    def n_hss(self) -> int:
        return self._n_hss


class SerializedHsFullTeam(HsFullTeamView):

    def __init__(self, pftv: HsFullTeamView):
        self._hs_view = [SerializedHs(pftv.get_hs_view(i)) for i in range(pftv.n_hss)]
        self._n_hss = pftv.n_hss

    def get_hs_view(self, idx: int) -> HsView:
        return self._hs_view[idx]

    @property
    def n_hss(self) -> int:
        return self._n_hss
