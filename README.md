# thinkRC
A neural network trained in pygame to be used with a real RC Car! (How original !)

## Issues

* Terrain generation overlaps with the current car position.

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
