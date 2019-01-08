import math, asyncio, random#, numpy as np

import sc2
from sc2 import run_game, maps, Race, Difficulty, units, unit
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
#from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.ids import ability_id

# I'd imagine this will eventually be repurposed into a module for microing units and 
# possibly for the efficient execution of build-order plans (ex. having each gateway 
# train 1 unit in the build-order until they're all building one unit, then adding 
# the units left to be built back onto the stack to be built [since the machine can 
# decide to make a living structure build a unit if my structures are attacked half-way 
# through a construction goal, where certain structures may have had units dequeued 
# because the structure no longer exists]. This could be extended to catching unit 
# destruction events and calculating what that means for my projected build path and 
# future state, so destroyed/dequeued units can be placed back on the build stack).
# 
# Should also handle analysis of enemy infrastructure to single out critical infrastructure
# for their projected build path/macro strat.


def find_target(self, state):
		if len(self.known_enemy_units) > 0:
			return random.choice(self.known_enemy_units)
			
		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures)
			
		else:
			return self.enemy_start_locations[0]


def go_on_the_offensive(self):
		if self.units(STALKER).amount > 15:
			for stalker in self.units(STALKER).idle:
				self.combinedActions.append(stalker.attack(find_target(self, self.state)))
				

def attack(self):
	aggressive_units = {STALKER: [15, 5], VOIDRAY: [8, 3]}
	
	for UNIT in aggressive_units:
		if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
			for s in self.units(UNIT).idle:
				self.combinedActions.append(s.attack(find_target(self, self.state)))
				
		elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
			if len(self.known_enemy_units) > 0:
				for s in self.units(UNIT).idle:
					self.combinedActions.append(s.attack(random.choice(self.known_enemy_units)))

					
def build_offensive_force(self):
	for gw in self.units(GATEWAY).ready.noqueue:
		if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
			if self.can_afford(STALKER) and self.supply_left > 0:
				self.combinedActions.append(gw.train(STALKER))
				
	for sg in self.units(STARGATE).ready.noqueue:
		if self.can_afford(VOIDRAY) and self.supply_left > 0:
			self.combinedActions.append(sg.train(VOIDRAY))
			
			
async def build_offensive_buildings(self):
	if self.units(PYLON).ready.exists:
		pylon = self.units(PYLON).ready.random
			
		if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
			if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE)  and len(self.units(PROBE)) > 0:
				worker = self.workers.random
				location = await self.find_placement(CYBERNETICSCORE, pylon.position, placement_step=4)
				if worker is not None and location is not None:
					self.combinedActions.append(worker.build(CYBERNETICSCORE, location))
					
		elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
			if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and len(self.units(PROBE)) > 0:
				worker = self.workers.random
				location = await self.find_placement(GATEWAY, pylon.position, placement_step=4)
				if worker is not None and location is not None:
					self.combinedActions.append(worker.build(GATEWAY, location))
					
		if self.units(CYBERNETICSCORE).ready.exists:
			if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
				if self.can_afford(STARGATE) and not self.already_pending(STARGATE)  and len(self.units(PROBE)) > 0:
					worker = self.workers.random
					location = await self.find_placement(STARGATE, pylon.position, placement_step=4)
					if worker is not None and location is not None:
						self.combinedActions.append(worker.build(STARGATE, location))
						
						
async def build_gateway(self):
	print("call to: build_gateway")
	if self.can_afford(GATEWAY) and len(self.units(PROBE)) > 0:
		if len(self.units(PYLON).ready) > 0:
			worker = self.workers.random
			pylon = self.units(PYLON).ready.random
			location = await self.find_placement(CYBERNETICSCORE, pylon.position, placement_step=4)
			if worker is not None and location is not None:
				self.combinedActions.append(worker.build(GATEWAY, location))#, queue=True))
		else:
			print("building prerequisite pylon before gateway")
			await self.build_single_pylon()
	if len(self.units(GATEWAY)) > 3:
		self.producerDict["voidrays"][5] += 500
		self.One_OffDict["cybernetics core"][5] += 500
		self.producerDict["gateways"][5] -= 200

async def build_cybernetics_core(self):
	print("call to: build_cybernetics_core")
	if self.can_afford(CYBERNETICSCORE) and len(self.units(PROBE)) > 0:
		if len(self.units(PYLON).ready) > 0:
			worker = self.workers.random
			pylon = self.units(PYLON).ready.random
			location = await self.find_placement(CYBERNETICSCORE, pylon.position, placement_step=4)
			if worker is not None and location is not None:
				self.combinedActions.append(worker.build(CYBERNETICSCORE, location))#, queue=True))
		else:
			print("building prerequisite pylon before cybernetics core")
			await self.build_single_pylon()		

async def build_stargate(self):
	print("call to: build_stargate")
	if self.can_afford(STARGATE) and len(self.units(PROBE)) > 0:
		if len(self.units(PYLON).ready) > 0:
			worker = self.workers.random
			pylon = self.units(PYLON).ready.random
			location = await self.find_placement(STARGATE, pylon.position, placement_step=4)
			if worker is not None and location is not None:
				self.combinedActions.append(worker.build(STARGATE, location))#, queue=True))
		else:
			print("building prerequisite pylon before stargate")
			await self.build_single_pylon()

def build_stalker(self):
	print("call to: build_stalker")
	if len(self.units(GATEWAY).ready) > 0:
		gw = random.choice(self.units(GATEWAY).ready)
		if self.can_afford(STALKER) and self.supply_left > 0 and gw is not None:
			self.combinedActions.append(gw.train(STALKER))#, queue=True))
		# I KNOW THIS IS GOING TO CAUSE PROBLEMS FOR ME IN THE FUTURE, I JUST WANT TO GET SOMETHING FUNCTIONAL WITHOUT CREATING
		# ALL OF THE CODE REQUIRED TO EFFICIENTLY REPRESENT REQUIREMENTS FOR CONSTRUCTING UNITS
	else:  
		self.producerDict['gateways'][5] += 500
			

def build_voidray(self):
	print("call to: build_voidray")
	if len(self.units(STARGATE).ready) > 0:
		sg = random.choice(self.units(STARGATE).ready)
		if self.can_afford(VOIDRAY) and self.supply_left > 0 and sg is not None:
			self.combinedActions.append(sg.train(VOIDRAY))#, queue=True))
	# I KNOW THIS IS GOING TO CAUSE PROBLEMS FOR ME IN THE FUTURE, I JUST WANT TO GET SOMETHING FUNCTIONAL WITHOUT CREATING
	# ALL OF THE CODE REQUIRED TO EFFICIENTLY REPRESENT REQUIREMENTS FOR CONSTRUCTING UNITS
	else:
		self.producerDict["stargates"][5] += 500