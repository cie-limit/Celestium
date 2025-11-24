import numpy as np

def get_earth_moon_positions(days_from_now=0):
    moon_dist = 384400
    period = 27.3
    omega = 2 * np.pi / period
    theta = omega * days_from_now
    
    earth_pos = np.array([0.0, 0.0, 0.0])
    moon_pos = np.array([
        moon_dist * np.cos(theta),
        moon_dist * np.sin(theta),
        0.0
    ])
    return earth_pos, moon_pos
