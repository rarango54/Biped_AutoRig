import maya.cmds as cmds

from face_proxies.proxyteeth import ProxyTeeth

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Teeth(object):
    
    def __init__(self, joint_socket, ctrl_socket):

        self.module_name = "teeth"
        
        self.upmain_jnt = "upteeth_JNT"
        self.upmain = "upteeth_CTRL"
        
        self.lowmain_jnt = "lowteeth_JNT"
        self.lowmain = "lowteeth_CTRL"
        
        self.teeth_ctrls = [self.upmain, self.lowmain]
    
    def skeleton(self, joint_socket, proxies):
        rad = cmds.getAttr("jaw_JNT.radius")
        teeth_jnts = rig.make_joints(
                proxies_list = proxies,
                rot_order = "zyx", 
                radius = rad/2,
                set = "fjoints")
        cmds.parent(teeth_jnts[0], joint_socket)
        cmds.joint(teeth_jnts[1], e = True, 
                   orientJoint = "zyx",
                   secondaryAxisOrient = "yup",
                   children = True,)
    # noInvScale = True
        for j in teeth_jnts:
            child = cmds.listRelatives(j, children = True)
            if child:
                cmds.disconnectAttr(j+".scale", child[0]+".inverseScale")
        mirr_jnts = cmds.mirrorJoint(
            teeth_jnts[1], mirrorYZ = True, 
            mirrorBehavior = True, 
            searchReplace = ["L_", "R_"])
        teeth_jnts.extend(mirr_jnts)
        cmds.sets(teeth_jnts, add = "teeth_joints")
        return teeth_jnts
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, joint):
        size = cmds.getAttr(joint+".radius")
    ### CTRL SHAPES
        main = Nurbs.box(joint.replace("JNT", "CTRL"), 
                         size*4, size, size, "brown", "zyx")
        cmds.matchTransform(main, joint, pos = True, rot = True)
    # buffers
        buff = util.buffer(main)
        cmds.parent(buff, ctrl_socket)
####### Attributes
        util.attr_separator(main)
        attr_dict = {
            main : ["bend", "L_bend", "R_bend", "spread", "L_spread", "R_spread" ]}
        for ctrl in attr_dict.keys():
            for attr in attr_dict[ctrl]:
                cmds.addAttr(ctrl, longName = attr, attributeType = "double")
                cmds.setAttr(f"{ctrl}.{attr}", e = True, keyable = True)
    # selection sets
        cmds.sets(main, add = "mouth")
    # cleanup
        util.mtx_zero([buff, main])
        return main
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket):
        pteeth = ProxyTeeth()
        cmds.sets(n = "teeth_joints")
        upjnts = self.skeleton(joint_socket, pteeth.upprx)
        lowjnts = self.skeleton("jaw_JNT", pteeth.lowprx)
        upctrl = self.controls("jaw_inverse_CTRL", self.upmain_jnt)
        lowctrl = self.controls("jaw_FK_CTRL", self.lowmain_jnt)
    # connect joint to ctrls
        for part in ["upteeth", "lowteeth"]:
            cmds.parentConstraint(f"{part}_CTRL", f"{part}_JNT", mo = True, w = 1,
                                  n = f"{part}_ctrl_PC")
            cmds.scaleConstraint(f"{part}_CTRL", f"{part}_JNT", o = (1,1,1), w = 1,
                                 n = f"{part}_ctrl_SCL")
        for jnts in [upjnts[1:], lowjnts[1:]]:
            part = jnts[0].split("_")[1] # upteeth or lowteeth
            ctrl = f"{part}_CTRL"
            # add ctrl attrs
            for attr in ["bend", "spread"]:
                left = "L_"+attr
                right = "R_"+attr
                leftadd = cmds.shadingNode("addDoubleLinear", 
                                           n = f"{part}_{left}_ADD", au = True)
                cmds.connectAttr(f"{part}_CTRL.{attr}", leftadd+".input1")
                cmds.connectAttr(f"{part}_CTRL.{left}", leftadd+".input2")
                rightadd = cmds.shadingNode("addDoubleLinear", 
                                           n = f"{part}_{right}_ADD", au = True)
                cmds.connectAttr(f"{part}_CTRL.{attr}", rightadd+".input1")
                cmds.connectAttr(f"{part}_CTRL.{right}", rightadd+".input2")
            # connect to joints
            for jnt in jnts:
                if jnt.startswith("L_"):
                    cmds.connectAttr(f"{part}_L_bend_ADD.output", jnt+".rx")
                    cmds.connectAttr(f"{part}_L_spread_ADD.output", jnt+".ry")
                else:
                    cmds.connectAttr(f"{part}_R_bend_ADD.output", jnt+".rx")
                    cmds.connectAttr(f"{part}_R_spread_ADD.output", jnt+".ry")
                    
    ### clean up attributes - lock & hide
        # util.lock([self.inner, self.main, self.bone], 
        #           ["sx","sy","sz"], rsidetoo = True)

### missing:

if __name__ == "__main__":
    for name in ["head_JNT", "jaw_JNT"]:
        cmds.joint(n = name)
        cmds.select(clear = True)
    test = Teeth()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL",
        lipcorners = ["L_lipcorner_macroOut_GRP", 
                      "R_lipcorner_macroOut_GRP"])
    cmds.hide("proxy_test_GRP")
    pass