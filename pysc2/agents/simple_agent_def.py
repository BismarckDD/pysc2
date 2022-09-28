from pysc2.lib import features
import enum
from pysc2.lib.units import Neutral, Terran

class ACTION_STEP(enum.IntEnum): 
    NAN = 0
    TRAIN_SCV = 1
    TRAIN_MARINE = 2
    TRAIN_TANK = 3
    TRAIN_BANSHEE = 4
    TRAIN_BATTLE_SHIP = 20
    SELECT_COMMAND_CENTER = 21
    SELECT_BARRACKS = 22
    SELECT_FACTORY = 23
    SELECT_STARPORT = 24
    MOVE_CAMERA_COMMAND_CENTER = 41


# SAO: select add option
SAO_SELECT = [0]
SAO_ADD = [1]
# SPAO: select point act option
SPAO_SCREEN = [0]
SPAO_MINIMAP = [1]
SPAO_SELECT = [0]
SPAO_SELECT_ALL = [2]
# QO = queued option
QO_NOW = [0]
QO_QUEUED = [1]
# cgao: control group act option
CGAO_RECALL = [0]
CGAO_SET = [1]
CGAO_APPEND = [2]
# PR: player relative
PR_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
PR_PLAYER_SELF = 1

# SWO: select worker option
SWO_SELECT = [0]

# define some const.
MAX_FOOD_CAP = 200
FOOD_THRESHOLD = 8
SUPPLY_DEPOT_MINERALS = 100
BARRACKS_MINERALS = 150
FACTORY_MINERALS = 200
FACTORY_VES = 100
SCV_MINERALS = 50
MARINE_MINERALS = 50
TANK_MINERALS = 150
TANK_VES = 100

# control group rule
# army: 1 - 5 
# arbitrary: control_group 0
# all barracks: control_group 6
# all factory: control_group 7
# all starport: control_group 8
# all command centers: control_group 9
class CG_IDX(enum.IntEnum):
    BARRACKS = 6
    FACTORY = 7
    STARPORT = 8
    COMMAND_CENTER = 9

PATTERN_W = 18
PATTERN_H = 7
COMMAND_CENTER_PATERN = [[Terran.CommandCenter] * PATTERN_W] * PATTERN_H
COMMAND_BARRACKS = [[Terran.Barracks] * PATTERN_W] * PATTERN_H
COMMAND_FACTORY = [[Terran.Factory] * PATTERN_W] * PATTERN_H
COMMAND_STARPORT = [[Terran.Starport] * PATTERN_W] * PATTERN_H

MINERAL_COLLECTION = [Neutral.BattleStationMineralField, Neutral.BattleStationMineralField750,\
Neutral.MineralField, Neutral.MineralField450, Neutral.MineralField750,\
Neutral.LabMineralField, Neutral.LabMineralField750, Neutral.RichMineralField, Neutral.RichMineralField750,\
Neutral.PurifierMineralField, Neutral.PurifierMineralField750,\
Neutral.PurifierRichMineralField, Neutral.PurifierRichMineralField750]


# minimap search sequence.
MINIMAP_COORDINATE_REPOSITORY = [
    [[8, 8], [8, 24], [24, 8],
     [56, 8], [56, 24], [40, 8],
     [8, 56], [8, 40], [24, 56],
     [56, 56], [56, 40], [40, 56],
     [24, 24], [40, 40], [24, 40], [40, 24]],
    [[56, 56], [56, 40], [40, 56],
     [56, 8], [56, 24], [40, 8],
     [8, 56], [8, 40], [24, 56],
     [8, 8], [8, 24], [24, 8],
     [40, 40], [40, 24], [24, 40], [24, 24]],
    [[8, 8], [8, 24], [24, 8],
     [56, 8], [56, 24], [40, 8],
     [8, 56], [8, 40], [24, 56],
     [56, 56], [56, 40], [40, 56],
     [24, 24], [40, 40], [24, 40], [40, 24]],
    [[8, 8], [8, 24], [24, 8],
     [56, 8], [56, 24], [40, 8],
     [8, 56], [8, 40], [24, 56],
     [56, 56], [56, 40], [40, 56],
     [24, 24], [40, 40], [24, 40], [40, 24]],
]