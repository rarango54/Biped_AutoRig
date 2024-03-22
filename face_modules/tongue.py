import maya.cmds as cmds

from face_proxies.proxytongue import ProxyTongue

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy

class Tongue(object):
    
    def __init__(self, joint_socket, ctrl_socket):

        self.module_name = "tongue"
        
        self.base_jnt = "tongue_base_JNT"
        
        self.base = "tongue_base_CTRL"
        self.mid = "tongue_mid_CTRL"
        self.tip = "tongue_tip_CTRL"
        
        self.tongue_ctrls = [self.base, self.mid, self.tip]
    
    def skeleton(self, joint_socket):
        ptongue = ProxyTongue()
        
        tongue_jnts = rig.make_joints(
                proxies_list = ptongue.proxies,
                rot_order = "yzx", 
                radius = 0.8,
                set = "fjoints")
        cmds.parent(tongue_jnts[0], joint_socket)
        # cmds.parent(tongue_jnts[0], joint_socket, noInvScale = True)
        cmds.joint(tongue_jnts[0], e = True, 
                   orientJoint = "zxy",
                   secondaryAxisOrient = "xup",
                   children = True,)
        cmds.joint(tongue_jnts[-1], e = True, 
                   orientJoint = "none")
    # noInvScale = True
        # for j in tongue_jnts:
            # child = cmds.listRelatives(j, children = True)
            # if child:
            #     cmds.disconnectAttr(j+".scale", child[0]+".inverseScale")
        cmds.sets(tongue_jnts, add = "tongue_joints")
        return tongue_jnts
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        ptongue = ProxyTongue()
        ro = "yzx"
        dist = util.distance(ptongue.base, ptongue.tip)
    ### CTRL SHAPES
        base = Nurbs.lollipop(self.base, dist/3, "purple", ro)
        tip = Nurbs.sphere(self.tip, dist/8, "purple", ro)
        mid = Nurbs.lollipop(self.mid, dist/4, "purple", ro)
        Nurbs.flip_shape(base, "-x")
        Nurbs.flip_shape(mid, "-x")
    # position & parent
        relations = {
            base :     (ptongue.base,        ctrl_socket),
            tip :      (ptongue.tip,         base),
            mid :      (ptongue.mid,        base),}
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    # buffer
        mid_buff = util.buffer(mid)
    # selection sets
        set_grp = [base, tip, mid]
        cmds.sets(set_grp, add = "mouth")
    # cleanup
        util.mtx_zero([base, tip, mid_buff, mid])
        return [base, mid, tip]
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, lipcorners = None):
        cmds.sets(n = "tongue_joints")
        joints = self.skeleton(joint_socket)
        ctrls = self.controls(ctrl_socket)
        # rig.sub_ctrl_vis(self.mid, self.tip)
        mid = ctrls[1]
        mid_buff = cmds.listRelatives(ctrls[1], parent = True)[0]
        cmds.pointConstraint([ctrls[0], ctrls[-1]], mid_buff, mo = True, w = 0.5,
                             n = mid.replace("CTRL", "POINT"), skip = "x")
        cmds.aimConstraint(ctrls[-1], mid_buff, mo = True, w = 1, aimVector = (0,0,1),
                             n = mid.replace("CTRL", "AIM"), upVector = (0,1,0),
                             worldUpType = "objectrotation", worldUpVector = (0,1,0),
                             worldUpObject = self.base, skip = "y")
    # bendy setup
        hcurve = bendy.crv("tongue_highres_CRV", joints, 3)
        tcurve = cmds.rebuildCurve(
                hcurve, n = "tongue_ikSpline_CRV", replaceOriginal = 1, 
                rebuildType = 0, keepRange = 0,
                spans = 4, degree = 3, constructionHistory = 0)[0]
        bendy.ikspline(
                mod_name = "tongue",
                start_jnt = joints[0],
                end_jnt = joints[-1],
                forwardaxis = "z", 
                upaxis = "y",
                base_driver = ctrls[0], 
                head_driver = ctrls[2],
                mid_ctrl = ctrls[1],
                curve = tcurve)
    # switch adv twist type
        iks = "tongue_IKS"
        cmds.setAttr(iks+".dWorldUpType", 4) # obj rot up (start/end)
        cmds.connectAttr(f"{ctrls[0]}.worldMatrix[0]", 
                         f"{iks}.dWorldUpMatrix", f = True)
        cmds.connectAttr(f"{ctrls[2]}.worldMatrix[0]", 
                         f"{iks}.dWorldUpMatrixEnd", f = True)
        cmds.delete("tongue_baseTwist_LOC", "tongue_endTwist_LOC")
            
### missing:

if __name__ == "__main__":
    
    test = tongue()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL",
        lipcorners = ["L_lipcorner_macroOut_GRP", 
                      "R_lipcorner_macroOut_GRP"])
    cmds.hide("proxy_test_GRP")
    pass