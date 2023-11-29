from copy import copy

from metagame_balance.hearthstone.datatypes.Constants import MAX_HIT_POINTS, MOVE_MAX_PP
from metagame_balance.hearthstone.datatypes.Objects import HsMove, HsTemplate, HsFullTeam
from metagame_balance.hearthstone.datatypes.Types import WeatherCondition, HsStatus, MAX_STAGE, HsEntryHazard


def _remove_effects(move: HsMove) -> HsMove:
    move.target = 1
    move.recover = 0.0
    move.status = HsStatus.NONE
    move.stat = 0
    move.stage = 0
    move.fixed_damage = False
    move.weather = WeatherCondition.CLEAR
    move.hazard = HsEntryHazard.NONE
    return move


def std_move_dist(move0: HsMove, move1: HsMove) -> float:
    # attributes distances
    d_power = abs(move0.power - move1.power) / MAX_HIT_POINTS
    d_acc = abs(move0.acc - move1.acc)
    d_max_pp = float(abs(move0.max_pp - move1.max_pp)) / MOVE_MAX_PP
    d_type = float(move0.type != move1.type)
    d_priority = float(abs(move0.priority - move1.priority))
    # effects distance
    d_prob = abs(move0.prob - move1.prob)
    if move0.prob == 0.0:
        move0 = _remove_effects(copy(move0))
    if move1.prob == 0.0:
        move1 = _remove_effects(copy(move1))
    d_target = float(move0.target != move1.target)
    d_recover = abs(move0.recover - move1.recover) / MAX_HIT_POINTS
    d_status = float(move0.status != move1.status)
    d_stat = float(move0.stat != move1.stat)
    d_stage = float(abs(move0.stage - move1.stage)) / MAX_STAGE
    d_fixed_damage = float(move0.fixed_damage != move1.fixed_damage)
    d_weather = float(move0.weather != move1.weather)
    d_hazard = float(move0.hazard != move1.hazard)
    # compound distances
    d_base = d_power + 0.7 * d_acc + 0.1 * d_max_pp + d_type + 0.2 * d_priority
    d_effects = d_prob + d_target + d_recover + d_status + d_stat + d_stage + d_fixed_damage + d_weather + d_hazard
    # total distances
    return d_base + d_effects / 4.0


def std_hs_dist(hs0: HsTemplate, hs1: HsTemplate, move_distance=std_move_dist) -> float:
    d_max_hp = abs(hs0.max_hp - hs1.max_hp) / MAX_HIT_POINTS
    d_type = float(hs0.type != hs1.type)
    d_moves = 0.0
    for move0, move1 in zip(hs0.move_roster, hs1.move_roster):
        d_moves += move_distance(move0, move1) / 5.25
    return d_max_hp + d_type + d_moves / 8.0


def std_team_dist(team0: HsFullTeam, team1: HsFullTeam, pokemon_distance=std_hs_dist) -> float:
    d_hss = 0.0
    t0 = team0.get_battle_team([0, 1, 2])
    t1 = team1.get_battle_team([0, 1, 2])
    for hs0, hs1 in zip([t0.active] + t0.party, [t1.active] + t1.party):
        tmp0 = HsTemplate(set(hs0.moves), hs0.type, hs0.max_hp, hs0.hs_id)
        tmp1 = HsTemplate(set(hs1.moves), hs1.type, hs1.max_hp, hs1.hs_id)
        d_hss += pokemon_distance(tmp0, tmp1) / 5.25
    return d_hss
