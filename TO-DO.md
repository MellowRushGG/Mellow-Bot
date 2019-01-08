IN: Mellow-Bot();
# TO-DO: utilize a packing algorithm (2D ball-packing?) and/or a machine learning-/B.O.S.S-based PYLON distribution scheme.

IN: Intel::Scout()
# TO-DO: GET UNIT ID OF SCOUT WORKER AND SET AN ON_UNIT_DEATH EVENT HANDLER FOR ITS DEATH

IN: BOSS above bad_search()
# TO-DO: need to create a "bar" which selected strategies must beat in order to be enacted, that way
# the NO-OPs will have value

IN: BOSS above bad_search()
# TO-DO: Fix; Optimize; Change this to recur every time the longest 
# queued action completes; Use the corrected version to replace many
# of the current Offense_Methods; Hash state to ignore searching 
# dupicates; fix the problem where the highest valued unit is just
# bought as many times as possible (IE make unit heuristic depreciate 
# if unit is already in build_plan for certain 1-off structures/units


-------------------------------------------------------------------------
THINGS I'LL PROBABLY IMPLEMENT NEXT:
-------------------------------------------------------------------------

Figure out how to hash states and shit so that I'm not lagging SC2 every time I call bad_search().

Figure out how to augment value heuristics based on info gained from scouting (or the lack thereof) 

Figure out the optimal selection process for units who will be building things

COMPLETELY REDO EVERYTHING SO THAT I GET A REPRESENTATION OF THE STATE WHICH IS MY ABILITY TO BUILD THINGS 
(ie, for each unit which can build something, add to the available_actions all the actions they can take, then 
iterate through that instead of this really kinda shitty heuristics-based version which requires me to dial in
hyperfunctions/hyperparameter












