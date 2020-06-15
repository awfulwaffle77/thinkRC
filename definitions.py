import math

# DRL PARAMETERS
LOAD_WEIGHTS = False
EPISODES = 1000
MAX_STEPS = 1000 # Max steps per episode
TRAIN = True
WEIGHTS_PATH = 'weights/w2.hdf5'
COORDS_PATH = 'coords/c2.txt'
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.15
MAX_TEMP = 0.8
MIN_TEMP = 0.01

# COLOR DEFINITIONS
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)

# SCREEN SIZE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BORDER_WEIGHT = 3

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

# REWARDS
NONSAFE_TO_SAFE = 2
SAFE_TO_NONSAFE = -10
SAFE_TO_SAFE = -0.4
NONSAFE_TO_NONSAFE_CLOSER = -8
NONSAFE_TO_NONSAFE_FARTHER = 2
WINNING_STATE = 40
FAILURE_STATE = -30

# STATE PARAMETERS
MIN_SAFE_DISTANCE = 100

# MISC
DISTANCE_INF = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 2
ANGLE = 45
STEP = 1
VELOCITY = STEP
BASE_LINE_LENGTH = 150
LINE_DIVIDER = math.sqrt(2)  # SEEMS TO WORK. HYPOTENUSE?
LINE_LENGTH = BASE_LINE_LENGTH
