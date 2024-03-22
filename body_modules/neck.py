import maya.cmds as cmds

from body_proxies.proxyneck import ProxyNeck

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Neck(object):
    
    def __init__(self, joint_socket, ctrl_socket, spaces):
        
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
        
        self.build_rig(joint_socket, ctrl_socket, spaces)
        
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

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
        nsize = util.distance(self.neck_jnt, self.head_jnt)
        hsize = util.distance(self.head_jnt, self.head_end_jnt)
    # ctrl shapes
        neck = Nurbs.sphere(self.neck, nsize/10, "yellow", "yzx")
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
        bendy = Nurbs.sphere(self.neck_b, nsize/15, "brown")
        for xray in [bendy, neck]:
            shapes = cmds.listRelatives(xray, children = True, shapes = True)
            for s in shapes:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
        # bendy = Nurbs.lollipop(self.neck_b, necklen/3, "yellow")
        # Nurbs.flip_shape(bendy, "y")
        cmds.matchTransform(bendy, neck)
        pointc = cmds.pointConstraint(
                (neck, head), bendy, offset = (0,0,0), weight = 0.5)
        cmds.delete(pointc)
        cmds.parent(bendy, ctrl_socket)
        
####### Attributes
        util.attr_separator([self.neck, self.head])
        cmds.addAttr(self.head, longName = "auto_bend", attributeType = "double", 
                     defaultValue = 1, min = 0, max = 1)
        cmds.setAttr(f"{self.head}.auto_bend", e = True, keyable = True)
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
        
        # connect joints
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
        cmds.setAttr("BODY_TUNING.breath_headFollow", e = True, k = True, channelBox = True)
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
        
        neck_bendy_joints = bendy.setup(
                mod_name = self.module_name, 
                base_driver = self.neck_jnt, 
                head_driver = self.head_jnt,
                forwardaxis = "y", 
                upaxis = "-z",
                mid_ctrl = self.neck_b)
        bendy.aim(
                bendy = self.neck_b,
                aimtarget = self.head_jnt, 
                uptarget = "neck_baseTwist_LOC",
                root = self.neck_jnt,
                vaim = (0,1,0),
                vup = (0,0,-1))
    # auto bending with head rot
        driver = cmds.group(
                n = "neck_autobend_DRIVER", em = True, p = "neck_bendy_buffer_GRP")
        autobend = util.buffer(self.neck_b, "autobend_GRP")
        cmds.parentConstraint(self.head_sub, driver, mo = True, w = 1,
                              skipRotate = ["x", "y", "z"], skipTranslate = ["y"],
                              n = "neck_autobend_driver_PC")
        # toggle
        togg = cmds.shadingNode(
                "multiplyDivide", n = "neck_autobend_toggle_MULT", au = True)
        weight = cmds.shadingNode(
                "multiplyDivide", n = "neck_autobend_weight_MULT", au = True)
        cmds.connectAttr(self.head+".auto_bend", togg+".input1X")
        cmds.connectAttr(self.head+".auto_bend", togg+".input1Y")
        cmds.connectAttr(self.head+".auto_bend", togg+".input1Z")
        cmds.connectAttr(driver+".t", togg+".input2")
        cmds.connectAttr(togg+".output", weight+".input1")
        cmds.setAttr(weight+".input2", 0.4, 0.4, 0.4)
        cmds.connectAttr(weight+".output", autobend+".t")
        
    ### THICKNESS setup for bendies
        thick = bendy.chainthick("neck_thickness_channels_GRP", 
                                   ["sx", "sz"], neck_bendy_joints)
        cmds.parent(thick, "neck_ikSpline_GRP")
    # START
    # neck base into thick.start
        cmds.connectAttr("neck_CTRL.sx", thick+".start_sx")
        cmds.connectAttr("neck_CTRL.sz", thick+".start_sz")
    # MID
    # neck bendy into thick.mid
        cmds.connectAttr("neck_bendy_CTRL.sx", thick+".mid_sx")
        cmds.connectAttr("neck_bendy_CTRL.sz", thick+".mid_sz")
    # END
    # head into thick.end
        cmds.connectAttr("head_CTRL.sx", thick+".end_sx")
        cmds.connectAttr("head_CTRL.sz", thick+".end_sz")
        
### missing:
    # head squetch? MD to maintain normal scale channels on ctrl
    # neck scl shouldn't affect head
        
        
    ### clean up attributes - lock & hide
        util.lock([self.neck, self.neck_sub], ["tx","ty","tz"])
        util.lock(self.neck_sub, ["sx","sy","sz"])
        util.lock(self.neck_b, ["ry"])



if __name__ == "__main__":
    
    test2 = Module()
        
    pass