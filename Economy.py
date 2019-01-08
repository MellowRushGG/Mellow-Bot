import math, asyncio, random#, numpy as np

import sc2
from sc2 import run_game, maps, Race, Difficulty, units, unit
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
#from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.ids import ability_id





def take_into_account_expansion(self):
	# refresh a list of nexuses/assimilators/etc.
	# probably just need to take into consideration
	# assimilators
	self.BOSS_Assimilator_ID_List.clear() #refresh ass_ID list
	if len(self.units(NEXUS)) > 0:
		for nexus in self.units(NEXUS):
			for vg in self.state.vespene_geyser.closer_than(15.0, nexus):
				self.BOSS_Assimilator_ID_List.append(vg.tag)
		#if len(self.units(NEXUS)) > self.BOSS_Average_Nexus_Distance[1]:
			#nvm

def refresh_worker_econ_split(self):
	self.BOSS_Worker_Econ_Split_Array[0] = 0 # of workers collecting minerals
	self.BOSS_Worker_Econ_Split_Array[1] = 0 # of workers collecting vespene
	if len(self.units(NEXUS)) > 0 and len(self.units(PROBE)) > 0:
		for worker in self.units(PROBE):
			for ass_ID in self.BOSS_Assimilator_ID_List:
				if worker.orders[1] == ass_ID or worker.is_carrying_vespene(self):
					self.BOSS_Worker_Econ_Split_Array[1] += 1
				else:
					self.BOSS_Worker_Econ_Split_Array[0] += 1
					
					
def simulate_state_progression(self, time): -> list
	# time is in seconds
	# workers return a mean of 34 minerals per minute
	# and 38 gas per minute.
	# ((time * 34 * mineral_workers) / 60) and 
	# ((time * 38 * vespene_workers) / 60 are
	# admissible guesses/heuristics, albeit ones which
	# should be improved later by changing to floats
	list_return = []
	list_return.append(time * 34 * self.BOSS_Worker_Econ_Split_Array[0] / 60)
	list_return.append(time * 38 * self.BOSS_Worker_Econ_Split_Array[1] / 60)
	
	# check which durative activities will have completed
	# and report the progress of those which will not have
	
	return list_return

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	