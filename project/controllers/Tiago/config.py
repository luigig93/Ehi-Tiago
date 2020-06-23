WEBOTS_ROBOT_NAME = "tiago"

# set robot name/parameters
HEAD_RL = "head_1_joint"
HEAD_UD = "head_2_joint"
TORSO_LIFT = "torso_lift_joint"

HEAD_RL_SENSOR = "head_1_joint_sensor"
HEAD_UD_SENSOR = "head_2_joint_sensor"
TORSO_LIFT_SENSOR = "torso_lift_joint_sensor"

LEFT_WHEEL_MOTOR = "wheel_left_joint"
RIGHT_WHEEL_MOTOR = "wheel_right_joint"
LEFT_WHEEL_SENSOR = "wheel_left_joint_sensor"
RIGHT_WHEEL_SENSOR = "wheel_right_joint_sensor"
MAX_SPEED = 6.4 # rad/s
MIN_SPEED = 0.5 # rad/s
CRUISE_SPEED = 3.0 # rad/s
NULL_SPEED = 0.0
HALF_SPEED = 3.2 # rad/s
INFINITY = float('+inf')
EXIT_SUCCESS = 0
CLOCK_WISE = 1
COUNTER_CLOCK_WISE = -1
TURNING_SPEED = 1

# sensors test
GPS_SENSOR = "test_gps"
CAMERA_SENSOR = "my_smart_camera"
INERTIAL_UNIT = "inertial unit"
RECEIVER = "bluetooth"

#ERRORS
DIST_ERROR = 0.3  # for stop condition 1
COORDINATE_ERROR = 0 # for stop condition 2
NAV_ERROR = 0.2 # for stop condition 0
DOOR_ERROR = 0.1 # for stop condizion 0

# Beacons placement
NUM_OF_BEACONS = 16
ADVERT_INTERVAL = 352  # min 100ms -> max 1000ms
# per comodità dare le coordinate nel formato (x, z) così diventa più leggibile su webots
BEACONS_POS_DICT = {
        "B0":  (0, 0),   "B1":  (0, 4),   "B2":  (0, 10),   "B3": (0, 12.5),
        "B4":  (3.5, 12.5),
        "B5":  (6, 0),   "B6":  (6, 4),   "B7":  (6, 10),
        "B8":  (8.5, 0), "B9":  (8.5, 3), "B10": (8.5, 5.5), "B11": (8.5, 10),
        "B12": (13, 0),  "B13": (13, 3),  "B14": (13, 5.5),  "B15": (13, 10),
    }


# door opening system
NUM_OF_DOORS = 7
DOOR_OPENING_FIELD = "position"
DOOR_OPENING_SIDE = {
        "D0": 3,
        "D1": -3,
        "D2": 3,
        "D3": 3,
        "D4": -3,
        "D5": 3,
        "D6": -3,
        "D7": 3,
}


# search module
ID_TO_TAG = {

"L0": "kitchen-fridge",
"L1": "kitchen-table",
"L2": "kitchen-cabinet",
"L3": "livingroom-cabinet2",
"L4": "livingroom-table",
"L5": "livingroom-cabinet1",
"L6": "livingroom-couch",
"L7": "storage-cabinet",
"L8": "storage-desk",
"L9": "smallbedroom-cabinet",
"L10": "smallbedroom-bed",
"L11": "bathroom-cabinet",
"L12": "bathroom-washingmachine",
"L13": "bedroom-desk",
"L14": "bedroom-bed",
"L15": "bedroom-cabinet",
"L16": "outdoor-trashbin"

}


TAG_TO_ID = {v: k for k, v in ID_TO_TAG.items()}


HOME_OBJECTS = {

        "L0": [],
        "L1": ["banana",],
        "L2": [],
        "L3": [],
        "L4": [],
        "L5": [],
        "L6": [],
        "L7": [],
        "L8": [],
        "L9": [],
        "L10": [],
        "L11": [],
        "L12": [],
        "L13": [],
        "L14": [],
        "L15": [],
        "L16": []

}
