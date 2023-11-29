from typing import Optional

from elo import INITIAL

from metagame_balance.hearthstone.competition import Competitor
from metagame_balance.hearthstone.datatypes.Constants import BASE_HIT_POINTS
from metagame_balance.hearthstone.datatypes.Objects import HsRoster, Hs, HsTemplate, HsFullTeam, HsMove
from metagame_balance.hearthstone.datatypes.Types import HsStatus, HsEntryHazard, WeatherCondition


STANDARD_TOTAL_POINTS = 11


def get_move_points(move: HsMove) -> int:
    points = 0
    points += max(int((move.power - 30.) / 30.) + ((move.power - 30.) % 30. > 0), 0)
    points += int(move.priority)
    points += int(move.recover > 0.)
    points += int(move.stage > 0.)
    points += int(move.status != HsStatus.NONE)
    points += int(move.fixed_damage > 0.)
    points += int(move.weather != WeatherCondition.CLEAR)
    points += int(move.hazard != HsEntryHazard.NONE)
    return points


def get_hs_points(hs: Hs) -> int:
    points = 0
    points += int((hs.hp - BASE_HIT_POINTS) / 30.) + ((hs.hp - BASE_HIT_POINTS) % 30. > 0)
    for i in range(4):
        points += get_move_points(hs.moves[i])
    return points


def legal_move_set(hs: Hs, template: HsTemplate) -> bool:
    # there must be no repeated members
    for i in range(len(hs.moves)):
        move = hs.moves[i]
        for j in range(i + 1, len(hs.moves)):
            if move == hs.moves[j]:
                return False
    # all members must be instances of roster
    for move in hs.moves:
        valid = False
        for roster_move in template.move_roster:
            valid = move == roster_move
            if valid:
                break
        if not valid:
            return False
    return True


def legal_team(team: HsFullTeam, roster: HsRoster) -> bool:
    # there must be no repeated members
    for i in range(len(team.hs_list)):
        hs_id = team.hs_list[i].hs_id
        for j in range(i + 1, len(team.hs_list)):
            if hs_id == team.hs_list[j].hs_id:
                return False
    # all members must be instances of roster
    for hs in team.hs_list:
        for template in roster:
            if hs.hs_id == template.hs_id:
                valid = hs.type == template.type and 1.0 <= hs.max_hp <= template.max_hp and legal_move_set(hs,
                                                                                                              template)
                if not valid:
                    return False
    return True


class CompetitorManager:

    def __init__(self, c: Competitor):
        self.competitor = c
        self.team: Optional[HsFullTeam] = None
        self.elo: float = INITIAL
