from typing import List, Union

from metagame_balance.hearthstone.datatypes.Constants import MAX_HIT_POINTS, MOVE_MAX_PP, DEFAULT_TEAM_SIZE
from metagame_balance.hearthstone.datatypes.Objects import HsMove, Hs, HsTeam, GameState, null_hs_move, HsTeamPrediction, null_hs, \
    Weather
from metagame_balance.hearthstone.datatypes.Types import N_TYPES, N_STATUS, N_STATS, N_ENTRY_HAZARD, N_WEATHER, HsStat, HsType, \
    HsStatus, WeatherCondition, HsEntryHazard


def one_hot(p, n):
    b = [0] * n
    b[p] = 1
    return b


def encode_move(e, move: HsMove):
    e += [move.power / MAX_HIT_POINTS,
          move.acc,
          float(move.pp / MOVE_MAX_PP),
          move.priority,
          move.prob,
          move.target,
          move.recover / MAX_HIT_POINTS,
          move.stat.value,
          move.stage / 2,
          move.fixed_damage / MAX_HIT_POINTS]
    e += one_hot(move.type, N_TYPES)
    e += one_hot(move.status, N_STATUS)
    e += one_hot(move.weather, N_WEATHER)
    e += one_hot(move.hazard, N_ENTRY_HAZARD)


def decode_move(e) -> HsMove:
    power = e[0] * MAX_HIT_POINTS
    acc = e[1]
    pp = int(e[2] * MOVE_MAX_PP)
    priority = e[3]
    prob = e[4]
    target = e[5]
    recover = e[6] * MAX_HIT_POINTS
    stat = HsStat(e[7])
    stage = e[8] * 2
    fixed_damage = e[9] * MAX_HIT_POINTS
    _start = 10
    _end = _start + N_TYPES
    move_type = HsType(e.index(1, _start, _end) - _start)
    _start = _end
    _end = _start + N_STATUS
    status = HsStatus(e.index(1, _start, _end) - _start)
    _start = _end
    _end = _start + N_WEATHER
    weather = WeatherCondition(e.index(1, _start, _end) - _start)
    _start = _end
    _end = _start + N_ENTRY_HAZARD
    hazard = HsEntryHazard(e.index(1, _start, _end) - _start)
    return HsMove(power=power, acc=acc, max_pp=pp, priority=priority, prob=prob, target=target, recover=recover,
                   stat=stat, stage=stage, fixed_damage=fixed_damage, move_type=move_type, status=status,
                   weather=weather, hazard=hazard)


MOVE_ENCODE_LEN = 42


def encode_hs(e, hs: Hs):
    e += [hs.hp / MAX_HIT_POINTS, hs.n_turns_asleep / 5]
    e += one_hot(hs.type, N_TYPES)
    e += one_hot(hs.status, N_STATUS)
    # Hs moves
    for move in hs.moves:
        encode_move(e, move)


def partial_encode_hs(e, hs: Hs, hs_prediction: Union[Hs, None] = None):
    if hs.revealed:
        _hs = hs
    elif hs_prediction is not None:
        _hs = hs_prediction
    else:
        _hs = null_hs
    e += [_hs.hp / MAX_HIT_POINTS, _hs.n_turns_asleep / 5]
    e += one_hot(_hs.type, N_TYPES)
    e += one_hot(_hs.status, N_STATUS)
    # Hs moves
    for i, move in enumerate(hs.moves):
        if move.revealed:
            encode_move(e, move)
        elif hs_prediction is not None and hs_prediction.moves[i] is not None:
            encode_move(e, hs_prediction.moves[i])
        else:
            encode_move(e, null_hs_move)


def decode_hs(e) -> Hs:
    hp = e[0] * MAX_HIT_POINTS
    n_turns_asleep = int(e[1] * 5)
    _start = 2
    _end = _start + N_TYPES
    p_type = HsType(e.index(1, _start, _end) - _start)
    _start = _end
    _end = _start + N_STATUS
    status = HsStatus(e.index(1, _start, _end) - _start)
    _start = _end
    _end = _start + MOVE_ENCODE_LEN
    move0 = decode_move(e[_start:_end])
    _start = _end
    _end = _start + MOVE_ENCODE_LEN
    move1 = decode_move(e[_start:_end])
    _start = _end
    _end = _start + MOVE_ENCODE_LEN
    move2 = decode_move(e[_start:_end])
    _start = _end
    _end = _start + MOVE_ENCODE_LEN
    move3 = decode_move(e[_start:_end])
    hs = Hs(max_hp=hp, p_type=p_type, status=status, move0=move0, move1=move1, move2=move2, move3=move3)
    hs.n_turns_asleep = n_turns_asleep
    return hs


PKM_ENCODE_LEN = 195


def encode_team(e, team: HsTeam):
    e += [team.confused]
    e += team.entry_hazard
    for stat in range(N_STATS):
        e += [team.stage[stat] / 5]
    encode_hs(e, team.active)
    for hs in team.party[:DEFAULT_TEAM_SIZE - 1]:
        encode_hs(e, hs)


def _nonempty_team_pred(team_prediction: HsTeamPrediction) -> bool:
    """If this is an empty team prediction (i.e. the party list is empty), then return false"""
    if not team_prediction or not team_prediction.party:
        return False
    return True


def partial_encode_team(e, team: HsTeam, team_prediction: Union[HsTeamPrediction, None] = None):
    e += [team.confused]
    e += team.entry_hazard
    for stat in range(N_STATS):
        e += [team.stage[stat] / 5]
    partial_encode_hs(e, team.active, team_prediction.active if _nonempty_team_pred(team_prediction) else None)
    for i, hs in enumerate(team.party):
        partial_encode_hs(e, hs, team_prediction.party[i] if _nonempty_team_pred(team_prediction) else None)


def decode_team(e) -> HsTeam:
    confused = e[0]
    _start = 1
    _end = _start + N_ENTRY_HAZARD
    entry_hazard = e[_start: _end]
    _start = _end
    _end = _start + N_STATS
    stage = []
    i = 0
    for stat in range(_start, _end):
        stage.append(e[stat] * 5)
        i += 1
    hss: List[Hs] = []
    for _ in range(DEFAULT_TEAM_SIZE):
        _start = _end
        _end = _start + PKM_ENCODE_LEN
        hss.append(decode_hs(e[_start: _end]))
    team = HsTeam(hss)
    team.confused = confused
    team.entry_hazard = entry_hazard
    return team


TEAM_ENCODE_LEN = 591


def encode_game_state(e, game_state: GameState):
    for team in game_state.teams:
        encode_team(e, team)
    e += one_hot(game_state.weather.condition, N_WEATHER)
    e += [game_state.weather.n_turns_no_clear / 5]


def partial_encode_game_state(e, game_state: GameState, team_prediction: HsTeamPrediction = None):
    encode_team(e, game_state.teams[0])
    partial_encode_team(e, game_state.teams[1], team_prediction)
    e += one_hot(game_state.weather.condition, N_WEATHER)
    e += [game_state.weather.n_turns_no_clear / 5]


def decode_game_state(e) -> GameState:
    teams = [decode_team(e[:TEAM_ENCODE_LEN]), decode_team(e[TEAM_ENCODE_LEN:TEAM_ENCODE_LEN * 2])]
    game_state = GameState(teams, Weather())
    _start = TEAM_ENCODE_LEN * 2
    _end = _start + N_WEATHER
    game_state.weather.condition = WeatherCondition(e.index(1, _start, _end) - _start)
    game_state.weather.n_turns_no_clear = e[_end] * 5
    return game_state


GAME_STATE_ENCODE_LEN = 1188
