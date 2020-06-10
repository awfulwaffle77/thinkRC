import pygame
import operator
import random
import math
import time
import sys
import numpy as np

# COLOR DEFINITIONS
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)

# SCREEN SIZE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

FPS = 60

# CAR DIM & COORDS
STARTPOINT_X = 200
STARTPOINT_Y = 150

CARDIM_TopRight = 50
CARDIM_BottomLeft = 50

CARDIM_HEIGHT = 50
CARDIM_WIDTH = 50

CAR_X = STARTPOINT_X
CAR_Y = STARTPOINT_Y

# MISC
ANGLE = 45
STEP = 1
VELOCITY = STEP
BASE_LINE_LENGTH = 150
LINE_DIVIDER = math.sqrt(2)  # SEEMS TO WORK. HYPOTENUSE?
LINE_LENGTH = BASE_LINE_LENGTH


class Car(pygame.Surface):
    direction = (1, 0)
    sensors = []

    def __init__(self, width, height, x, y):
        super().__init__((width, height))
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.original_image.fill(COLOR_RED)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # self.center = (float(x), float(y))
        self.angle = 0

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.angle += angle % 360
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def move_forward(self):
        self.direction = degrees_to_direction(self.angle % 360, STEP)
        self.rect.center = tuple(map(operator.add, degrees_to_direction(self.angle % 360, STEP), self.rect.center))

        # Some version 0.0.1 implementation of 30 deg rotation. Until further updates, this does not work.
        # TO ADD IF WORKING WITH 30 DEGREES
        # self.center = tuple(map(operator.add, degrees_to_direction(self.angle % 360, STEP), self.center))
        # self.rect.center = self.center


class Sensor:
    def __init__(self, startpoint_x, startpoint_y, endpoint_x, endpoint_y, angle):
        self.sp_x = startpoint_x
        self.sp_y = startpoint_y
        self.ep_x = endpoint_x
        self.ep_y = endpoint_y
        self.angle = angle


class Terrain(pygame.Surface):
    def __init__(self, width, height, x, y):
        super(Terrain, self).__init__((width, height))
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.original_image.fill(COLOR_WHITE)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        print("Generated terrain")


def frame_action(action):
    if action == 0:
        return
    elif action == 1:
        car.rotate(ANGLE)
        print(car.angle % 360)
        print(car.direction)
    elif action == 2:
        car.rotate(360-ANGLE)
        print(car.angle % 360)
        print(car.direction)


def generate_terrain(elem_number):
    terrain_list = []
    for i in range(elem_number):
        terrain_x = -1
        terrain_y = -1
        width = np.random.randint(0, CARDIM_HEIGHT * 2)
        height = np.random.randint(0, CARDIM_HEIGHT * 2)
        # height = CARDIM_HEIGHT
        while terrain_x < 0 or STARTPOINT_X - CARDIM_WIDTH // 2 < terrain_x + width // 2 < STARTPOINT_X + CARDIM_WIDTH // 2 \
                or STARTPOINT_X - CARDIM_WIDTH // 2 < terrain_x - width // 2 < STARTPOINT_X + CARDIM_WIDTH // 2:  # DO NOT GENERATE OVER THE CAR
            terrain_x = np.random.randint(SCREEN_WIDTH)
        while terrain_y < 0 or STARTPOINT_Y - CARDIM_HEIGHT // 2 < terrain_y + height // 2 < STARTPOINT_Y + CARDIM_HEIGHT // 2 \
                or STARTPOINT_Y - CARDIM_HEIGHT // 2 < terrain_y - height // 2 < STARTPOINT_Y + CARDIM_HEIGHT // 2:
            terrain_y = np.random.randint(SCREEN_HEIGHT)

        terrain_list.append(Terrain(width, height, terrain_x, terrain_y))
    return terrain_list


def create_sensors():
    """ Creates facing direction sensor and creates 2 sensors at 45 degrees from facing direction """
    # Props to:
    # https://stackoverflow.com/questions/14842090/rotate-line-around-center-point-given-two-vertices
    sensors = []

    x = car.rect.center[0] + car.direction[0] * LINE_LENGTH
    y = car.rect.center[1] + car.direction[1] * LINE_LENGTH
    cx = car.rect.center[0]
    cy = car.rect.center[1]
    for tetha in [0, ANGLE, 360 - ANGLE]:
        xp, yp = calc_rotated_line(x, y, cx, cy, tetha)
        sensors.append(Sensor(x, y, xp, yp, tetha))

    return sensors


def calc_rotated_line(x, y, cx, cy, tetha):
    """ Rotates line around center (cx, cy) with angle tetha, knowing its end points (x, y) """
    xp = ((x - cx) * math.cos(math.radians(tetha)) + (y - cy) * math.sin(math.radians(tetha))) + cx
    yp = (-(x - cx) * math.sin(math.radians(tetha)) + (y - cy) * math.cos(math.radians(tetha))) + cy
    return xp, yp


def update_sensors():
    for sensor in car.sensors:
        x = car.rect.center[0] + car.direction[0] * LINE_LENGTH  # x, y are coordinates of the endpoint of line in facing dir
        y = car.rect.center[1] + car.direction[1] * LINE_LENGTH
        sensor.sp_x, sensor.sp_y = car.rect.center
        sensor.ep_x = ((x - sensor.sp_x) * math.cos(math.radians(sensor.angle)) + (y - sensor.sp_y) * math.sin(
            math.radians(sensor.angle))) + sensor.sp_x
        sensor.ep_y = (-(x - sensor.sp_x) * math.sin(math.radians(sensor.angle)) + (y - sensor.sp_y) * math.cos(
            math.radians(sensor.angle))) + sensor.sp_y


def draw_sensors():
    for sensor in car.sensors:
        pygame.draw.line(screen, COLOR_WHITE, (int(sensor.sp_x), int(sensor.sp_y)),
                         (int(sensor.ep_x), int(sensor.ep_y)))


def get_minimum_distance(distances):
    """ Goes through the array of distances and returns the first appearance that is not 0.
     If every element in array is 0, it return 0. Wonderful! """
    final_distance = 0
    for distance in distances:
        if distance > 0:
            final_distance = distance

    return final_distance


def get_current_state():
    """ Gets the array of states at instant t as stated on page 2, ecuation (1). Every value of the
    array signifies a distance to the nearest object.
    First value is sensor at tetha = 0, then ANGLE, then 360 - ANGLE """
    states = []  # array with distances
    distances = []  # distances relative to all the terrain elements

    for sensor in car.sensors:
        for elem in terrain:
            clipped = elem.rect.clipline(sensor.sp_x, sensor.sp_y, sensor.ep_x, sensor.ep_y)
            if clipped:
                start, end = clipped
                x1, y1 = start
                x2, y2 = end
                dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                distances.append(dist)
            else:
                distances.append(0)
        states.append(get_minimum_distance(distances))
        distances.clear()

    return states


def check_crash():
    """ Check if car's coordinates collided with one of a terrain's. This works only for STEP = 1
    as it verifies only the border of the object"""
    for elem in terrain:
        if elem.rect.colliderect(car.rect):
            print("Crashed -> ")
            pygame.quit()


def degrees_to_direction(deg, offset):
    """
    Returns the direction where the car should be headed, interpreting the angle.
    Only works on multiples of 45 degress.

    NOTE: Due to the fact that lines on the diagonal are
    drawed at a greater distance than those on angles multilple of 90 degress, we had to
    divide the line length when the angle was multiple of 45 """
    global LINE_LENGTH
    if ANGLE == 45:
        if deg == 0:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (offset, 0)
        elif deg == 45:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return (offset, -offset)
        elif deg == 90:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (0, -offset)
        elif deg == 135:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return (-offset, -offset)
        elif deg == 180:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (-offset, 0)
        elif deg == 225:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return (-offset, offset)
        elif deg == 270:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (0, offset)
        elif deg == 315:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return (offset, offset)
    elif ANGLE == 30:  # Does not currently work properly. The square surface goes bananaz, cause it s configured for 45
        if deg == 0:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (offset, 0)
        if deg == 30:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 30)  # Idk why there's 360 - 30 instead of 30
        elif deg == 60:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 60)
        elif deg == 90:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (0, -1)
        elif deg == 120:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 120)
        elif deg == 150:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 150)
        elif deg == 180:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (-1, 0)
        elif deg == 210:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 210)
        elif deg == 240:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 240)
        elif deg == 270:
            LINE_LENGTH = BASE_LINE_LENGTH
            return (0, 1)
        elif deg == 300:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 300)
        elif deg == 330:
            LINE_LENGTH = BASE_LINE_LENGTH / LINE_DIVIDER
            return calc_rotated_line(1, 0, 0, 0, 330)


#############
# INIT GAME #
#############
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
# for setting FPS
clock = pygame.time.Clock()

car = Car(CARDIM_WIDTH, CARDIM_HEIGHT, STARTPOINT_X, STARTPOINT_Y)
car.sensors = create_sensors()
terrain = generate_terrain(40)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                frame_action(1)
            elif event.key == pygame.K_RIGHT:
                frame_action(2)

    # if it >= 1:
    car.move_forward()
    # it += -1
    # pygame.time.wait(10)
    screen.fill(COLOR_BLACK)
    # screen.blit(car.image, car.center)  # USE THIS FOR 30 degrees
    screen.blit(car.image, car.rect)

    update_sensors()
    draw_sensors()

    for elem in terrain:
        screen.blit(elem.image, elem.rect)

    x = get_current_state()
    print(x)
    pygame.display.flip()
    pygame.event.pump()
    clock.tick(FPS)
    # check_crash()
