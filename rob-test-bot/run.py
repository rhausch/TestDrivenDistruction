import battlecode as bc
import random
import sys
import traceback
import marscontroller
import earthcontroller

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

my_team = gc.team()
if my_team == bc.Team.Red:
    opponent_team = bc.Team.Blue
else:
    opponent_team = bc.Team.Red

if gc.planet() == bc.Planet.Earth:
    controller = earthcontroller.EarthController(gc)
else:
    controller = marscontroller.MarsController(gc)

while True:
    if gc.round() % 50 == 0:
        print('RobBot:', gc.round(),
              ' Karbonite:', gc.karbonite(),
              ' Time:', gc.get_time_left_ms())
    try:
        controller.run_turn()
    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()
    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()
    sys.stdout.flush()
    sys.stderr.flush()
