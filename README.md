SC2AI Mellow-Bot Python

NOT UPDATED. THIS BOT SUCKS (but still beats me). DON'T LOOK HERE 
.
.
.
.
.
.
.
The idea was to use varying heuristic values for buildings/units every 40 seconds, 
choose the best three units, build them, and then repeat until I've either lost 
the game or won the game. If I've won the game, save the heuristic values that 
were used at each 40 seconds to a CSV file; if I've lost the game, don't. Kinda a 
random-walk approach. After I've gathered a few different "paths" (CSV files for 
won games), I'd do a genetic algorithm on them to create new CSV files and I'd 
tune their variance down. CSV files can supply as a baseline heuristic value, 
instead of just a random value generated by high-variance. For each CSV file which 
I had for input, I'd similarly run hundreds of games using the saved values as 
baseline values and then add smaller and smaller variance so that each "random walk"
would start to form a finely-tuned path (This is referred to as simulated annealing 
with a genetic algorithm). 
Unfortunately, even the easy AI has an efficiency that requires at least a basic 
early strategy which is hard to randomly stumble across when my computer can only run ~200
simulations in 7 hours.
