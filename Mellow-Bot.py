#!python3

# IN ORDER TO LAUNCH THIS FILE WITH PYTHON 3, YOU MUST CALL IT WITH "py mellow_bot.py" OR "python3 mellow_bot.py". 
# Otherwise the cmd interpreter will try to run this with Python 2 and it'll throw a fit about shit like asyncio...

import math, random, asyncio, numpy as np, cv2, csv
import sys

from Offense_Methods import *
from Intel import *
from BOSS import *
#from Economy import *

import sc2
from sc2.game_state import *
import sc2.game_data
from sc2.game_data import *
from sc2 import run_game, maps, Race, Difficulty, units, unit, game_data, game_info, position
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.ids import ability_id

###################################################################################################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###################################################################################################################################################


class MellowBot(sc2.BotAI):


	# this'll be a set of points. Each time I want to create a PYLON I'll grab the first item in the set. Each set will contain points such that
	# no two points are closer than ~5 units to each other, that way I can have a somewhat efficient spread of PYLONs in my base which don't
	# unnecessarily overlap.
	# TO-DO: utilize a packing algorithm (2D ball-packing?) and/or a machine learning-/B.O.S.S-based PYLON distribution scheme.
	basePylonPlanningSet = [] 	
	baseRadius = 5;

	# {"unit" : [(0)starting_amount, (1)mineral_cost, (2)vespene_cost, (3)time_to_complete, (4)unit_cost, (5)heuristic_value, (6)UNITTYPEID, (7)construction_function, (8)awaitable ? 1 : 0]}

	#producerDict = {"workers" : [0,50,0,12,1,0,PROBE,build_single_worker,0], "assimilators" : [0,75,0,21,0,0,ASSIMILATOR,build_single_assimilator,0], 
	#	"pylons" : [0,100,0,18,-8,0,PYLON,build_pylons,1], "gateways" : [0,150,0,46,0,0,GATEWAY,build_gateway,1], "stargates" : [0,150,150,43,0,10,STARGATE,build_stargate,1],
	#	"stalkers" : [0,125,50,30,2,0,STALKER,build_stalker,0], "voidrays" : [0,250,150,43,4,0,VOIDRAY,build_voidray,0]}
		
	#One_OffDict = {"cybernetics core" : [0,150,0,36,0,0,CYBERNETICSCORE]}

	#BOSS_Nexus_Average_Distance = np.array([0,1]) # for a weird idea I have #nvm
	BOSS_State_Resources = [0,0]
	BOSS_State_In_Progress_Actions = [] #Maybe made up of tuples/dicts/things with (unit, time_to_completion, unit_ID, unit_location if applicable, construction_function) 
	BOSS_Worker_Econ_Split_Array = np.array([0,0])
	BOSS_Assimilator_ID_List = []
	
	BOSS_RESOURCE_MINERALS_PER_WORKER_PER_MINUTE = 102
	BOSS_RESOURCE_GAS_PER_WORKER_PER_MINUTE = 38
	
	BOSS_Build_Order = []
	heuristic_high_score = -999999999
		
	worker_scouting = False
	BOSS_iter = 0
	
	#scout_ID = null


	def __init__(self, csv_READ_file_number, csv_WRITE_file_number):
		self.ITERATIONS_PER_MINUTE = 165
		self.MAX_WORKERS = 50
		
		self.CSV_READ_FILE_NUMBER = csv_READ_file_number
		self.CSV_WRITE_FILE_NUMBER = csv_WRITE_file_number
		file_name = 'SC2AI'
		producerDictFieldNames = ['workers', 'gateways', 'stargates', 'stalkers', 'voidrays']
		
		if csv_READ_file_number != 0:
			read_file_name = file_name + str(self.CSV_READ_FILE_NUMBER) + '.csv'
			reading_file = open(read_file_name, 'r')
			#producerDictFieldNames = ['workers', 'assimilators', 'nexuses', 'pylons', 'gateways', 'stalkers', 'voidrays']
			self.csv_reader = csv.DictReader(reading_file, fieldnames=producerDictFieldNames)
			
		if csv_WRITE_file_number != 0:
			write_file_name = file_name + str(self.CSV_WRITE_FILE_NUMBER) + '.csv'
			#producerDictFieldNames = ['workers', 'gateways', 'stalkers', 'voidrays']
			writing_file = open(write_file_name, 'w')
			self.csv_writer = csv.DictWriter(writing_file, fieldnames=producerDictFieldNames)
			
		update_heuristic_values(self, self.BOSS_iter, self.CSV_READ_FILE_NUMBER, self.CSV_WRITE_FILE_NUMBER) # 0th iteration heuristics
		
		
	
	
	# What's done every "step". Need to make it so that the distribute/build commands check to see if 
	# something should be done && isn't in a queue to be done already
	# in a way that's thread-safe (use futures?)
	#
	# I'll probably have to have observation events asynchronous (multithreaded?) while having execution (on_step) stuff not be asynchronous	
	async def on_step(self, iteration):
	
		# First set of commands
		
		if iteration == 0: #game start
			await self.on_game_start() # could just use the bot_ai.py's on_start method...
	
	
		if iteration % 500 == 0: #print time
			print("Time: " + str(self.time / 60) + ":" + str(self.time % 60) + "\n")
			print(self.producerDict)
			print("\n\n")
			
	

		# Set of commands for every step
		self.iteration = iteration #what the fuck is the point of this code
		self.combinedActions = []

		#self.build_single_assimilator() #debugging #this function doesn't seem to be working
		
		# Gonna just hard-code some build order stuff in right now, but I'm going to do it in such a way that it won't be hard/necessary to
		# refactor the code once I start implementing RL/ML

		#Intel
		intel(self)
		
		#B.O.S.S
		if iteration % 100 == 50:
			if len(self.units(PROBE)) > 0: #debugging
				for probe in self.units(PROBE):
					print(probe.orders)
					print(type(probe.orders))
			if len(self.units(NEXUS)) > 0: #debugging
				nexus = random.choice(self.units(NEXUS))
				print(self.state.vespene_geyser.closer_than(15.0, nexus))		
			
			# OLD BAD SEARCH STUFF
			#---------------------------------------------
			update_list_of_producers(self)
			self.heuristic_high_score = 0
			self.BOSS_Build_Order.clear()
			update_heuristic_values(self, self.BOSS_iter, self.CSV_READ_FILE_NUMBER, self.CSV_WRITE_FILE_NUMBER)
			#await scout(self)
			self.BOSS_iter += 1
			#bad_search(self, [self.minerals, self.vespene, 0, 0])
			only_once(self, [self.minerals, self.vespene, 0, 0]) # this only runs when self.build_assimilators() is called later down in #Economy????
			print("\n\n\n\n\n\n\n\n")
			print("\n\n\nself.BOSS_Build_Order: ", self.BOSS_Build_Order)
			for unit in self.BOSS_Build_Order:
				print(unit)
			print("self.minerals: ", self.minerals)
			print("self.heuristic_high_score: ", self.heuristic_high_score)
			for boss in self.BOSS_Build_Order:
				if (self.universalDict[boss][8] == 1):
					print(self.universalDict[boss][7])#debugging
					await self.universalDict[boss][7](self)
				else:
					print(self.universalDict[boss][7])#debugging
					self.universalDict[boss][7](self)
			print("\n\n\n")
			# END OF OLD BAD SEARCH STUFF
			#---------------------------------------------
		
		#Economy
		if iteration % 40 == 0:
			await self.distribute_workers()
			#self.build_workers()
			await self.build_pylons()
			self.utilize_inactive_workers() # this is an already extant part of distribute_workers, but for some reason build_pylons would idle 1 worker every time & distribute_workers wouldn't un-idle them
			self.build_assimilators()
			#await self.expand()
		
		#Offense_Methods
		#if iteration % 40 == 0:
			#await build_offensive_buildings(self)
		#build_offensive_force(self)
		#await build_offensive_buildings(self)
		#build_offensive_force(self)
		go_on_the_offensive(self)
		attack(self)
		
		#RL/ML
		
		
		#End of step
		await self.do_actions(self.combinedActions)
		
		#debugging
		#for nexus in self.units(NEXUS).not_ready:
		#	print(str(nexus.build_progress))
	
	async def getPositionsAroundUnit(self, unit, minRange=0, maxRange=10, stepSize=0.2, locationAmount=64, unit_type = None):
	# Stolen from Burny, who apparently forgot that he made a variable called "stepSize" lol
		assert isinstance(unit, (Unit, Point2, Point3))
		if isinstance(unit, Unit):
			loc = unit.position.to2
		else:
			loc = unit
		positions = [Point2(( \
			loc.x + distance * math.cos(math.pi * 2 * alpha / locationAmount), \
			loc.y + distance * math.sin(math.pi * 2 * alpha / locationAmount))) \
			for alpha in range(locationAmount)
			for distance in range(minRange, maxRange+1)]
		if unit_type == None: 
			# Don't thin the positions array by eliminating points which a unit of type unit_type isn't able to be placed
			return positions
		else:
			# Do thin the positions array by eliminating points which a unit of type unit_type isn't able to be placed
			iterator = 1
			positionUnderConsideration = 0
			while(iterator < len(positions) - 1):
				if not await self.can_place(unit_type, positions[iterator]):
					del positions[iterator]
					# DON'T increment iterator, since the object previously at the iterator's position has been removed and the object which would have been next has now taken its place
				else: 
					positionUnderConsideration = iterator
					iterator = iterator + 1
			if (unit_type == PYLON): # Thin the positions out by eliminating those points which would lead to two pylons being unnecessarily close together
				iterator = 1
				positionUnderConsideration = 0
				while(iterator < len(positions) - 1):
					if positions[iterator].distance_to_point2(positions[positionUnderConsideration]) < 5:
						del positions[iterator]
						# DON'T increment iterator, since the object previously at the iterator's position has been removed and the object which would have been next has now taken its place
					else: 
						positionUnderConsideration = iterator
						iterator = iterator + 1
		return positions

	
	def build_assimilators(self):
		for nexus in self.units(NEXUS).ready:
			vespene_geysers_to_be_ASSIMILATED = self.state.vespene_geyser.closer_than(15.0, nexus)
			for vesp in vespene_geysers_to_be_ASSIMILATED:
				if not self.can_afford(ASSIMILATOR):
					break
				worker = self.select_build_worker(vesp.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vesp).exists:
					self.combinedActions.append(worker.build(ASSIMILATOR, vesp))
					
					
	def build_single_assimilator(self):
		for nexus in self.units(NEXUS).ready:
			vespene_geysers_to_be_ASSIMILATED = self.state.vespene_geyser.closer_than(15.0, nexus)
			for vesp in vespene_geysers_to_be_ASSIMILATED:
				if not self.can_afford(ASSIMILATOR):
					break
				worker = self.select_build_worker(vesp.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vesp).exists:
					self.combinedActions.append(worker.build(ASSIMILATOR, vesp))
					return
		"""while (i < len(vespene_geysers_to_be_ASSIMILATED)):
			vesp = vespene_geysers_to_be_ASSIMILATED[i]
			if not self.units(ASSIMILATOR).closer_than(1.0, vesp).exists:
				worker = self.select_build_worker(vesp.position)
				if worker is not None and not self.can_afford(ASSIMILATOR):
					self.combinedActions.append(worker.build(ASSIMILATOR, vesp))
					i = 99
			i += 1"""

	
	def utilize_inactive_workers(self):
		for idle_worker in self.workers.idle:
			mf = self.state.mineral_field.closest_to(idle_worker)
			self.combinedActions.append(idle_worker.gather(mf))

		
	def build_workers(self):
		if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)) and len(self.units(PROBE)) < self.MAX_WORKERS:
			for nexus in self.units(NEXUS).ready.noqueue:
				if self.can_afford(PROBE) and nexus is not None:
					self.combinedActions.append(nexus.train(PROBE))


	def build_single_worker(self):
		if True:
			if len(self.units(NEXUS)) > 0:
				if len(self.units(NEXUS).ready.noqueue) > 0:
					nexus = random.choice(self.units(NEXUS).ready.noqueue)
					if self.can_afford(PROBE) and nexus is not None:
						self.combinedActions.append(nexus.train(PROBE))#, queue=True))
				else:
					nexus = random.choice(self.units(NEXUS).ready)
					if self.can_afford(PROBE) and nexus is not None:
						self.combinedActions.append(nexus.train(PROBE, queue=True))#, queue=True))

					
	# To-Do for build_pylons:
	"""
	# ~DONE~ Need to set the worker back to collecting stuff, since they stop doing anything after placing a pylon
	#
	# Need to have a (B.O.S.S.-esque?) model for N steps ahead which takes into account which buildings I want 
	# to have constructed and how much power I'll need to run them
	#
	# Need to not put pylons in the way of workers collecting resources so that resource collection is as 
	# efficient as possible
	"""			
	async def build_pylons(self):
		if self.supply_left < 5 and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					workers = self.workers.gathering
					if workers:
						worker = workers.furthest_to(workers.center)
						
						#print("Finding a place to build a pylon")
						
						while(not len(self.basePylonPlanningSet) > 0 or not await self.can_place(PYLON, self.basePylonPlanningSet[0])):
							if len(self.basePylonPlanningSet) > 0:
								del self.basePylonPlanningSet[0]
							else:
								self.baseRadius += 4
								self.basePylonPlanningSet = await self.getPositionsAroundUnit(self.units(NEXUS).first, minRange=self.baseRadius, maxRange=self.baseRadius + 1, stepSize=0.2, locationAmount=64 * (self.baseRadius - 5), unit_type = PYLON)

						#print("Found one")
						self.combinedActions.append(worker.build(PYLON, self.basePylonPlanningSet.pop()))
						return
						# This code needs to be re-written hard-core, but right now this should be fine
						# OK, I kinda re-wrote it. Pylons now spiral outward. Their increase in radius could be adjusted though, but meh
						#

						
	async def build_single_pylon(self):
		nexuses = self.units(NEXUS).ready
		if nexuses.exists:
			if self.can_afford(PYLON):
				workers = self.workers.gathering
				if workers:
					worker = workers.furthest_to(workers.center)
					#worker.#un-idle the worker so that it doesn't fall prey to the problem I outlined below
					#print("Finding a place to build a pylon")
					while(not len(self.basePylonPlanningSet) > 0 or not await self.can_place(PYLON, self.basePylonPlanningSet[0])):
						if len(self.basePylonPlanningSet) > 0:
							del self.basePylonPlanningSet[0]
						else:
							self.baseRadius += 4
							self.basePylonPlanningSet = await self.getPositionsAroundUnit(self.units(NEXUS).first, minRange=self.baseRadius, maxRange=self.baseRadius + 1, stepSize=0.2, locationAmount=64 * (self.baseRadius - 5), unit_type = PYLON)

					#print("Found one")
					self.combinedActions.append(worker.build(PYLON, self.basePylonPlanningSet.pop(), queue=True))
					return
					# This code might end up choosing the same unit to construct different things because it won't have updated its ready.noqueue status before it
					# evaluates the list again. maybe that doesn't matter though, since I set it to queue=true.
					
						
						
	async def expand(self):
		if self.units(NEXUS).amount < (self.iteration / (2 * self.ITERATIONS_PER_MINUTE)) and self.can_afford(NEXUS):
			await self.expand_now()

	
	async def on_game_start(self):
		await self.chat_send("MellowBot v0.2.1 (Overhaul of v0.2.0's B.O.S.S System)")
		print(draw_dict)
		self.basePylonPlanningSet = await self.getPositionsAroundUnit(self.units(NEXUS).first, minRange=self.baseRadius, maxRange=7, stepSize=0.2, locationAmount=64, unit_type = PYLON)
							
	
	# {"unit" : [(0)starting_amount, (1)mineral_cost, (2)vespene_cost, (3)time_to_complete, (4)unit_cost, (5)heuristic_value, (6)UNITTYPEID, (7)construction_function, (8)awaitable ? 1 : 0]}
	
	producerDict = {"workers" : [0,50,0,12,1,300,PROBE,build_single_worker,0], "gateways" : [0,150,0,46,0,400,GATEWAY,build_gateway,1], "stargates" : [0,150,150,43,0,400,STARGATE,build_stargate,1],
		"stalkers" : [0,125,50,30,2,300,STALKER,build_stalker,0], "voidrays" : [0,250,150,43,4,400,VOIDRAY,build_voidray,0]}
		
	One_OffDict = {"cybernetics core" : [0,150,0,36,0,300,CYBERNETICSCORE,build_cybernetics_core,1], "nexuses" : [1,400,0,71,-15,400,NEXUS,expand,1], 
	"assimilators" : [0,75,0,21,0,300,ASSIMILATOR,build_single_assimilator,0], "pylons" : [0,100,0,18,-8,300,PYLON,build_single_pylon,1]}

	universalDict = {"workers" : [0,50,0,12,1,0,PROBE,build_single_worker,0], "assimilators" : [0,75,0,21,0,0,ASSIMILATOR,build_single_assimilator,0], 
		"pylons" : [0,100,0,18,-8,0,PYLON,build_single_pylon,1], "gateways" : [0,150,0,46,0,0,GATEWAY,build_gateway,1], "stargates" : [0,150,150,43,0,10,STARGATE,build_stargate,1],
		"stalkers" : [0,125,50,30,2,0,STALKER,build_stalker,0], "voidrays" : [0,250,150,43,4,0,VOIDRAY,build_voidray,0], 
		"cybernetics core" : [0,150,0,36,0,0,CYBERNETICSCORE,build_cybernetics_core,1], "nexuses" : [1,400,0,71,-15,0,NEXUS,expand,1]}

	
###################################################################################################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###################################################################################################################################################
							
"""result = run_game(maps.get("AbyssalReefLE"), [
	Bot(Race.Protoss, MellowBot(0,0)),
	Computer(Race.Terran, Difficulty.Easy)
], realtime=False)"""

def main_function(a=0,b=0):
	if a != 0:
		print("reading from csv file number: ", a)
	if b != 0:
		print("writing to csv file number: ", b)
	if a == b and b == 0:
		print("running game without reading or writing to a file")
	result = run_game(maps.get("AbyssalReefLE"), [
	Bot(Race.Protoss, MellowBot(a,b)),
	Computer(Race.Terran, Difficulty.Easy)
], realtime=False)

	if result.value == 1:
		print(result)
		print("WIN")
	elif result.value == 2:
		print(result)
		print("LOSS")
		
	sys.stdout.write(str(result.value)) # used for ML when spawned as a subprocess of a larger process

	
a = int(sys.argv[1])
b = int(sys.argv[2])
main_function(a,b)

"""
# result.value: 1 = Win; 2 = Loss; 3 = Tie; 4 = Undecided
if result.value == 1:
	print(result)
	print("WIN")
elif result.value == 2:
	print(result)
	print("LOSS")
	
sys.stdout.write(str(result.value)) # used for ML when spawned as a subprocess of a larger process
"""
#print(result) #returns "result.X" where X is either a "Victory", "Defeat", or some other stuff described in sc2api_pb2.py. This will be useful later in analyzing self-training data