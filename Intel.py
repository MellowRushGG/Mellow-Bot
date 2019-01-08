import math, random, asyncio, numpy as np

import sc2
import cv2

from sc2 import run_game, maps, Race, Difficulty, units, unit, position
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.ids import ability_id


########################
###		  Intel       ###
########################

draw_dict = {
                     NEXUS: [15, (0, 255, 0)],
                     PYLON: [3, (20, 235, 0)],
                     PROBE: [1, (55, 200, 0)],
                     ASSIMILATOR: [2, (55, 200, 0)],
                     GATEWAY: [3, (200, 100, 0)],
                     CYBERNETICSCORE: [3, (150, 150, 0)],
                     STARGATE: [5, (255, 0, 0)],
                     VOIDRAY: [3, (255, 100, 0)],
                    }

def intel(self): # why is this asynchronous #FIXED
	game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
	for nexus in self.units(NEXUS).ready:
		nex_pos = nexus.position
		#print(nex_pos) #WHY WAS THIS IN THE TUTORIAL IT'S FLOODING MY FUCKING CONSOLE
		cv2.circle(game_data, (int(nex_pos[0]), int(nex_pos[1])), 10, (0, 255, 0), -1)
		
	flipped = cv2.flip(game_data, 0)
	resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
		
	cv2.imshow('Intel', resized)
	cv2.waitKey(1)

def random_location_variance(self, enemy_start_location):
	x = enemy_start_location[0]
	y = enemy_start_location[1]

	x += ((random.randrange(-10, 10))/100) * enemy_start_location[0]
	y += ((random.randrange(-10, 10))/100) * enemy_start_location[1]

	if x < 0:
		x = 0
	if y < 0:
		y = 0
	if x > self.game_info.map_size[0]:
		x = self.game_info.map_size[0]
	if y > self.game_info.map_size[1]:
		y = self.game_info.map_size[1]

	go_to = position.Point2(position.Pointlike((x,y)))
	return go_to
	
	
async def scout(self):
	scout_bool = False
	if self.iteration < 820:
		if self.worker_scouting:
			#self.combinedActions.append(self, 17, 
			# Since I've already got something scouting. I'll need to get the unit ID of the 
			# worker I use and set an on_unit_death event to set worker_scouting back to False.			
			return
		else:
			scout = self.workers.random
			#self.scout_ID = scout.tag
			# TO-DO: GET UNIT ID OF SCOUT WORKER AND SET AN ON_UNIT_DEATH EVENT HANDLER FOR ITS DEATH
			scout_bool = True
	elif len(self.units(OBSERVER)) > 0 and self.units(OBSERVER)[0].is_idle:
		scout = self.units(OBSERVER)[0]
		self.scout_ID = scout.tag
		scout_bool = True
		if scout.is_idle:
			enemy_location = self.enemy_start_locations[0]
			move_to = random_location_variance(self, enemy_location)
			self.combinedActions.append(scout.move(move_to))
			self.combinedActions.append(scout.hold_position(queue=True))
			self.combinedActions.append(scout(MORPH_SURVEILLANCEMODE, queue=True))
			return
	else:
		if self.units(ROBOTICSFACILITY).ready.noqueue and self.can_afford(OBSERVER) and self.supply_left > 0:
			rf = self.units(ROBOTICSFACILITY).ready.noqueue.random
			self.combinedActions.append(rf.train(OBSERVER))
			return
		elif self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
			if self.units(PYLON).ready.exists:
				worker = self.workers.random
				pylon = self.units(PYLON).ready.random
				location = await self.find_placement(ROBOTICSFACILITY, pylon.position, placement_step=4)
				if worker:
					self.combinedActions.append(worker.build(ROBOTICSFACILITY, location))
	if scout_bool:
		enemy_location = self.enemy_start_locations[0]
		move_to = random_location_variance(self, enemy_location)
		move_to_2 = random_location_variance(self, enemy_location)
		#print(move_to)
		self.combinedActions.append(scout.move(move_to))
		#self.combinedActions.append(scout.patrol(move_to_2), queue=True)
		self.combinedActions.append(scout.hold_position(queue=True))
		return