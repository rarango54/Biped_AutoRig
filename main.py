import maya.cmds as cmds
import maya.api.OpenMaya as om2
import math

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy

def distance(obj1, obj2):
    # define vectors
    vec1 = om2.MVector(cmds.xform(obj1, q = True, t = True))
    vec2 = om2.MVector(cmds.xform(obj2, q = True, t = True))
    # subtract them
    vec = vec2 - vec1
    # calculate vector length
    dist = om2.MVector.length(vec)
    return dist
    
if __name__ == "__main__":
    
    loc = cmds.spaceLocator(n = "test")[0]
    loc2 = cmds.spaceLocator(n = "test2")[0]
    cmds.xform(loc, t = (3, 8, 4))
    cmds.xform(loc2, t = (7, -1, -3.5))
    dist_new = distance(loc, loc2)
    dist = util.get_distance(loc, loc2)
    print("new approach = ", dist_new)
    print("old approach = ", dist)
    # orig = cmds.spaceLocator(n = "origin")[0]
    # cmds.xform(loc, t = (6,2,18))
    # vec = om2.MVector((6,2,18))
    # dist = util.get_distance(orig, loc)
    # length = math.sqrt(6**2 + 2**2 + 18 **2)
    # mlen = om2.MVector.length(vec)
    # print(dist)
    # print(length)
    # print(mlen)

    pass