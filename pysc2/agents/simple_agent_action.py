from absl import logging

from pysc2.agents.simple_agent_def import ACTION_STEP, CG_IDX, COMMAND_CENTER_PATERN
from pysc2.agents.simple_agent_def import QO_NOW, QO_QUEUED, SPAO_MINIMAP, SPAO_SCREEN, CGAO_RECALL, CGAO_SET, CGAO_APPEND
from pysc2.agents.simple_agent_def import SAO_SELECT, SWO_SELECT, SPAO_SELECT, SPAO_SELECT_ALL
from pysc2.agents.simple_agent_def import SCV_MINERALS, MARINE_MINERALS, TANK_MINERALS, TANK_VES
from pysc2.agents.simple_agent_def import MINERAL_COLLECTION
from pysc2.agents.simple_agent_def import MINIMAP_COORDINATE_REPOSITORY
from pysc2.agents.simple_agent_utils import get_buildable_area, pattern_match, pattern_match2, match_in, get_mode_by_unit_type
from pysc2.agents.simple_agent_utils import get_building_area

from pysc2.lib import actions
from pysc2.lib.actions import FUNCTIONS, move_camera
from pysc2.lib.units import Terran, Neutral

class ActionCollection:

    action_queue = None
    status = None
    retry = 0
    retry_threshold = 0

    is_top = True
    is_left = True
    minimap_coordinate = None

    @classmethod 
    def set_action_queue(cls, action_queue):
        cls.action_queue = action_queue

    @classmethod 
    def set_func_queue(cls, func_queue):
        cls.func_queue = func_queue
    
    @classmethod
    def set_is_top(cls, is_top):
        cls.is_top = is_top

    @classmethod
    def set_is_left(cls, is_left):
        cls.is_left = is_left

    @classmethod
    def set_minimap_coordinate(cls):
        if cls.is_top and cls.is_left:
            cls.minimap_coordinate = MINIMAP_COORDINATE_REPOSITORY[0]
        elif not cls.is_top and not cls.is_left:
            cls.minimap_coordinate = MINIMAP_COORDINATE_REPOSITORY[1]
        elif cls.is_top and not cls.is_left:
            cls.minimap_coordinate = MINIMAP_COORDINATE_REPOSITORY[2]
        elif not cls.is_top and cls.is_left:
            cls.minimap_coordinate = MINIMAP_COORDINATE_REPOSITORY[3]
        else:
            logging.info("Illegal born position info.")
        cls.retry_threshold = len(cls.minimap_coordinate)

    @classmethod
    def select_all_army(cls, obs):
        return actions.FunctionCall(FUNCTIONS.select_army.id, [SAO_SELECT])

    @classmethod
    def attack_all_map(cls, obs):
        attack_path = []
        attack_path.append(actions.FunctionCall(FUNCTIONS.Attack_minimap, [QO_QUEUED, []]))
        attack_path.append(actions.FunctionCall(FUNCTIONS.Attack_minimap, [QO_QUEUED, []]))
        attack_path.append(actions.FunctionCall(FUNCTIONS.Attack_minimap, [QO_QUEUED, []]))
        attack_path.append(actions.FunctionCall(FUNCTIONS.Attack_minimap, [QO_QUEUED, []]))
        return attack_path
   
    # 1. obs.feature_screen.unit_type == 0
    # 2. obs.feature_screen.visibility == 2
    # 3. obs.feature_screen.buildable == 1
    # 4. exist such an area with n * n size
    @classmethod
    def find_proper_pos_for_command_center(cls, obs):
        return cls.get_buildable_area(obs, Terran.CommandCenter) 

    @classmethod
    def find_proper_pos_for_supply_depot(cls, obs):
        return cls.get_buildable_area(obs, Terran.SupplyDepot) 

    @classmethod
    def find_proper_pos_for_barracks(cls, obs):
        return cls.get_buildable_area(obs, Terran.Barracks) 

    @classmethod
    def find_proper_pos_for_factory(cls, obs):
        return cls.get_buildable_area(obs, Terran.Factory)

    @classmethod
    def find_proper_pos_for_starport(cls, obs):
        return cls.get_buildable_area(obs, Terran.Starport)

    # list::extend 并不会有任何返回值, 切记!
    # build_xxx_screen 的位置参数是左上还是正中?
    # move_camera_minimap 的位置参数是左上还是正中?
    # minimap [64, 64]
    # prerequisite: select a scv
    @classmethod
    def build_supply_depot_with_move_camera(cls, obs):
        if obs.single_select[0].unit_type != Terran.SCV:
            cls.func_queue.append(cls.build_supply_depot_with_move_camera)
            return cls.select_scv(obs)
        y, x = cls.find_proper_pos_for_supply_depot(obs)
        if y != -1 and x != -1: # there is proper space to build supply depot.
            cls.retry = 0 # clear retry.
            return actions.FunctionCall(FUNCTIONS.Build_SupplyDepot_screen.id, [QO_QUEUED, [x + 5, y + 5]])
        else: # there is no proper space to build supply deopt at current screen.
            if cls.retry < cls.retry_threshold:
                t = cls.retry
                cls.retry = cls.retry + 1
                cls.func_queue.append(cls.build_supply_depot_with_move_camera)
                return actions.FunctionCall(FUNCTIONS.move_camera.id, [cls.minimap_coordinate[t]])
            else:
                cls.retry = 0
                return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def build_barracks_with_move_camera(cls, obs):
        if obs.single_select[0].unit_type != Terran.SCV:
            cls.func_queue.append(cls.build_barracks_with_move_camera)
            return cls.select_scv(obs)
        y, x = cls.find_proper_pos_for_barracks(obs)
        if y != -1 and x != -1: # there is proper space to build supply depot.
            cls.retry = 0 # clear retry.
            return actions.FunctionCall(FUNCTIONS.Build_Barracks_screen.id, [QO_QUEUED, [x + 9, y + 9]])
        else: # there is no proper space to build supply deopt at current screen.
            if cls.retry < cls.retry_threshold:
                t = cls.retry
                cls.retry = cls.retry + 1
                cls.func_queue.append(cls.build_barracks_with_move_camera)
                return actions.FunctionCall(FUNCTIONS.move_camera.id, [cls.minimap_coordinate[t]])
            else:
                cls.retry = 0
                return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def select_scv(cls, obs):
        if obs.player.idle_worker_count > 0:
            return actions.FunctionCall(FUNCTIONS.select_idle_worker.id, [SWO_SELECT])
        else:
            unit_y, unit_x = (obs.feature_screen.unit_type == Terran.SCV).nonzero()
            if len(unit_y) == 0 or len(unit_x) == 0:
                return actions.FunctionCall(FUNCTIONS.no_op.id, [])
            x, y = unit_x[0], unit_y[0]
            return actions.FunctionCall(FUNCTIONS.select_point.id, [SPAO_SELECT, [x, y]])

    @classmethod
    def find_command_center(cls, obs):
        # warning: there must be only on command center in on screen.
        p = COMMAND_CENTER_PATERN
        unit_y, unit_x = pattern_match(obs.feature_screen.unit_type, len(p[0]), len(p), p[0][0])
        cls.status = ACTION_STEP.MOVE_CAMERA_COMMAND_CENTER
        if unit_y != -1 and unit_x != -1:
            cls.retry = 0
            y, x = (unit_y * 2 + len(p)) / 2, (unit_x * 2 + len(p[0])) / 2
            return actions.FunctionCall(FUNCTIONS.select_point.id, [SPAO_SELECT, [x, y]])
        else:
            if cls.retry >= cls.retry_threshold:
                cls.retry = 0
                return actions.FunctionCall(FUNCTIONS.no_op.id, [])
            else:
                t = cls.retry
                cls.retry = cls.retry + 1
                logging.info("find command center with reties: " + str(cls.retry))
                cls.action_queue = [cls.find_command_center] + cls.action_queue
                return actions.FunctionCall(FUNCTIONS.move_camera.id, [SPAO_MINIMAP, cls.minimap_coordinate[t]])

    @classmethod
    def have_command_center(cls, obs):
        if obs.control_groups[CG_IDX.COMMAND_CENTER][0] == Terran.CommandCenter:
            return True
        else:
            return False

    # 如果是选中一个编队，则可能选中多个command center
    # 如果进入find阶段， 则至多选中一个command center
    # barracks, factory, starport 同理
    @classmethod
    def select_command_center(cls, obs):
        if cls.have_command_center(obs):
            return actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_RECALL, [CG_IDX.COMMAND_CENTER]])
        return cls.find_command_center(obs)
    
    @classmethod
    def find_barracks(cls, obs): 
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def have_barracks(cls, obs):
        if obs.control_groups[CG_IDX.BARRACKS][0] == Terran.Barracks:
            return True
        return False

    @classmethod
    def select_barracks(cls, obs):
        if cls.have_barracks(obs):
            return actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_RECALL, [CG_IDX.BARRACKS]])
        return cls.find_barracks(obs)
    
    @classmethod
    def have_factory(cls, obs):
        if obs.control_groups[CG_IDX.FACTORY][0] == Terran.Factory:
            return True
        return False

    @classmethod
    def select_factory(cls, obs):
        if cls.have_factory(obs):
            return actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_RECALL, [CG_IDX.FACTORY]])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def select_starport(cls, obs):
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def train_scv(cls, obs):
        if obs.player.minerals >= SCV_MINERALS and FUNCTIONS.Train_SCV_quick.id in obs.available_actions:
            return actions.FunctionCall(FUNCTIONS.Train_SCV_quick.id, [QO_NOW])
        # logging.info("Cannot train scv.")
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def train_marine(cls, obs):
        if obs.player.minerals >= MARINE_MINERALS and FUNCTIONS.Train_Marine_quick.id in obs.available_actions:
            return actions.FunctionCall(FUNCTIONS.Train_Marine_quick.id, [QO_NOW])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def train_tank(cls, obs):
        if obs.player.minerals >= TANK_MINERALS and obs.player.minerals >= TANK_VES \
            and FUNCTIONS.Train_SiegeTank_quick.id in obs.available_actions:
            return actions.FunctionCall(FUNCTIONS.Train_SiegeTank_quick.id, [QO_NOW])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def get_buildable_area(cls, obs, unit_type):
        map = get_buildable_area(obs)
        pattern = get_mode_by_unit_type(unit_type)
        return pattern_match2(map, pattern)
    
    @classmethod
    def move_camera_for_building_command_center(cls, obs):
        return actions.FunctionCall(FUNCTIONS.no_op.id, []) 
    
    @classmethod
    def build_supply_depot(cls, obs):
        buildable_area = cls.get_buildable_area(obs)
        y, x = pattern_match(buildable_area, 9, 9, 1)
        if y != -1 and x != -1 and FUNCTIONS.Build_SupplyDepot_screen.id in obs.available_actions:
            y = y * 2 - 9
            x = x * 2 - 9
            return actions.FunctionCall(FUNCTIONS.Build_SupplyDeopt_screen.id, [QO_NOW, [x, y]])
        else:
            return actions.FunctionCall(FUNCTIONS.no_op.id, [])
        
    @classmethod
    def build_barracks(cls, obs):
        buildable_area = cls.get_buildable_area(obs)
        y, x = pattern_match(buildable_area, 19, 19, 1)
        if y != -1 and x != -1 and FUNCTIONS.Build_Barracks_screen.id in obs.available_actions:
            y = y * 2 - 19
            x = x * 2 - 19
            return actions.FunctionCall(FUNCTIONS.Build_Barracks_screen.id, [QO_NOW, [x, y]])
        else:
            return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def build_factory(cls, obs):
        buildable_area = cls.get_buildable_area(obs)
        y, x = pattern_match(buildable_area, 19, 19, 1)
        if y != -1 and x != -1 and FUNCTIONS.Build_Factory_screen.id in obs.available_actions:
            return actions.FunctionCall(FUNCTIONS.Build_Factory_screen.id, [QO_NOW, [x, y]])
        else:
            return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def build_starport(cls, obs):
        buildable_area = cls.get_buildable_area(obs)
        y, x = match_in(buildable_area, 19, 19, 1)
        if y != -1 and x != -1 and FUNCTIONS.Build_Starport_screen.id in obs.available_actions:
            return actions.FunctionCall(FUNCTIONS.Build_Starport_screen.id, [QO_NOW, [x, y]])
        else:
            return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def rally_command_center(cls, obs):
        y, x = match_in(obs.feature_screen.unit_type, MINERAL_COLLECTION)
        if y != -1 and x != -1:
            if FUNCTIONS.Rally_Workers_screen.id in obs.available_actions:
                return actions.FunctionCall(FUNCTIONS.Rally_Workers_screen.id, [QO_QUEUED, [x, y]])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def search_path(cls, is_top, is_left):
        target0 = [16, 16]
        target1 = [48, 16]
        target2 = [16, 48]
        target3 = [48, 48]
        global sp
        sp = []
        sp.append(actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_QUEUED, target0]))
        sp.append(actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_QUEUED, target1]))
        sp.append(actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_QUEUED, target3]))
        sp.append(actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_QUEUED, target2]))
        if is_top and is_left:
            tmp = [sp[3], sp[2]]
            sp = [actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_NOW, target1])]
            sp.extend(tmp)
            logging.info("1tmp: " + str(tmp))
            logging.info("1sp: " + str(sp))
        elif is_top and not is_left:
            tmp = [sp[2], sp[0]]
            sp = [actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_NOW, target3])]
            sp.extend(tmp)
            logging.info("sp: " + str(sp))
        elif not is_top and not is_left:
            tmp = [sp[0], sp[1]]
            sp = [actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_NOW, target2])]
            sp.extend(tmp)
            logging.info("3tmp: " + str(tmp))
            logging.info("3sp: " + str(sp))
        elif not is_top and is_left:
            tmp = [sp[1], sp[3]]
            sp = [actions.FunctionCall(FUNCTIONS.Smart_minimap.id, [QO_NOW, target0])]
            sp.extend(tmp)
            logging.info("sp: " + str(sp))
        else:
            sp = []
        logging.info("sp: " + str(sp))
        return sp


    @classmethod
    def control_group_command_center(cls, obs):
        res = get_buildable_area(obs, Terran.CommandCenter)
        pattern = get_mode_by_unit_type(Terran.CommandCenter)
        if FUNCTIONS.select_control_group.id in obs.available_actions:
            if obs.control_groups[CG_IDX.COMMAND_CENTER][0] != Terran.CommandCenter:
                return actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_SET, [CG_IDX.COMMAND_CENTER]]) 
            else:
                return actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_APPEND, [CG_IDX.COMMAND_CENTER]]) 
    
    @classmethod
    def control_group_barracks(cls, obs):
        res = get_building_area(obs, Terran.Barracks)
        pattern = get_mode_by_unit_type(Terran.Barracks)
        y, x = pattern_match2(res, pattern) 
        if y != -1 and x != -1:
            if obs.control_groups[CG_IDX.BARRACKS][0] != Terran.Barracks:
                cls.action_queue.append(actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_SET, [CG_IDX.BARRACKS]]))
            else:
                cls.action_queue.append(actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_APPEND, [CG_IDX.BARRACKS]]))
            y = y + 4
            x = x + 10
            return actions.FunctionCall(FUNCTIONS.select_point.id, [SPAO_SELECT_ALL, [x, y]])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])

    @classmethod
    def control_group_factory(cls, obs):
        res = get_building_area(obs, Terran.Factory)
        pattern = get_mode_by_unit_type(Terran.Factory)
        y, x = pattern_match2(res, pattern) 
        if y != -1 and x != -1:
            if obs.control_groups[CG_IDX.FACTORY][0] != Terran.Factory:
                cls.action_queue.append(actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_SET, [CG_IDX.Factory]]))
            else:
                cls.action_queue.append(actions.FunctionCall(FUNCTIONS.select_control_group.id, [CGAO_APPEND, [CG_IDX.Factory]]))
            y = y + 4
            x = x + 10
            return actions.FunctionCall(FUNCTIONS.select_point.id, [SPAO_SELECT_ALL, [x, y]])
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])
    
    @classmethod
    def check_all_barracks(cls, obs):
       move_camera()
    
    @classmethod
    def check_all_building(cls, obs):
        cls.func_queue.append(cls.check_all_barracks)
        cls.func_queue.append(cls.check_all_factory)
        cls.func_queue.append(cls.check_all_starport)
        return actions.FunctionCall(FUNCTIONS.no_op.id, [])
