import csv, subprocess
from subprocess import *
import os
from os import system

"""
file_name = 'SC2AI'
producerDictFieldNames = ['workers', 'assimilators', 'nexuses', 'pylons', 'gateways', 'cybernetics cores', 'stalkers', 'voidrays']
write_file_name = file_name + "3" + '.csv'
appending_file = open(write_file_name, 'a')
csv_writer = csv.DictWriter(appending_file, producerDictFieldNames)
EOFDict = {'workers' : '!', 'assimilators' : '!', 'nexuses' : '!','pylons' : '!','gateways' : '!','cybernetics cores' : '!','stalkers' : '!', 'voidrays' : '!'}
csv_writer.writerow(EOFDict)
"""

def run_ML_game(a,b):
	procString = "py Mellow-Bot.py " + str(a) + " " + str(b)
	result = ""
	proc = subprocess.Popen(procString, stdout=subprocess.PIPE)
	#proc.communicate(str(a) + " " + str(b)) 
	outStr = ""
	try:
		outs, errs = proc.communicate(timeout=2400) #40 minute game
		outStr += str(outs)
	except subprocess.TimeoutExpired:
		proc.kill()
		outs, errs = proc.communicate(timeout=3)
		outStr += str(outs)
		
	#print(outStr)
	outString = str(outStr)
	#print(outString[-1])
	if outString[-2] == "2":
		print("you suck (LOSS)")
		result = "LOSS"
		pathStr = r"C:\\Users\\Myles\\Desktop\\SC2AI Mellow-Bot Python\\SC2AI Mellow-Bot Python\\SC2AI" + str(b) + ".csv"
		if os.path.exists(pathStr):
			os.remove(pathStr)
			print("deleting SC2AI" + str(b) + ".csv")
	elif outString[-2] == "1":
		print("HOLY SHIT WE FUCKING WON A GAME")
		result = "WIN"
	print(outString[-2])
	return result


write_file_n = "won_games.txt"
f = open(write_file_n, 'w')
for i in range(3, 1300):
	ML_result = run_ML_game(0,i)
	if ML_result == "WIN":
		f.write("Won game: ", i)
		#save the heuristics

		
		
f.close()