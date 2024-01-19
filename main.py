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
    
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[0].value_Interp", 3)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[1].value_Interp", 3)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[2].value_FloatValue", 0.075)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[2].value_Position", 0.3)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[2].value_Interp", 3)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[3].value_FloatValue", 0.25)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[3].value_Position", 0.6)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[3].value_Interp", 3)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[4].value_FloatValue", 0.6)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[4].value_Position", 0.85)
    cmds.setAttr("L_uporb_main_macro1_uplid_up_RMV.value[4].value_Interp", 1)

    pass