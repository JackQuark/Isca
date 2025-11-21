# universal functions
# author: Quark
# ==================================================
import numpy     as np
# ==================================================

def lat_weights(lat, norm: bool = False):
    weights = np.cos(np.deg2rad(lat))
    if norm:
        weights = weights / weights.mean()
    return weights

def array_equal(a, b):
    if np.array_equal(a, b):
        return True
    else:
        print("Maximum err:", np.max(np.abs(a-b)))
        return False