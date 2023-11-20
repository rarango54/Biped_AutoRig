import maya.cmds as cmds

from body_proxies.proxyneck import ProxyNeck

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Neck(object):
    
    def __init__(self):
        
        self.module_name = "neck"
        
        self.head_jnt = "head_JNT"
        self.neck_jnt = "neck_JNT"
        self.head_end_jnt = "head_end_JNT"
        
        # 5 joints in a straight line
        self.neck_1_jnt = "neck_1_JNT"
        self.neck_2_jnt = "neck_2_JNT"
        self.neck_3_jnt = "neck_3_JNT"
        self.neck_4_jnt = "neck_4_JNT"
        self.neck_5_jnt = "neck_5_JNT"
        
        self.twist_jnt = "neck_twist_JNT"
                
        self.neck_ctrl = "neck_CTRL"
        self.neck_sub_ctrl = "neck_sub_CTRL"
        self.neck_bendy_ctrl = "neck_bendy_CTRL"
        self.head_ctrl = "head_CTRL"
        self.head_sub_ctrl = "head_sub_CTRL"
        
    
        
    def skeleton(self, joint_socket):
        pneck = ProxyNeck()
        neck_jnts = rig.make_joints(
                proxies_list = list(pneck.proxy_dict),
                rot_order = "zxy", 
                radius = 1.5)
        cmds.joint(
                self.neck_jnt, e = True, 
                orientJoint = "yxz", 
                secondaryAxisOrient = "xup", 
                children = True, 
                zeroScaleOrient = True)
        cmds.parent(self.neck_jnt, joint_socket)
        
        cmds.sets(self.head_jnt, add = "bind_joints")
        
        # temp jaw for better skinning during testing
        cmds.select(self.head_jnt)
        mandible = cmds.joint(n = "mandible_JNT", position = (0, 166, 8))
        chin = cmds.joint(n = "chin_JNT", position = (0, 164, 14))
        cmds.sets((mandible, chin), add = "bind_joints")

    def controls(self, ctrl_socket):
        nsize = util.get_distance(self.neck_jnt, self.head_jnt)
        hsize = util.get_distance(self.head_jnt, self.head_end_jnt)
        # ctrl shapes
        neck = Nurbs.swoop_circle(self.neck_ctrl, nsize/3)
        neck_sub = Nurbs.swoop_circle(self.neck_sub_ctrl, nsize/3.5, "orange")
        head = Nurbs.box(self.head_ctrl, hsize, hsize*1.5, hsize,
        "yellow", "xzy")
        head_sub = Nurbs.box(self.head_sub_ctrl, hsize/2.2, hsize/1.1, hsize/2.2,
        "orange", "xzy")
        
        relations = {
            neck :      (self.neck_jnt, ctrl_socket),
            neck_sub :  (self.neck_jnt, neck),
            head :      (self.head_jnt, ctrl_socket),
            head_sub :  (self.head_jnt, head)
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.mtx_zero(list(relations))
        util.attr_separator([self.neck_ctrl, self.head_ctrl])
        rig.sub_ctrl_vis(self.neck_sub_ctrl)
        rig.sub_ctrl_vis(self.head_sub_ctrl)
        
        necklen = util.get_distance(self.neck_jnt, self.head_jnt)
        bendy = Nurbs.lollipop(self.neck_bendy_ctrl, necklen/3, "yellow")
        Nurbs.flip_shape(bendy, "y")
        cmds.matchTransform(bendy, neck)
        pointc = cmds.pointConstraint(
                (neck, head), bendy, offset = (0,0,0), weight = 0.5)
        cmds.delete(pointc)
        cmds.parent(bendy, ctrl_socket)
        util.mtx_hook(self.neck_jnt, bendy)
        
        cmds.sets(neck, neck_sub, bendy, head, head_sub,
                  add = "neck_head")

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
        # connections = {
        #     self.neck_sub_ctrl : self.neck_jnt,
        #     self.head_sub_ctrl : self.head_jnt
        # }
        # for ctrl in list(connections):
        #     jnt = connections[ctrl]
        #     cmds.parentConstraint(ctrl, jnt, weight = 1)
        #     cmds.scaleConstraint(ctrl, jnt, offset = (1,1,1), weight = 1)
        
        bendy.setup(
                mod_name = self.module_name, 
                base_driver = self.neck_jnt, 
                head_driver = self.head_jnt,
                forwardaxis = "y", 
                upaxis = "-z",
                mid_ctrl = self.neck_bendy_ctrl)
        
        head_buff = util.buffer(self.head_ctrl)
        cmds.parentConstraint(
                self.neck_sub_ctrl, head_buff, mo = True, 
                skipRotate = ("x", "y", "z"), weight = 1)
        cmds.pointConstraint(
                self.neck_sub_ctrl, self.neck_jnt, offset = (0,0,0), weight = 1)
        # add orient constraint with rot spaces
        neck_ikh = cmds.ikHandle(
                self.neck_jnt,
                solver = "ikSCsolver",
                startJoint = self.neck_jnt,
                endEffector = self.head_jnt,
                n = f"{self.module_name}_IKH")
        cmds.rename(neck_ikh[1], f"{self.module_name}_EFF")
        head_ikh = cmds.ikHandle(
                self.head_jnt,
                solver = "ikSCsolver",
                startJoint = self.head_jnt,
                endEffector = self.head_end_jnt,
                n = "head_IKH")
        cmds.rename(neck_ikh[1], "head_EFF")
        cmds.parent((neck_ikh[0], head_ikh[0]), "misc_GRP")
        util.mtx_hook(self.head_ctrl, neck_ikh[0])
        util.mtx_hook(self.head_ctrl, head_ikh[0])
        cmds.parentConstraint(
                self.neck_jnt, self.neck_bendy_ctrl, mo = True, weight = 1)
        # stretch: distBetw(head & neck_sub) -> MD normalize -> neck_JNT scaleY
        dist = cmds.shadingNode(
                "distanceBetween", n = "neck_length_DBTW", asUtility = True)
        cmds.connectAttr(f"{self.neck_sub_ctrl}.worldMatrix[0]", f"{dist}.inMatrix1")
        cmds.connectAttr(f"{self.head_ctrl}.worldMatrix[0]", f"{dist}.inMatrix2")
        orig_length = cmds.getAttr(f"{dist}.distance")
        norm = cmds.shadingNode(
                "multiplyDivide", n = "neck_lengthNormalise_MD", asUtility = True)
        cmds.setAttr(f"{norm}.operation", 2)
        cmds.connectAttr(f"{dist}.distance", f"{norm}.input1X")
        cmds.setAttr(f"{norm}.input2X", orig_length)
        cmds.connectAttr(f"{norm}.outputX", f"{self.neck_jnt}.scaleY")
        #### IK FK hybrid not working yet, might need setup without single IKHandles?
        #### currentlywhen IK posing the head,
        #### -> neck scale Y is not shortening the length of the neck :(
        # direct connect: head_ctrl scale * global_scl to head_jnt
        globscl = cmds.shadingNode(
                "multiplyDivide", n = "head_globalScl_MD", asUtility = True)
        cmds.connectAttr("global_CTRL.scale", f"{globscl}.input1")
        cmds.connectAttr(f"{self.head_ctrl}.scale", f"{globscl}.input2")
        cmds.connectAttr(f"{globscl}.output", f"{self.head_jnt}.scale")
        
        # head squetch? MD to maintain normal scale channels on ctrl
        # neck scl shouldn't affect head
        
        # mid twist from bendy_ctrl Ry possible?



if __name__ == "__main__":
    
    test2 = Module()
        
    pass