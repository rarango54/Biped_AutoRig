import maya.cmds as cmds

from body_proxies.proxyhand import ProxyHand

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import helpers


class Hands(object):
    
    def __init__(self):
        
        self.module_name = "L_fingers"
        
        phand = ProxyHand()
        
        self.hand_grp = "L_hand_ctrls_GRP"
        
        self.meta_jnts = []
        for finger in ("index", "middle", "ring", "pinky"):
            self.meta_jnts.append(f"L_{finger}_meta_JNT")
        self.thumb_meta_jnt = "L_thumb_meta_JNT"
        self.finger_jnts = [x.replace("_PRX", "_JNT") for x in phand.finger_prxs]
        self.onlyfinger_jnts = [x.replace("_PRX", "_JNT") for x in phand.onlyfinger_prxs]
        
        self.index_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.index[:-1]]
        self.middle_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.middle[:-1]]
        self.ring_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.ring[:-1]]
        self.pinky_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.pinky[:-1]]
        self.thumb_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.thumb[:-1]]
        
        self.allfinger_ctrls = [x.replace("_PRX", "_CTRL") for x in phand.finger_prxs]
        self.allmeta_ctrls = [
            "L_index_meta_CTRL", "L_middle_meta_CTRL", "L_ring_meta_CTRL",
            "L_pinky_meta_CTRL", "L_thumb_meta_CTRL"]
        
        self.master = "L_fingerMaster_CTRL"
        
        
        
         
    def skeleton(self, joint_socket):
        phand = ProxyHand()
    # prxorient = True for all finger joints -> no need to orient
        index_jnts = rig.make_joints(phand.index, "zyx", 1, True)
        middle_jnts = rig.make_joints(phand.middle, "zyx", 1, True)
        ring_jnts = rig.make_joints(phand.ring, "zyx", 1, True)
        pinky_jnts = rig.make_joints(phand.pinky, "zyx", 1, True)
        thumb_jnts = rig.make_joints(phand.thumb, "zyx", 1, True)
        allmetas = self.meta_jnts.copy()
        allmetas.append(self.thumb_meta_jnt)
        cmds.parent(allmetas, "root_JNT") # temporary to make mirroring work

        for jnt in allmetas:
            mirr_jnt = cmds.mirrorJoint(
                    jnt, mirrorYZ = True, mirrorBehavior = True, 
                    searchReplace = ["L_", "R_"])[0]
            cmds.parent(jnt, joint_socket)
            cmds.parent(mirr_jnt, joint_socket.replace("L_", "R_"))
        # sets
        cmds.sets(self.finger_jnts, add = "bind_joints")
        r_bind_jnts = [x.replace("L_", "R_") for x in self.finger_jnts]
        cmds.sets(r_bind_jnts, add = "bind_joints")

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
    # setup
        phand = ProxyHand()
        hand_grp = cmds.group(n = self.hand_grp, em = True, 
                              parent = "global_sub_CTRL")
        cmds.matchTransform(hand_grp, "L_hand_JNT", pos = True, rot = True)
    # FK controls
        # scl = thickness of fk ctrls
        scl = cmds.getAttr("L_middle_2_JNT.tz") / 2
        ro = "zyx"
        prev_dist = scl
        for name in self.allfinger_ctrls:
            # derive joint
            jnt = name.replace("_CTRL", "_JNT")
            # derive next joint
            nxt_jnt = cmds.listRelatives(jnt, children = True, type = "joint")[0]
            # read Tz for distance
            if nxt_jnt:
                dist = cmds.getAttr(f"{nxt_jnt}.tz") * 0.8
            else:
                dist = prev_dist
            # create ctrl based on distance
            if "meta" in name:
                ctrl = Nurbs.metacarpal(name, scl, "blue", ro)
            else:
                ctrl = Nurbs.fk_box(name, scl, dist, "blue", ro)
            # snap ctrl to joint
            cmds.matchTransform(ctrl, jnt, pos = True, rot = True)
            prev_dist = dist
            
    ### parenting loop for each chain of finger ctrls
        for finger in [self.index_ctrls, self.middle_ctrls, self.ring_ctrls, 
                      self.pinky_ctrls, self.thumb_ctrls]:
            many = len(finger)
            for n in range(1, many):
                neg = n * -1
                cmds.parent(finger[neg], finger[neg-1])
                    
    # fingerMaster ctrl
        master = Nurbs.metaMaster(self.master, scl)
        cmds.matchTransform(master, "L_ring_meta_JNT", pos = True, rot = True)
    
    # parent ctrls into hand_grp
        cmds.parent(self.allmeta_ctrls, hand_grp)
        cmds.parent(self.master, hand_grp)
        
####### Attributes
        util.attr_separator(master)
        # cmds.addAttr(master, longName = "curl", attributeType = "double", 
        #              defaultValue = 0)
        # cmds.setAttr(f"{master}.curl", e = True, keyable = True)

        
    #### MIRROR CTRLS TO THE RIGHT SIDE ####
        ctrl_mirror_grp = cmds.group(
                n = "R_hand_ctrls_mirror_GRP", empty = True, parent = "global_sub_CTRL")
        cmds.setAttr(f"{ctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls(hand_grp, ctrl_mirror_grp)
        
    # selection sets
        L_ctrls = self.allfinger_ctrls.copy()
        L_ctrls.append(self.master)
        R_ctrls = [x.replace("L_", "R_") for x in L_ctrls]
        cmds.sets(L_ctrls, add = "L_fingers")
        cmds.sets(R_ctrls, add = "R_fingers")
        
    # cleanup
        util.mtx_zero(L_ctrls, rsidetoo = True)
        for sclinv in [
                self.index_ctrls[1:], self.middle_ctrls[1:], self.ring_ctrls[1:],
                self.pinky_ctrls[1:], self.thumb_ctrls[1:]
                ]:
            rig.fk_sclinvert(sclinv, rsidetoo = True)

###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
    # connect rotateOrders from ctrls to joints
        for s in ["L_", "R_"]:
            if s  == "R_":
                fing_ctrls = [x.replace("L_", "R_") for x in self.allfinger_ctrls]
            else:
                fing_ctrls = self.allfinger_ctrls
            for ctrl in fing_ctrls:
                jnt = ctrl.replace("_CTRL", "_JNT")
                cmds.connectAttr(f"{ctrl}.rotateOrder", f"{jnt}.rotateOrder")
        
    ### FK setup
                cmds.connectAttr(f"{ctrl}.r", f"{jnt}.r")
                cmds.pointConstraint(
                        ctrl, jnt, n = ctrl.replace("_CTRL", "_POINT"),
                        offset = (0,0,0), weight = 1)
                cmds.scaleConstraint(
                        ctrl, jnt, n = ctrl.replace("_CTRL", "_SCL"),
                        mo = True, weight = 1)
        # attach hand_grp to hand_JNT
            util.mtx_hook(f"{s}hand_JNT", f"{s}hand_ctrls_GRP")
            
    ### Meta-Master setup
        # master_ctrl drives rotations on all meta_ctrls
            for nr, meta in enumerate(
                [f"{s}middle_meta_CTRL", f"{s}ring_meta_CTRL", f"{s}pinky_meta_CTRL"]
                    ):
                buff = util.buffer(meta, "macro_GRP")
                cmds.setAttr(f"{buff}.rotateOrder", 5) # zyx
                util.mtx_zero(meta)
                jnt = meta.replace("_CTRL", "_JNT")
            # middle
                if nr == 0:
                    # buff connection (MULT)
                    mult = cmds.shadingNode(
                            "multiplyDivide", 
                            n = meta.replace("_CTRL", "_fingerMaster_MULT"), au = True)
                    cmds.setAttr(f"{mult}.input2", 0.2, 0.2, 0.2)
                    cmds.connectAttr(f"{s}fingerMaster_CTRL.r", f"{mult}.input1")
                    cmds.connectAttr(f"{mult}.output", f"{buff}.r")
                    # jnt connection (ADD)
                    pma = cmds.shadingNode(
                            "plusMinusAverage", 
                            n = meta.replace("_CTRL", "_fingerMaster_ADD"), au = True)
                    cmds.connectAttr(f"{mult}.output", f"{pma}.input3D[0]")
                    cmds.connectAttr(f"{meta}.r", f"{pma}.input3D[1]")
                    cmds.connectAttr(f"{pma}.output3D", f"{jnt}.r", force = True)
            # ring
                if nr == 1:
                    # buff connection (MULT)
                    mult = cmds.shadingNode(
                            "multiplyDivide", 
                            n = meta.replace("_CTRL", "_fingerMaster_MULT"), au = True)
                    cmds.setAttr(f"{mult}.input2", 0.5, 0.5, 0.5)
                    cmds.connectAttr(f"{s}fingerMaster_CTRL.r", f"{mult}.input1")
                    cmds.connectAttr(f"{mult}.output", f"{buff}.r")
                    # jnt connection (ADD)
                    pma = cmds.shadingNode(
                            "plusMinusAverage", 
                            n = meta.replace("_CTRL", "_fingerMaster_ADD"), au = True)
                    cmds.connectAttr(f"{mult}.output", f"{pma}.input3D[0]")
                    cmds.connectAttr(f"{meta}.r", f"{pma}.input3D[1]")
                    cmds.connectAttr(f"{pma}.output3D", f"{jnt}.r", force = True)
            # pinky
                if nr == 2:
                    # buff connection no MULT needed for pinky
                    cmds.connectAttr(f"{s}fingerMaster_CTRL.r", f"{buff}.r")
                    # jnt connection (ADD)
                    pma = cmds.shadingNode(
                            "plusMinusAverage", 
                            n = meta.replace("_CTRL", "_fingerMaster_ADD"), au = True)
                    cmds.connectAttr(f"{s}fingerMaster_CTRL.r", f"{pma}.input3D[0]")
                    cmds.connectAttr(f"{meta}.r", f"{pma}.input3D[1]")
                    cmds.connectAttr(f"{pma}.output3D", f"{jnt}.r", force = True)
        
        partials = helpers.partial(self.onlyfinger_jnts, rsidetoo = True)
        cmds.sets(partials, add = "helper_joints")
                    
                    
    ### clean up attributes - lock & hide
        lock_set = self.allfinger_ctrls.copy()
        lock_set.remove("L_thumb_meta_CTRL")
        util.lock(lock_set, ["tx","ty","tz"], rsidetoo = True)
        util.lock(self.master, ["tx","ty","tz","sx","sy","sz"], rsidetoo = True)
        

if __name__ == "__main__":
    
    test = Hands()
    print(test.allfinger_ctrls)
    print(test.master)
    print(test.index_ctrls)
        
    pass