import math, asyncio, random, csv#, numpy as np

import sc2
from sc2 import run_game, maps, Race, Difficulty, units, unit, game_info, game_state
from sc2.unit import Unit
from sc2.units import Units
import sc2.game_data
from sc2.game_data import *
from sc2.position import Point2, Point3
#from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.ids import ability_id

# Each unit(key) needs to have added to it a rewards/heuristic value.
# {"unit" : [starting_amount, mineral_cost, vespene_cost, time_to_complete, unit_cost, heuristic_value, UNITTYPEID, construction_function]}
# producerDict = {"workers" : [0,50,0,12,1,0,PROBE,self.build_single_worker], "assimilators" : [0,75,0,21,0,0,ASSIMILATOR,self.build_single_assimilator], 
# "pylons" : [0,100,0,18,-8,0,PYLON,self.build_pylons], "gateways" : [0,150,0,46,0,0,GATEWAY,build_gateway], "stargates" : [0,150,150,43,0,10,STARGATE,build_stargate],
# "stalkers" : [0,125,50,30,2,0,STALKER,build_stalker], "voidrays" : [0,250,150,43,4,0,VOIDRAY,build_voidray]}

def update_list_of_producers(self):
	self.producerDict["workers"][0] = len(self.workers.ready)
	#self.producerDict["assimilators"][0] = len(self.units(ASSIMILATOR).ready)
	#self.producerDict["pylons"][0] = len(self.units(PYLON).ready)
	self.producerDict["gateways"][0] = len(self.units(GATEWAY).ready)
	self.producerDict["stargates"][0] = len(self.units(GATEWAY).ready)
	#self.producerDict["crystals"][0] = self.minerals
	#self.producerDict["vespene"][0] = self.vespene
	self.producerDict["stalkers"][0] = len(self.units(STALKER).ready)
	self.producerDict["voidrays"][0] = len(self.units(VOIDRAY).ready)
	
	self.One_OffDict["nexuses"][0] = len(self.units(NEXUS).ready)
	self.One_OffDict["assimilators"][0] = len(self.units(ASSIMILATOR).ready)
	self.One_OffDict["pylons"][0] = len(self.units(PYLON).ready)
	
	
def update_heuristic_values(self, BOSS_iter, csv_READ_file_number=0, csv_WRITE_file_number=0):
	if csv_READ_file_number != 0:
		# get the heuristic values for each unit from the given CSV file for the current BOSS_iter
		# if a set of heuristic values isn't available for the given BOSS_iter, keep the 
		# previous set of heuristic values +/- random variance
		
		try:
			readDict = next(self.csv_reader)
			if (readDict == {'workers' : '!', 'gateways' : '!', 'stargates' : '!', 'stalkers' : '!', 'voidrays' : '!'}):
				self.csv_WRITE_file_number = 0
				print("hit end of file")
			else:
				for unit in self.producerDict:
					self.producerDict[unit][5] = int(readDict[unit])
		except csv.Error as e:
			print("hit end of csv read file")
		"""try:
			for unit in self.producerDict:
				self.producerDict[unit][5] = self.csv_reader[BOSS_iter][unit]
		except IOError:
			print("hit end of csv read file")"""

	# Add variance
	for row in self.producerDict:
		self.producerDict[row][5] += random.randint(-200,200)
		if self.producerDict[row][5] < -10:
			self.producerDict[row][5] = -10
			
	if csv_WRITE_file_number != 0:
		# write the current heuristic value into a new BOSS_iter row in a csv file, which will 
		# not be deleted if the bot wins the match
		
		#stringThing = ""
		writeDict = {}
		for unit in self.producerDict:
			#stringThing += self.producerDict[unit][5] + ","
			writeDict[unit] = self.producerDict[unit][5]
			#print(self.producerDict[unit][5])
		#stringThing = stringThing[:-1]
		
		self.csv_writer.writerow(writeDict)
	
	self.BOSS_iter += 1


"""	
# bad_search should utilize knowledge of what the enemy is building (knowledge gained from scouting) 
# to set the rewards/heuristics for each building/unit/macro strategy.
# 
# Then, it'll utilize a B.O.S.S system to plan ahead for some amount of time, and the successful 
# completion of the plan will affect the rewards/heuristics used for the next planning phase.
# Failure to complete some/all of the plan will also affect the rewards/hearistics
#
# The specificities of how much each building/macro strategy will be weighted given the enemy's 
# scouted factors should be determined through analysis of professional replays AND self-training 
# (playing against itself). Games against itself can utilize simulated-annealing-esque learning,
# genetic algorithms, and reinforcement learning.
#
# Uncertainty can be factored in by favoring defense, aggression, more scouting, or even No-Ops 
# (NO-OPs will need to be added). Macro strategies will need to be factored in, and should be given
# their own package. In this macro strategy package the macro plan will be set and the rewards used 
# by the B.O.S.S system will also be set (though those are kinda the same thing).
#
# TO-DO: need to create a "bar" which selected strategies must beat in order to be enacted, that way
# the NO-OPs will have value
	
# This code needs to be cleaned up and sped up.

# TO-DO: Fix; Optimize; Change this to recur every time the longest 
# queued action completes; Use the corrected version to replace many
# of the current Offense_Methods; Hash state to ignore searching 
# dupicates; fix the problem where the highest valued unit is just
# bought as many times as possible (IE make unit heuristic depreciate 
# if unit is already in build_plan for certain 1-off structures/units
"""

def bad_search(self, build_plan, heuristic_score=0, newItem=None, current_depth=0):
	if newItem != None:
		#print("Considering new unit for build_plan: " + newItem.name) #debugging
		newUnit = self._game_data.units[newItem.value]
		newUnitCost = self._game_data.calculate_ability_cost(newUnit.creation_ability)
		build_plan[0] -= newUnitCost.minerals # minerals left after creating unit
		build_plan[1] -= newUnitCost.vespene # vespene left after creating unit
		build_plan[2] += newUnitCost.minerals # total mineral cost of build_plan after creating unit
		build_plan[3] += newUnitCost.vespene # total vespene cost of build_plan after creating unit
		#build_plan.append(newItem) #test
		#print(build_plan)
	if current_depth < 3: #Depth-Bounded DFS
		for unit in self.producerDict:
			#print("unit: ", unit) #debugging
			#print("build_plan: ", build_plan[2:]) #debugging
			unit1 = self._game_data.units[self.producerDict[unit][6].value]
			unitCost = self._game_data.calculate_ability_cost(unit1.creation_ability)
			#print(self._game_data.calculate_ability_cost(unit1.creation_ability))
			if unitCost.minerals <= build_plan[0] and unitCost.vespene <=  build_plan[1]:
				heuristic_score += self.producerDict[unit][5]
				#print(heuristic_score) #debugging
				#print(unit1) #debugging
				bad_search(self, build_plan + [unit], heuristic_score+int(self.producerDict[unit][5]), self.producerDict[unit][6], current_depth+1)
	#print("build_plan: ", build_plan[2:]) #debugging
	if heuristic_score > self.heuristic_high_score:
		#print("NEW HIGH SCORE REACHED")
		#print("bad_search build_plan: ", build_plan)
		#print("bad_search heuristic_score: ", heuristic_score)
		self.BOSS_Build_Order.clear()
		for unit in build_plan[4:]:
			self.BOSS_Build_Order.append(unit)
		self.heuristic_high_score = heuristic_score


"""		
# WIP: GONNA KINDA CHEAT JUST SO THAT I CAN HAVE A FUNCTIONAL HEURISTICS-BASED BOT THAT DOESN'T
# JUST STUPIDLY BUY LIKE TWELVE NEXUSES JUST BECAUSE THE HEURISTIC VALUE FOR A NEXUS WAS GREATER
# THAN ALL OTHER UNITS. I'M GOING TO CREATE A SEPARATE LIST OF 1-OFF STRUCTURES/UNITS WHICH 
# WILL EACH BE INCLUDED IN THE BUILD PATH ONLY ONCE BECAUSE THEY'RE PUT INTO THE BUILD_PLAN FROM
# THEIR OWN FUNCTION. THIS WILL MAKE IT SO THAT BAD_SEARCH() IS NOT BOGGED DOWN WITH CHECKS ONLY
# REQUIRED FOR SPECIFIC UNITS/STRUCTURES.
# Thinking about this for more than, like, eight seconds has made me pretty confident that my 
# current data structures for this project just absolutely suck massive dick. Also, this isn't 
# even really B.O.S.S-esque... Time to go read more stuff I guess
"""
def only_once(self, build_plan, heuristic_score=0, newItem=None, current_depth=0, iterIndex=0):
	print("testing")#debugging
	if newItem != None:
		#print("Considering new unit for build_plan: " + newItem.name) #debugging
		newUnit = self._game_data.units[newItem.value]
		newUnitCost = self._game_data.calculate_ability_cost(newUnit.creation_ability)
		build_plan[0] -= newUnitCost.minerals # minerals left after creating unit
		build_plan[1] -= newUnitCost.vespene # vespene left after creating unit
		build_plan[2] += newUnitCost.minerals # total mineral cost of build_plan after creating unit
		build_plan[3] += newUnitCost.vespene # total vespene cost of build_plan after creating unit
	if current_depth < 3: #Depth-Bounded DFS
		while iterIndex < len(self.One_OffDict):
			#print("iterIndex: ", iterIndex) #debugging
			#print("build_plan: ", build_plan[2:]) #debugging
			print(list(self.One_OffDict.items())[iterIndex][1][6]) #debugging
			unit1 = self._game_data.units[list(self.One_OffDict.items())[iterIndex][1][6].value]
			unitCost = self._game_data.calculate_ability_cost(unit1.creation_ability)
			#print(self._game_data.calculate_ability_cost(unit1.creation_ability))
			if unitCost.minerals <= build_plan[0] and unitCost.vespene <=  build_plan[1]:
				heuristic_score += list(self.One_OffDict.items())[iterIndex][1][5]
				#print(heuristic_score) #debugging
				#print(unit1) #debugging
				only_once(self, build_plan + [list(self.One_OffDict.items())[iterIndex][0]], heuristic_score+int(list(self.One_OffDict.items())[iterIndex][1][5]), list(self.One_OffDict.items())[iterIndex][1][6], current_depth+1, iterIndex+1)
			iterIndex += 1
		for unit in self.producerDict:
			#print("unit: ", unit) #debugging
			#print("build_plan: ", build_plan[2:]) #debugging
			unit1 = self._game_data.units[self.producerDict[unit][6].value]
			unitCost = self._game_data.calculate_ability_cost(unit1.creation_ability)
			#print(self._game_data.calculate_ability_cost(unit1.creation_ability))
			if unitCost.minerals <= build_plan[0] and unitCost.vespene <=  build_plan[1]:
				heuristic_score += self.producerDict[unit][5]
				#print(heuristic_score) #debugging
				#print(unit1) #debugging
				bad_search(self, build_plan + [unit], heuristic_score+int(self.producerDict[unit][5]), self.producerDict[unit][6], current_depth+1)
	#print("build_plan: ", build_plan) #debugging
	if heuristic_score > self.heuristic_high_score:
		#print("NEW HIGH SCORE REACHED")
		#print("bad_search build_plan: ", build_plan)
		#print("bad_search heuristic_score: ", heuristic_score)
		self.BOSS_Build_Order.clear()
		for unit in build_plan[4:]:
			self.BOSS_Build_Order.append(unit)
		self.heuristic_high_score = heuristic_score





# GONNA TRY TO JUST LITERALLY COPY THE FUNCTIONS FROM D. CHURCHILL'S FAMOUS PAPER AND THEN MAYBE MODIFY
# THEM AFTERWARDS

"""
def Sim(self, time):
	


















"""


















		