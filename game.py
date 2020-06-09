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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1920

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

ANGLE = 45
STEP = 1
BASE_LINE_LENGTH = 150
LINE_DIVIDER = math.sqrt(2)
LINE_LENGTH = BASE_LINE_LENGTH


class Car(pygame.Surface):
    direction = (0, 1)

    def __init__(self, width, height, x, y):
        super().__init__((width, height))
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.original_image.fill(COLOR_RED)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # pygame.draw.line(self.original_image, COLOR_BLUE, (int(self.rect.center[0]), int(self.rect.center[1])),
        #                 (int(self.rect.center[0]), int(self.rect.center[1] - self.rect.center[1] / 10)))
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
        car.rotate(-ANGLE)
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


def check_crash():
    """ Check if car's coordinates collided with one of a terrain's. This works only for STEP = 1
    as it verifies only the border of the object"""
    for elem in terrain:
        if elem.rect.colliderect(car.rect):
            print("Crashed -> ")
            pygame.quit()


def degrees_to_direction(deg, offset):
    global LINE_LENGTH
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
        print(LINE_LENGTH)
        return (offset, offset)


#############
# INIT GAME #
#############
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
# for setting FPS
clock = pygame.time.Clock()

car = Car(CARDIM_WIDTH, CARDIM_HEIGHT, STARTPOINT_X, STARTPOINT_Y)
# terrain = generate_terrain(30)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                print("Center: " + str(car.rect.center[0]) + " " + str(car.rect.center[1]) + "\nEndpoint: " + str(
                    car.rect.center[0] + car.direction[0] * LINE_LENGTH) + " " + str(
                    car.rect.center[1] + car.direction[1] * LINE_LENGTH))
                # car.rect.center = np.subtract(car.rect.center, (STEP, 0))
                frame_action(1)
            elif event.key == pygame.K_RIGHT:
                print("Center: " + str(car.rect.center[0]) + " " + str(car.rect.center[1]) + "\nEndpoint: " + str(
                    car.rect.center[0] + car.direction[0] * LINE_LENGTH) + " " + str(
                    car.rect.center[1] + car.direction[1] * LINE_LENGTH))
                # car.rect.center = np.subtract(car.rect.center, (-STEP, 0))
                frame_action(2)

    # if it >= 1:
    car.move_forward()
    # it += -1
    # pygame.time.wait(10)
    screen.fill(COLOR_BLACK)
    screen.blit(car.image, car.rect)
    pygame.draw.line(screen, COLOR_BLUE, (int(car.rect.center[0]), int(car.rect.center[1])),
                     (int(car.rect.center[0] + car.direction[0] * LINE_LENGTH),
                      int(car.rect.center[1] + car.direction[1] * LINE_LENGTH)))

    # https://stackoverflow.com/questions/14842090/rotate-line-around-center-point-given-two-vertices
    x = car.rect.center[0] + car.direction[0] * LINE_LENGTH
    y = car.rect.center[1] + car.direction[1] * LINE_LENGTH
    cx = car.rect.center[0]
    cy = car.rect.center[1]
    tetha = ANGLE
    xp = ((x - cx) * math.cos(math.radians(tetha)) + (y - cy) * math.sin(math.radians(tetha))) + cx
    yp = (-(x - cx) * math.sin(math.radians(tetha)) + (y - cy) * math.cos(math.radians(tetha))) + cy
    pygame.draw.line(screen, COLOR_GREEN, (int(car.rect.center[0]), int(car.rect.center[1])),
                     (int(xp), int(yp)))

    tetha = 360 - ANGLE
    xp = ((x - cx) * math.cos(math.radians(tetha)) + (y - cy) * math.sin(math.radians(tetha))) + cx
    yp = (-(x - cx) * math.sin(math.radians(tetha)) + (y - cy) * math.cos(math.radians(tetha))) + cy
    pygame.draw.line(screen, COLOR_WHITE, (int(car.rect.center[0]), int(car.rect.center[1])),
                     (int(xp), int(yp)))

    # for elem in terrain:
    #     screen.blit(elem.image, elem.rect)
    pygame.display.flip()
    pygame.event.pump()
    clock.tick(FPS)
    # check_crash()
