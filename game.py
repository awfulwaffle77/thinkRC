import pygame
import operator
import keras
from definitions import *
import DRL
import math
import sys
import numpy as np


def define_parameters():
    params = dict()
    params['discount_factor'] = DISCOUNT_FACTOR
    params['learning_rate'] = LEARNING_RATE
    params['first_layer_size'] = 500  # neurons in the first layer
    params['second_layer_size'] = 500  # neurons in the second layer
    params['third_layer_size'] = 500  # neurons in the third layer
    params['episodes'] = EPISODES
    params['memory_size'] = 5000 # orignially 2500
    params['batch_size'] = 2000 # originally 500p
    params['weights_path'] = WEIGHTS_PATH
    params['load_weights'] = LOAD_WEIGHTS
    params['train'] = TRAIN
    return params


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


class Endpoint(pygame.Surface):
    def __init__(self, width, height, endpoint_x, endpoint_y):
        super(Endpoint, self).__init__((width, height))
        self.original_image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.original_image.fill(COLOR_GREEN)
        self.image = self.original_image
        self.rect = self.image.get_rect()

        x = -1
        y = -1
        width = self.width
        height = self.height

        # for elem in terrain:
        #     while x < 0 or y < 0 or elem.rect.colliderect(x, y, width, height):
        #         x = np.random.randint(SCREEN_WIDTH)
        #         y = np.random.randint(SCREEN_HEIGHT)

        self.rect.center = (endpoint_x, endpoint_y)


def is_safe_state(state):
    """ state is a list(array) of 3 floats, representing distances recorded by the 3 sensors """
    for st in state:
        if st < MIN_SAFE_DISTANCE: # if at least one sensor detects this
            return False  # it is a non-safe state
    return True


def check_got_closer(old_state, current_state):
    """ Check if in this state, car got closer to object. It will check if any of the distances got lower. """
    for i in range(len(car.sensors)):  # should be 3 sensors
        if current_state[i] <= old_state[i]:
            return True  # car got closer to object
    return False


def check_win():
    if car.rect.colliderect(endpoint.rect):
        return True
    return False


def get_reward(old_state, current_state):
    if check_win():
        return WINNING_STATE
    if check_crash():
        return FAILURE_STATE
    # Moving from Non-Safe State
    if not is_safe_state(old_state):
        # to Safe State
        if is_safe_state(current_state):
            return NONSAFE_TO_SAFE
        # to Non-Safe, getting closer
        elif check_got_closer(old_state, current_state):
            return NONSAFE_TO_NONSAFE_CLOSER
        # to Non-Safe, getting farther
        else:
            return NONSAFE_TO_NONSAFE_FARTHER
    # Moving from Safe State
    else:
        # to Safe State
        if is_safe_state(current_state):
            return SAFE_TO_SAFE
        # to Non-Safe State
        else:
            return SAFE_TO_NONSAFE


def frame_action(action):
    car.move_forward()
    if action == 0:
        return
    elif action == 1:
        car.rotate(ANGLE)
    elif action == 2:
        car.rotate(360 - ANGLE)


def generate_terrain(elem_number):
    terrain_list = []
    margins = create_margins()
    for margin in margins:
        terrain_list.append(margin)

    for i in range(elem_number):
        terrain_x = -1
        terrain_y = -1
        width = np.random.randint(0, CARDIM_HEIGHT * 2)
        height = np.random.randint(0, CARDIM_HEIGHT * 2)

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
        x = car.rect.center[0] + car.direction[0] * LINE_LENGTH
        # x, y are coordinates of the endpoint of line in facing dir
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
    """ Goes through the array of distances and returns the first appearance that is not 0 or DISTANCE_INF. """
    final_distance = DISTANCE_INF
    for distance in distances:
        if distance > 0 and distance != DISTANCE_INF:
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
                x1, y1 = start  # Where the lines start intersecting
                x2, y2 = sensor.sp_x, sensor.sp_y
                dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                distances.append(dist)
            else:
                distances.append(DISTANCE_INF)
        states.append(get_minimum_distance(distances))
        distances.clear()

    return states


def create_margins():
    """ Creates the borders of the playzone """
    border_top = Terrain(SCREEN_WIDTH, BORDER_WEIGHT, SCREEN_WIDTH // 2, 0)
    border_left = Terrain(BORDER_WEIGHT, SCREEN_HEIGHT, 0, SCREEN_HEIGHT // 2)
    border_bottom = Terrain(SCREEN_WIDTH, BORDER_WEIGHT, SCREEN_WIDTH // 2, SCREEN_HEIGHT)
    border_right = Terrain(BORDER_WEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT // 2)

    return border_top, border_left, border_bottom, border_right


def crash():  # What happens in case of crash
    print("I have a crash on u <3")


def reinit_car_position():
    # while True:
    #     x = np.random.randint(SCREEN_WIDTH)
    #     y = np.random.randint(SCREEN_HEIGHT)
    #     car.rect.center = (x, y)
    #     if not check_crash():  # if car isn't in a crash position
    #         break
    car.rect.center = (STARTPOINT_X, STARTPOINT_Y)


def check_crash(skip_reinit=False):
    """ Check if car's coordinates collided with one of a terrain's."""
    for elem in terrain:
        if elem.rect.colliderect(car.rect) and elem != endpoint:
            return True  # car has crashed
    return False


def save_coords():
    """ Saves coordinates in the specified file """
    f = open(COORDS_PATH, "w")
    idx = 0
    for elem in terrain:
        f.write("Terrain " + str(idx) + str(": ") + str(elem.rect.center) + "\n")
        idx += 1

    f.write("Endpoint: " + str(endpoint.rect.center) + '\n')
    f.write("Rewards: \n" + " NONSAFE_TO_SAFE: " + str(NONSAFE_TO_SAFE) + "\n")
    f.write("SAFE_TO_NONSAFE: " + str(SAFE_TO_NONSAFE) + "\n")
    f.write("SAFE_TO_SAFE: " + str(SAFE_TO_SAFE) + "\n")
    f.write("NONSAFE_TO_NONSAFE_CLOSER: " + str(NONSAFE_TO_NONSAFE_CLOSER) + "\n")
    f.write("NONSAFE_TO_NONSAFE_FARTHER: " + str(NONSAFE_TO_NONSAFE_FARTHER) + "\n")
    f.write("WINNING_STATE: " + str(WINNING_STATE) + "\n")
    f.write("FAILURE_STATE: " + str(FAILURE_STATE) + "\n")


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


def get_reward_relative_to_endpoint(old_car, current_car): # i need the car pos, not sensors
    """ Gets a reward if car came closer/farther from endpoint """
    endpoint_coords = endpoint.rect.center
    old_distance = math.sqrt((old_car[0]-endpoint_coords[0])**2 + (old_car[1] - endpoint_coords[1])**2)
    current_distance = math.sqrt((current_car[0]-endpoint_coords[0])**2 + (current_car[1] - endpoint_coords[1])**2)

    if old_distance < current_distance: # if car got farther away
        return FARTHER_FROM_ENDPOINT
    else:
        return CLOSER_TO_ENDPOINT


def run():
    printReward = 0
    weights_filepath = params['weights_path']
    if params['load_weights']:
        agent.model.load_weights(weights_filepath)
        print("weights loaded")

    game_counter = 0
    while game_counter < params['episodes']:
        current_steps = 0
        print("Reinitted car pos")
        reinit_car_position()
        print("Episode: " + str(game_counter))
        while current_steps < MAX_STEPS and not check_crash() and not check_win():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if params['train']:
                        agent.model.save_weights(params['weights_path'])
                        save_coords()
                    pygame.quit()
                    sys.exit()

            if current_steps == 0: # If it is the first step in the episode
                frame_action(np.random.randint(2)) # take a random action

            if not params['train']:
                agent.epsilon = 0
            else:
                # agent.epsilon is set to give randomness to actions
                # it will decrease as episodes increase
                agent.epsilon = 1 - (game_counter * DISCOUNT_FACTOR)

            old_state = get_current_state()
            old_car = car.rect.center

            # As episodes increase, the random action will be chosen less and less
            randEps = np.random.random()
            if randEps < agent.epsilon:
                # take a random action between 0 and 2
                final_move = keras.utils.to_categorical(np.random.randint(2), num_classes=3)
            else:
                # predict action based on the old state
                prediction = agent.model.predict(np.reshape(old_state, (1, 3)))
                final_move = keras.utils.to_categorical(np.argmax(prediction[0]), num_classes=3)

            frame_action(np.argmax(final_move))
            new_state = get_current_state()
            current_car = car.rect.center

            # even though there should be no reward in distance relative to endpoint(because the sensors do not know
            # where the endpoint is
            reward = get_reward(old_state, new_state) + get_reward_relative_to_endpoint(old_car, current_car)
            printReward += reward

            if params['train']:
                done = check_crash()
                # train short memory base on the new action and state
                agent.train_short_memory(old_state, final_move, reward, new_state, done)
                # store the new data into a long term memory
                agent.remember(old_state, final_move, reward, new_state, done)

            ## DISPLAYING CAR
            screen.fill(COLOR_BLACK)
            # screen.blit(car.image, car.center)  # USE THIS FOR 30 degrees
            # DISABLED FOR QUICKED TRAIN
            screen.blit(car.image, car.rect)
            screen.blit(endpoint.image, endpoint.rect)

            update_sensors()
            draw_sensors()

            for elem in terrain:
                screen.blit(elem.image, elem.rect)

            pygame.display.flip()
            pygame.event.pump()
            clock.tick(FPS)
            if check_crash():
                print("I crashed")

            current_steps += 1
            if current_steps % 100 == 0:
                print(current_steps)
                print(printReward)

        if params['train']:
            agent.replay_new(agent.memory, params['batch_size'])

        if params['train']:
            agent.model.save_weights(params['weights_path'])
            save_coords()

        game_counter += 1


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    # for setting FPS
    clock = pygame.time.Clock()

    params = define_parameters()
    agent = DRL.DRLAgent(params)

    car = Car(CARDIM_WIDTH, CARDIM_HEIGHT, STARTPOINT_X, STARTPOINT_Y)
    car.sensors = create_sensors()
    terrain = generate_terrain(5)
    endpoint = Endpoint(CARDIM_WIDTH, CARDIM_HEIGHT, ENDPOINT_COORDS_X, ENDPOINT_COORDS_Y)
    # terrain.append(endpoint) # Will not consider the endpoint as terrain

    run()
