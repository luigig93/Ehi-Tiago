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

