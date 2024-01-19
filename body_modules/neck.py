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
        
        self.neck_1_jnt = "neck_1_JNT"
        self.neck_2_jnt = "neck_2_JNT"
        self.neck_3_jnt = "neck_3_JNT"
        self.neck_4_jnt = "neck_4_JNT"
        self.neck_5_jnt = "neck_5_JNT"
        
        self.twist_jnt = "neck_twist_JNT"
                
        self.neck = "neck_CTRL"
        self.neck_sub = "neck_sub_CTRL"
        self.neck_b = "neck_bendy_CTRL"
        self.head = "head_CTRL"
        self.head_sub = "head_sub_CTRL"
        
    
        
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
        # cmds.select(self.head_jnt)
        # mandible = cmds.joint(n = "mandible_JNT", position = (0, 166, 8))
        # chin = cmds.joint(n = "chin_JNT", position = (0, 164, 14))
        # cmds.sets((mandible, chin), add = "bind_joints")

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
        nsize = util.distance(self.neck_jnt, self.head_jnt)
        hsize = util.distance(self.head_jnt, self.head_end_jnt)
    # ctrl shapes
        neck = Nurbs.sphere(self.neck, nsize/10, "yellow", "yzx")
        nshapes = cmds.listRelatives(neck, children = True, shapes = True)
        for shp in nshapes:
            cmds.setAttr(shp+".alwaysDrawOnTop", 1)
        # neck = Nurbs.swoop_circle(self.neck, nsize/2)
        neck_sub = Nurbs.swoop_circle(self.neck_sub, nsize/2.5, "orange")
        head = Nurbs.box(self.head, hsize, hsize/6, hsize,"yellow", "xzy")
        head_sub = Nurbs.box(
                self.head_sub, hsize*0.8, hsize/8, hsize*0.8, "orange", "xzy")
        cmds.move(0, hsize*0.8, 0, head+".cv[0:15]", r = True)
        cmds.move(0, hsize*0.8, 0, head_sub+".cv[0:15]", r = True)
        
    # expose rotateOrder
        cmds.setAttr(f"{head}.rotateOrder", channelBox = True)
            
    # position & parent
        relations = {
            neck :      (self.neck_jnt, ctrl_socket),
            neck_sub :  (self.neck_jnt, neck),
            head :      (self.head_jnt, neck_sub),
            head_sub :  (self.head_jnt, head)}
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    # mid neck bendy ctrl
        necklen = util.distance(self.neck_jnt, self.head_jnt)
        bendy = Nurbs.lollipop(self.neck_b, necklen/3, "yellow")
        Nurbs.flip_shape(bendy, "y")
        cmds.matchTransform(bendy, neck)
        pointc = cmds.pointConstraint(
                (neck, head), bendy, offset = (0,0,0), weight = 0.5)
        cmds.delete(pointc)
        cmds.parent(bendy, ctrl_socket)
        
####### Attributes
        util.attr_separator([self.neck, self.head])
        rig.sub_ctrl_vis(self.neck_sub)
        rig.sub_ctrl_vis(self.head_sub)
    ### Spaces
        rig.spaces(spaces, head, r_only = True)
    # selection sets
        cmds.sets(neck, neck_sub, bendy, head, head_sub,
                  add = "neck_head")
    # cleanup
        util.mtx_zero(list(relations))
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, spaces)
        head_space = cmds.listRelatives(self.head, parent = True)[0]
        comp = rig.fk_sclinvert(head_space)
        # rewire scale inversion to neck_ctrl (neck_sub_ctrl scale will be locked)
        cmds.connectAttr(f"{self.neck}.s", f"{comp}.inputScale", force = True)
        
        # connect rotateOrders from ctrls to joints
        ro_ctrls = [self.neck, self.head]
        for ro_ctrl in ro_ctrls:
            jnt = ro_ctrl.replace("_CTRL", "_JNT")
            cmds.connectAttr(f"{ro_ctrl}.rotateOrder", f"{jnt}.rotateOrder")
        
        # connections = {
        #     self.neck_sub : self.neck_jnt,
        #     self.head_sub : self.head_jnt}
        # for ctrl in list(connections):
        #     jnt = connections[ctrl]
        #     cmds.parentConstraint(ctrl, jnt, weight = 1)
        #     cmds.scaleConstraint(ctrl, jnt, offset = (1,1,1), weight = 1)
        # cmds.pointConstraint(
        #         self.head_sub, self.head_jnt, offset = (0,0,0), weight = 1)
        cmds.orientConstraint(
                self.head_sub, self.head_jnt, offset = (0,0,0), weight = 1)
        cmds.scaleConstraint(
                self.head_sub, self.head_jnt, offset = (1,1,1), weight = 1)
        
        cmds.aimConstraint(self.head_sub, self.neck_jnt, aim = (0,1,0), 
                           upVector = (0,0,1), worldUpObject = ctrl_socket, 
                           worldUpType = "objectrotation", worldUpVector = (0,0,1),
                           weight = 1)
        
    # stretchy scale based on distance
        length = cmds.shadingNode(
            "distanceBetween", asUtility = True, n = "neck_length_DBTW")
        cmds.connectAttr(f"{self.head_sub}.worldMatrix[0]", f"{length}.inMatrix1")
        cmds.connectAttr(f"{self.neck_sub}.worldMatrix[0]", f"{length}.inMatrix2")
        orig_length = cmds.getAttr(f"{length}.distance")
        norm = cmds.shadingNode(
            "multiplyDivide", asUtility = True, n = "neck_length_NORM")
        cmds.setAttr(f"{norm}.operation", 2) # divide
        cmds.setAttr(f"{norm}.input1", 1,1,1)
        cmds.connectAttr(f"{length}.distance", f"{norm}.input1Y")
        cmds.setAttr(f"{norm}.input2Y", orig_length)
        
    ### mult breathing into scaleY
        # BODY_TUNING
        util.attr_separator("BODY_TUNING", name = "Neck")
        cmds.addAttr(
            "BODY_TUNING", longName = "breath_headFollow",
            attributeType = "double", defaultValue = 0.4, min = 0, max = 1)
        cmds.setAttr("BODY_TUNING.breath_headFollow", e = True, channelBox = True)
        # reverse the 0 to 1 range
        rev = cmds.shadingNode("reverse", n = "neck_breathHeadFollow_REV", au = True)
        cmds.connectAttr("BODY_TUNING.breath_headFollow", f"{rev}.inputY")
        # MULT breath driver TY * Tuning attr
        amult = cmds.shadingNode(
                "multiplyDivide", n = "neck_breathHeadFollow_MULT", au = True)
        cmds.connectAttr(f"{rev}.outputY", f"{amult}.input1Y")
        cmds.connectAttr("chest_breath_DRIVE.ty", f"{amult}.input2Y")
        # REMAP breathing ty to neck scale based on orig neck length
        rmv = util.remap(
                "neck_breathHeadFollow_RMAP", f"{amult}.outputY",
                -orig_length, orig_length, 2, 0)
        # cmds.connectAttr(f"{amult}.outputY", f"{rmv}.inputValue")
        # MULT breath neck scale * stretch setup (norm)
        bmult = cmds.shadingNode(
                "multiplyDivide", n = "neck_breath_MULT", au = True)
        cmds.connectAttr(f"{norm}.output", f"{bmult}.input1")
        cmds.connectAttr(f"{rmv}.outValue", f"{bmult}.input2Y")
    ### scale Y into neck_JNT
        cmds.connectAttr(f"{bmult}.outputY", f"{self.neck_jnt}.scaleY")
        
    ### Thickness = globalScl * neck_ctrl (only sx, sz)
        glob_mult = cmds.shadingNode(
                "multiplyDivide", n = "neck_thickness_MULT", au = True)
        cmds.connectAttr(f"{self.neck}.sx", f"{glob_mult}.input1X")
        cmds.connectAttr(f"{self.neck}.sz", f"{glob_mult}.input1Z")
        cmds.connectAttr("global_CTRL.s", f"{glob_mult}.input2")
        cmds.connectAttr(f"{glob_mult}.outputX", f"{self.neck_jnt}.sx")
        cmds.connectAttr(f"{glob_mult}.outputZ", f"{self.neck_jnt}.sz")
        
        bendy.setup(
                mod_name = self.module_name, 
                base_driver = self.neck_jnt, 
                head_driver = self.head_jnt,
                forwardaxis = "y", 
                upaxis = "-z",
                mid_ctrl = self.neck_b)
        # attach bendy ctrl
        util.mtx_hook(self.neck_jnt, self.neck_b)
        
        # head squetch? MD to maintain normal scale channels on ctrl
        # neck scl shouldn't affect head
        
        # mid twist from bendy_ctrl Ry possible?
        
    ### clean up attributes - lock & hide
        util.lock([self.neck, self.neck_sub], ["tx","ty","tz"])
        util.lock(self.neck_sub, ["sx","sy","sz"])



if __name__ == "__main__":
    
    test2 = Module()
        
    pass