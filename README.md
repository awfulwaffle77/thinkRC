# thinkRC
A neural network trained in pygame to be used with a real RC Car! (How original !)
## Intro



## To Do

* Random initial state (car's x, y)

* End point with random init as car

* Make terrain to not overlap with the end point

## Issues

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
