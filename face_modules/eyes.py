import maya.cmds as cmds

from face_proxies.proxyeye import ProxyEye

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


class Eyes(object):
    
    def __init__(self, joint_socket, ctrl_socket, spaces):

        self.module_name = "L_eye"
        
        self.socket_jnt = "L_eye_socket_JNT"
        self.eye_jnt = "L_eye_JNT"
        self.iris_jnt = "L_iris_JNT"
        self.pupil_jnt = "L_pupil_JNT"
        
        self.socket = "L_eye_socket_CTRL"
        self.aim = "aim_CTRL"
        self.aim_offset = "L_aim_offset_CTRL"
        self.eye = "L_eye_CTRL"
        self.aim_grp = "L_eye_aim_GRP"
        self.off_grp = "L_eye_offset_GRP"
        
        self.build_rig(joint_socket, ctrl_socket, spaces)
                
    def skeleton(self, joint_socket):
        peye = ProxyEye()
        eye_jnts = rig.make_joints(
                proxies_list = list(peye.proxy_dict)[:3],
                rot_order = "zxy", 
                radius = 1,
                set = "fjoints")
        cmds.parent(eye_jnts[0], joint_socket)
    # xtra eye_socket_jnt for non uniform scaling of eye
        cmds.duplicate(eye_jnts[0], parentOnly = True, n = self.socket_jnt)
        cmds.setAttr(self.socket_jnt+".radius", 2)
        cmds.parent(eye_jnts[0], self.socket_jnt)
        mirr_jnts = cmds.mirrorJoint(
                self.socket_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        
        # eye joints not relevant for fbind_joints set

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
    # Setup
        peye = ProxyEye()
        ikctrl_grp = cmds.group(
                n = "L_eye_IKctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "zxy"
        dist = util.distance("L_eye_JNT", "R_eye_JNT")
        ball = cmds.getAttr(self.iris_jnt+".tz")
      
    ### CTRL SHAPES
        socket = Nurbs.circle(self.socket, dist/3, "blue")
        aim = Nurbs.box(self.aim, dist*2, dist, dist/12, "yellow")
        eye = Nurbs.circle(self.eye, ball/3, "blue")
        aim_offset = Nurbs.circle(self.aim_offset, dist/3, "blue")
        # shape adjusts
        cmds.move(0,0,ball*1.2, eye+".cv[0:7]", r = True, localSpace = True)
        cmds.move(dist*1.5,0,0, socket+".cv[0:7]", r = True)
    # aim grp
        aim_grp = cmds.group(n = self.aim_grp, em = True)
        off_grp = cmds.group(n = self.off_grp, em = True)
        
    # position & parent
        relations = {
            socket :   (peye.eye,     ctrl_socket),
            aim :      (peye.aim,     ctrl_socket),
            aim_offset : (peye.aim,   aim),
            aim_grp :  (peye.eye,     socket),
            eye :      (peye.eye,     aim_grp),
            off_grp :  (peye.eye,     eye),
            }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            if ctrl == self.aim:
                cmds.setAttr(ctrl+".tx", 0)
            cmds.parent(ctrl, relations[ctrl][1])

        
####### Attributes
        util.attr_separator([aim, eye])
        cmds.addAttr(aim, longName = "converge", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(aim+".converge", e = True, keyable = True)
        for attr in ["horizontal", "vertical", "iris", "pupil"]:
            for side in ["L_", "R_"]:
                if attr == "iris" or attr == "pupil":
                    cmds.addAttr(aim, longName = side+attr, attributeType = "double", 
                                 defaultValue = 1, min = 0)
                    cmds.setAttr(aim+"."+side+attr, e = True, keyable = True)
                else:
                    cmds.addAttr(aim, longName = side+attr, attributeType = "double", 
                                 defaultValue = 0)
                    cmds.setAttr(aim+"."+side+attr, e = True, keyable = True)
        # fk eye ctrl
        cmds.addAttr(eye, longName = "iris", attributeType = "double", 
                     defaultValue = 1, min = 0)
        cmds.setAttr(eye+".iris", e = True, keyable = True)
        cmds.addAttr(eye, longName = "pupil", attributeType = "double", 
                     defaultValue = 1, min = 0)
        cmds.setAttr(eye+".pupil", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        aim_mirr_grp = cmds.group(
                n = "R_eye_aim_mirror_GRP", empty = True, parent = aim)
        cmds.setAttr(aim_mirr_grp+".sx", -1)
        fkctrl_mirror_grp = cmds.group(
                n = "R_eye_FKctrls_mirror_GRP", empty = True, parent = ctrl_socket)
        cmds.setAttr(fkctrl_mirror_grp+".sx", -1)
        rig.mirror_ctrls(socket, fkctrl_mirror_grp)
        rig.mirror_ctrls(aim_offset, aim_mirr_grp)
        
    ### Spaces only for aim_ctrl
        rig.spaces(spaces, aim)
    
    # selection sets (don't need for eye ctrls)
        set_grp = [socket, aim, eye, aim_offset]
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "eyes")
        
    # cleanup
        util.mtx_zero([socket, aim, aim_offset, eye, aim_grp], rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, spaces)
        
        for s in ["L_", "R_"]:
        # socket_jnt
            cmds.parentConstraint(
                s+"eye_socket_CTRL", s+"eye_socket_JNT", n = s+"eye_jnt_PC", 
                mo = True, w = 1)
            cmds.scaleConstraint(
                s+"eye_socket_CTRL", s+"eye_socket_JNT", n = s+"eye_jnt_PC", 
                mo = True, w = 1)
        
        # eye_jnt (no invScale)
            cmds.disconnectAttr(s+"eye_socket_JNT.s", s+"eye_JNT.inverseScale")
            cmds.parentConstraint(
                s+"eye_offset_GRP", s+"eye_JNT", n = s+"eye_jnt_PC", mo = True, w = 1)
            # cmds.scaleConstraint(
            #     s+"eye_offset_GRP", s+"eye_JNT", n = s+"eye_jnt_PC", mo = True, w = 1)
            
        # aimConstraint(aim, aim_grp, mo = True)
            cmds.aimConstraint(
                s+"aim_offset_CTRL", s+"eye_aim_GRP", n = s+"eye_AIM", mo = True, weight = 1,
                aimVector = (0,0,1), upVector = (0,1,0), 
                worldUpType = "objectrotation", worldUpVector = (0,1,0), 
                worldUpObject = s+"eye_socket_CTRL")
        
        # off.r = aimattrs + eyeattrs
            pma = cmds.shadingNode(
                    "plusMinusAverage", n = s+"eye_offset_r_ADD", au = True)
            cmds.connectAttr(self.aim+".converge", pma+".input3D[0].input3Dy")
            cmds.connectAttr(f"{self.aim}.{s}horizontal", pma+".input3D[1].input3Dy")
            cmds.connectAttr(f"{self.aim}.{s}vertical", pma+".input3D[1].input3Dx")
            cmds.connectAttr(pma+".output3D", s+"eye_offset_GRP.r")
            
        # scaling iris & puil
            cmds.disconnectAttr(s+"eye_JNT.scale", s+"iris_JNT.inverseScale")
            cmds.disconnectAttr(s+"iris_JNT.scale", s+"pupil_JNT.inverseScale")
            imult = cmds.shadingNode(
                    "multiplyDivide", n = s+"irisScl_MULT", au = True)
            cmds.connectAttr(f"{self.aim}.{s}iris", imult+".input1X")
            cmds.connectAttr(f"{self.aim}.{s}iris", imult+".input1Y")
            cmds.connectAttr(f"{self.aim}.{s}iris", imult+".input1Z")
            cmds.connectAttr(s+"eye_CTRL.iris",imult+".input2X")
            cmds.connectAttr(s+"eye_CTRL.iris",imult+".input2Y")
            cmds.connectAttr(s+"eye_CTRL.iris",imult+".input2Z")
            cmds.connectAttr(imult+".outputX", s+"iris_JNT.sx")
            cmds.connectAttr(imult+".outputY", s+"iris_JNT.sy")
            pmult = cmds.shadingNode(
                    "multiplyDivide", n = s+"pupilScl_MULT", au = True)
            cmds.connectAttr(f"{self.aim}.{s}pupil", pmult+".input1X")
            cmds.connectAttr(f"{self.aim}.{s}pupil", pmult+".input1Y")
            cmds.connectAttr(f"{self.aim}.{s}pupil", pmult+".input1Z")
            cmds.connectAttr(s+"eye_CTRL.pupil",pmult+".input2X")
            cmds.connectAttr(s+"eye_CTRL.pupil",pmult+".input2Y")
            cmds.connectAttr(s+"eye_CTRL.pupil",pmult+".input2Z")
            cmds.connectAttr(pmult+".outputX", s+"pupil_JNT.sx")
            cmds.connectAttr(pmult+".outputY", s+"pupil_JNT.sy")
    # aim aim_ctrl to head_ctrl = spaces[0]
        cmds.aimConstraint(
            spaces[0], self.aim, n = "aim_head_AIM", mo = True, w = 1,
            aimVector = (0,0,-1), upVector = (0,1,0), worldUpType = "objectrotation",
            worldUpVector = (0,1,0), worldUpObject = spaces[0])
        
    ### clean up attributes - lock & hide
        util.lock([self.aim, self.aim_offset], 
                  ["rx","ry","rz","sx","sy","sz"], rsidetoo = True)
        util.lock(self.eye, ["tx","ty","tz","sx","sy","sz"], rsidetoo = True)

if __name__ == "__main__":
    
    
    pass