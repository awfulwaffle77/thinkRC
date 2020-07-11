# thinkRC
A neural network trained in pygame to be used with a real RC Car! (How original !)
## Intro


## What I did to fix the problem

* Added `old_state[i] != DISTANCE_INF` in function `check_got_closer` so that
it should not get the reward if it switches from a no-object-detected state.
Does not seem to work, but I'll let that there.

* I am implementing a function that tracks wether the car gets closer or farther
from the endpoint. This is not how it should function in real life but I will reward
it if it comes closer and punish it harshly if it goes farther(with something like
3*getting closer reward). Edit: It worked early, making the car alternate rewards
a bit, but it still spins the head right round right round.

* Changed from `output_dim` to `units` in `network` function. It seemed to work 
a bit but then it changed to going straight.

* Set minimum safe distance to line length and set the reward for going with the same
distance the same as getting closer to avoid going in a straight line


## To Do

* Make the car and endpoint have the same initial coords and
do not reset the car coords after a crash, but reset the environment,
and see how that works

* Fix loading weights failure

* ~~Random initial state (car's x, y)~~

* ~~End point with random init as car~~

* ~~Make terrain to not overlap with the end point~~

## Issues

* Exploits the game by going forward to safe states

* Had a problem using np.random.randint(0,1), where this returned only 1(obviously).
Using np.random.random()

* ~~Distance sensors do not work properly in function `get_current_state()`.~~ Fixed by changing the end points in function 

* ~~Terrain generation overlaps with the current car position.~~ Seems to have been fixed?

* ~~Screwed it up and now the startpoint of the sensors is topleft. Whaaat?~~ Fixed by blitting by car.rect

* ~~Center of rect when rotating is also screwed.~~ Fixed by blitting by car.rect

## Not-so-important issues (a.k.a. Feature to implement)
* Rotating the car to multiple of 30's degrees surely work, but need 
some work when redrawing sensors. As I see it, implementing this with PyGame
is a bad idea due to the fact that the Rect and Surfaces store their coordinates as
int, and not as floats, leading to discrepancies in calculus. *NOTE: decomment code in move_forward, in loop and 
maybe the self.center property in class Car to test it further.*

## First steps
Creating a pygame to simulate the real environment.

The current state should be represented by the distances recorded by the sensors
and not also by the current position. Knowing the position is easy in the simulated
environment, but in reality, there is no way to check position. 

The current crash checking does not also apply in reality. I do not know how to
implement it in reality. Maybe with a collision sensor. 
