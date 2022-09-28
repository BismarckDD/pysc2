from queue import Empty
from select import select
import time
import numpy as np
from absl import logging

from pysc2.agents import base_agent
from pysc2.agents.simple_agent_action import ActionCollection
from pysc2.lib import actions, features
from pysc2.lib.actions import FUNCTIONS, build_queue
from pysc2.lib.units import Terran, Neutral

from pysc2.agents.simple_agent_def import BARRACKS_MINERALS, FACTORY_VES, FACTORY_MINERALS, SCV_MINERALS, SUPPLY_DEPOT_MINERALS
from pysc2.agents.simple_agent_def import FOOD_THRESHOLD, MAX_FOOD_CAP, PR_PLAYER_SELF

_NOOP = FUNCTIONS.no_op.id # 什么都不做
_SMART_SCREEN = FUNCTIONS.Smart_screen.id    # 主屏幕执行smart操作 smart: move, attack, rally...
_SMART_MINIMAP = FUNCTIONS.Smart_minimap.id  # 小地图执行smart操作
_RALLY_UNITS_MINIMAP = FUNCTIONS.Rally_Units_minimap.id # 设置集结点
SF_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index #


class FunctionCallGroup:
    def __init__(self):
        self.function_call_list = []


class SimpleAgent(base_agent.BaseAgent):

    def __init__(self):
        super(SimpleAgent, self).__init__()
        self.action_queue = []
        self.func_queue = []
        ActionCollection.set_action_queue(self.action_queue) # related this two queue.
        ActionCollection.set_func_queue(self.func_queue) # related this two queue.
        self.total_army_food = 0
        self.total_army_cnt = 0
        self.minimap_y = 0         # record current minimap size
        self.minimap_x = 0         # record current minimap size
        self.screen_y = 0          # record map size
        self.screen_x = 0          # record map size
        self.is_top = None
        self.is_left = None
        self.max_action_queue_length = 100 # hard code here to check effect.
        self.stage = None
        self.search_path = False

    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.is_top and not self.is_left:
            return [x - x_distance, y - y_distance]
        return [x + x_distance, y + y_distance]


    def first_step(self, timestep):
        obs = timestep.observation
        # save minimap size
        self.minimap_x = len(obs.feature_minimap.height_map[0])
        self.minimap_y = len(obs.feature_minimap.height_map)
        # judge is the base top left
        player_y, player_x = (obs.feature_minimap.player_relative == PR_PLAYER_SELF).nonzero()
        self.is_top = player_y.mean() <= self.minimap_y / 2
        self.is_left = player_x.mean() <= self.minimap_x / 2
        # after get first frame info, set ActionCollection
        ActionCollection.set_is_left(self.is_left)
        ActionCollection.set_is_top(self.is_top)
        ActionCollection.set_minimap_coordinate()
        self.func_queue.append(ActionCollection.train_scv)
        self.func_queue.append(ActionCollection.control_group_command_center)
        # self.func_queue.append(ActionCollection.rally_command_center)
        return ActionCollection.select_command_center(obs)
    
    def need_train_scv(self, obs):
        if obs.player.food_workers <= 30:
            if obs.player.idle_worker_count < 3:
                if obs.player.minerals > SCV_MINERALS and obs.player.food_used < obs.player.food_cap:
                    for item in obs.build_queue:
                        if item.unit_type == Terran.SCV:
                            return False
                    return True
        return False

    def not_in_build_queue(self, obs, unit):
        for item in obs.build_queue:
            if item.unit_type == Terran.SupplyDepot:
                return False
        return True

    def need_supply_depot(self, obs):
        player = obs.player
        if player.food_used + FOOD_THRESHOLD >= player.food_cap and player.food_cap < MAX_FOOD_CAP:
            if player.minerals >= SUPPLY_DEPOT_MINERALS:
                if self.not_in_build_queue(obs, Terran.SupplyDepot):
                    return True
        return False
    
    def need_barracks(self, obs):
        # cnt of factory is less than 2 * cnt of command center: cg7
        # resource is enough
        # not exist bulding barracks
        cg = obs.control_groups
        if cg[7][0] != Terran.Barracks or cg[8][1] <= cg[9][1] * 2:
            if obs.player.minerals > BARRACKS_MINERALS:
                if self.not_in_build_queue(obs, Terran.Barracks):
                    return True
        return False
    
    def need_factory(self, obs):
        # cnt of factory is less than 2 * cnt of command center
        # there must be one barracks 
        # resource is enough
        cg = obs.control_groups
        if cg[7][0] != Terran.Barracks or cg[8][1] <= cg[9][1] * 2:
            if obs.player.minerals > FACTORY_MINERALS and obs.player.vespene > FACTORY_VES:
                if self.not_in_build_queue(obs, Terran.Factory):
                    return True
        return False
    
    def need_starport(self, obs):
        return False

    def step(self, timestep):
        super(SimpleAgent, self).step(timestep)
        # adjust game speed.
        # time.sleep(0.04) # 25 step each second.
        # first step, we should initialize some params here.
        if timestep.first():
            return self.first_step(timestep)
        # last step, do nothing
        if timestep.last():
            return actions.FunctionCall(_NOOP, [])
        # mid step
        obs = timestep.observation

        # TODO: consider about alert appears, adjust sequence
        if len(self.action_queue) != 0:
            act = self.action_queue.pop(0)
            # if action.id is not obs.available_actions:
            #   logging.info("action is not available: expected: {}, real: {}.", str(action), str(obs.available_actions)) 
            #   return actions.FunctionCall(_NOOP, [])
            return act
        
        if len(self.func_queue) != 0:
            func = self.func_queue.pop(0)
            return func(obs)

        # (Pdb) obs.player
        # NamedNumpyArray([ 1, 60,  0, 12, 15,  0, 12,  0,  0,  0,  0],
        # ['player_id', 'minerals', 'vespene', 'food_used', 'food_cap', 'food_army', 'food_workers',
        # 'idle_worker_count', 'army_count', 'warp_gate_count', 'larva_count'], dtype=int32)
        if not self.search_path:
            self.action_queue.extend(ActionCollection.search_path(self.is_top, self.is_left))
            self.search_path = True
            return ActionCollection.select_scv(obs)
        
        if self.need_train_scv(obs):
            self.func_queue.append(ActionCollection.train_scv)
            return ActionCollection.select_command_center(obs)

        if self.need_supply_depot(obs):
            logging.info("now we need supply depot.")
            self.func_queue.append(ActionCollection.build_supply_depot_with_move_camera)
            return ActionCollection.select_scv(obs)

        if self.need_barracks(obs):
            logging.info("now we need barracks.")
            self.func_queue.append(ActionCollection.build_barracks_with_move_camera)
            return ActionCollection.select_scv(obs)

        if self.need_factory(obs):
            logging.info("now we need factory.")
            return ActionCollection.select_scv(obs)
        
        return actions.FunctionCall(_NOOP, [])