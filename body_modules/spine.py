import maya.cmds as cmds

from body_proxies.proxyspine import ProxySpine

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy
from utils import helpers


class Spine(object):
    
    def __init__(self, joint_socket, ctrl_socket, spaces):
        
        self.module_name = "spine"
        
        self.hip_jnt = "hip_JNT"
        self.waist_jnt = "waist_JNT"
        self.chest_jnt = "chest_JNT"
        self.chest_up_jnt = "chest_up_JNT"
        self.spine_end_jnt = "spine_end_JNT"
        
        self.fly = "fly_CTRL"
        self.cog = "cog_CTRL"
        self.body = "body_CTRL"
        self.body_sub = "body_sub_CTRL"
        self.hip = "hip_CTRL"
        self.hip_sub = "hip_sub_CTRL"
        self.waist = "waist_CTRL"
        self.chest = "chest_CTRL"
        self.chest_sub = "chest_sub_CTRL"
        self.chest_up = "chest_up_CTRL"
        
        self.breath = "breathing_CTRL"
        self.breath_drive = "chest_breath_DRIVE"
        self.ribcage_jnt = "ribcage_JNT"
        self.ribcage = "ribcage_GRP"
        
        self.chest_up_socket = "chest_up_SOCKET"
        
        spaces.insert(0, self.body_sub)
        self.build_rig(joint_socket, ctrl_socket, spaces)
        
    def skeleton(self, joint_socket):
        pspine = ProxySpine()
        spine_jnts = rig.make_joints(list(pspine.proxy_dict)[3:7], "zxy", 1.5)
        cmds.joint(
            self.hip_jnt, e = True, 
            orientJoint = "yxz", secondaryAxisOrient = "xup", children = True)
        cmds.parent(self.hip_jnt, joint_socket)
        
        cmds.sets(spine_jnts, add = "bind_joints")
        cmds.sets([self.waist_jnt, self.chest_jnt], 
                  remove = "bind_joints")
        
        cmds.select(clear = True)
        ribcage = cmds.joint(n = self.ribcage_jnt, rotationOrder = "zxy", radius = 1.5)
        cmds.matchTransform(ribcage, pspine.ribcage, position = True)
        cmds.parent(ribcage, spine_jnts[-1])
        cmds.select(clear = True)
### change to "helper_joints" after testing
        cmds.sets(ribcage, add = "bind_joints")
        cmds.sets(ribcage, add = "joints")

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
        size = util.distance(self.hip_jnt, self.chest_up_jnt)/2
        fly = Nurbs.fly(self.fly, size*3)
        cog = Nurbs.sphere(self.cog, size/6, "purple", "zxy")
        body = Nurbs.box(self.body, size*2, size/2, size*1.5, "yellow", "zxy")
        body_sub = Nurbs.box(self.body_sub, size*1.8, size/4, size*1.5, "pink", "zxy")
        # hip = Nurbs.swoop_circle(self.hip, size*0.75, "brown", "yzx")
        hip = Nurbs.sphere(self.hip, size/6, "yellow", "yzx")
        hip_sub = Nurbs.swoop_circle(self.hip_sub, size, "pink", "yzx")
        # waist = Nurbs.square(self.waist, size*1.5, "brown", "zxy")
        waist = Nurbs.sphere(self.waist, size/8, "brown", "zxy")
        # chest = Nurbs.swoop_circle(self.chest, size*1.2, "yellow", "zyx")
        chest = Nurbs.sphere(self.chest, size/6, "yellow", "zyx")
        chest_sub = Nurbs.swoop_circle(self.chest_sub, size, "pink", "zyx")
        breath_grp = cmds.group(n = self.breath_drive, em = True)
        # chest_up = Nurbs.swoop_circle(self.chest_up, size*0.75, "brown", "zyx")
        chest_up = Nurbs.sphere(self.chest_up, size/8, "brown", "zyx")
        breath = Nurbs.triangle(self.breath, size/3, size/6, "pink")
        ribs = cmds.group(n = self.ribcage, em = True)
        socket = cmds.group(n = self.chest_up_socket, em = True)
    # move chest & sub a bit higher
        # cmds.move(0,size/2,0, chest+".cv[0:7]", r = True, localSpace = True)
        cmds.move(0,size/2,0, chest_sub+".cv[0:7]", r = True, localSpace = True)
    # make visible through geo like xRay
        for xray in [cog, hip, waist, chest, chest_up]:
            shapes = cmds.listRelatives(xray, children = True, shapes = True)
            for s in shapes:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
        
    # ctrl : (position & parent)
        relations = {
            fly :       ("fly_PRX",     ctrl_socket),
            cog :       ("cog_PRX",     fly),
            body :      ("body_PRX",    cog),
            body_sub :  ("body_PRX",    body),
            hip :       ("hip_PRX",     body_sub),
            hip_sub :   ("hip_PRX",     hip),
            waist :     ("waist_PRX",   body_sub),
            chest:      ("chest_PRX",   body_sub),
            chest_sub : ("chest_PRX",   chest),
            breath_grp :("chest_PRX",   chest_sub),
            chest_up :  ("chest_up_PRX", breath_grp),
            breath :    ("chest_up_PRX", breath_grp),
            ribs :      ("ribcage_PRX", breath_grp),
            socket :    ("chest_up_PRX", chest_up),
            }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos=True)
            cmds.parent(ctrl, relations[ctrl][1])
    # position special ctrls
        cmds.move(0,0,size, self.breath, relative = True, localSpace = True)
        dist = util.distance(self.chest_jnt, self.chest_up_jnt)
        cmds.move(0, dist/2, 0, socket, relative = True)
        
    # expose rotateOrders
        for ctrl in [fly, cog, body, chest]:
            cmds.setAttr(f"{ctrl}.rotateOrder", channelBox = True)
        
####### Attributes
        util.attr_separator([body, hip, chest, breath])
        rig.sub_ctrl_vis(self.body_sub)
        rig.sub_ctrl_vis(self.chest_sub)
        rig.sub_ctrl_vis(self.hip_sub)
        # fly and cog invisible by default
        cmds.addAttr(self.body, longName = "cog_ctrl", attributeType = "double", 
                     defaultValue = 0, min = 0, max = 1)
        cmds.setAttr(f"{self.body}.cog_ctrl", e = True, keyable = True)
        cmds.addAttr(self.body, longName = "fly_ctrl", attributeType = "double", 
                     defaultValue = 0, min = 0, max = 1)
        cmds.setAttr(f"{self.body}.fly_ctrl", e = True, keyable = True)
        # breathing
        cmds.addAttr(self.breath, longName = "chest_breath", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{self.breath}.chest_breath", e = True, keyable = True)
        cmds.addAttr(self.breath, longName = "belly_breath", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{self.breath}.belly_breath", e = True, keyable = True)
        cmds.addAttr(self.breath, longName = "shoulder_breath", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{self.breath}.shoulder_breath", e = True, keyable = True)
    # BODY_TUNING_PANEL
        util.attr_separator("BODY_TUNING", name = "Spine")
        cmds.addAttr(
            "BODY_TUNING", longName = "lungs_sx",
            attributeType = "double", defaultValue = 0.5, min = 0, max = 1)
        cmds.setAttr("BODY_TUNING.lungs_sx", e = True, k = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "lungs_sz",
            attributeType = "double", defaultValue = 0.5, min = 0, max = 1)
        cmds.setAttr("BODY_TUNING.lungs_sz", e = True, k = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "lungs_ty",
            attributeType = "double", defaultValue = 0.3, min = 0)
        cmds.setAttr("BODY_TUNING.lungs_ty", e = True, k = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "lungs_rx",
            attributeType = "double", defaultValue = -1, max = 0)
        cmds.setAttr("BODY_TUNING.lungs_rx", e = True, k = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "hip_pivot_height",
            attributeType = "double", defaultValue = 0)
        cmds.setAttr("BODY_TUNING.hip_pivot_height", e = True, k = True, channelBox = True)
    # connect hip_pivot_height
        cmds.connectAttr("BODY_TUNING.hip_pivot_height", f"{self.hip}.rotatePivotY")
        cmds.connectAttr("BODY_TUNING.hip_pivot_height", f"{self.hip}.scalePivotY")
    # fly and cog visibility default OFF
        fly_shapes = cmds.listRelatives(self.fly, children = True, shapes = True)
        for s in fly_shapes:
            cmds.connectAttr(f"{self.body}.fly_ctrl", f"{s}.v")
        cog_shapes = cmds.listRelatives(self.cog, children = True, shapes = True)
        for s in cog_shapes:
            cmds.connectAttr(f"{self.body}.cog_ctrl", f"{s}.v")
        
    ### Spaces
        rig.spaces(spaces, chest, t_only = True)
        rig.spaces(spaces, chest, r_only = True, split = True)
        # rig.spaces(spaces, hip, r_only = True)
        # rig.spaces(spaces, hip, t_only = True, split = True)
    # Selection Sets
        cmds.sets(fly, cog, body, body_sub, hip, waist, 
                chest, chest_sub, chest_up,
                add = "spine")
    # cleanup
        util.mtx_zero(list(relations))

###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, spaces)

    ### waist setup with buffer group
        waist_twist = util.buffer(self.waist, "twistori_GRP")
        util.mtx_zero(self.waist)
        wpc = cmds.pointConstraint(
                [self.chest_sub, self.hip_sub], waist_twist, 
                mo = True, weight = 0.5, n = "waist_POINT")
        cmds.orientConstraint(
            [self.chest_sub, self.hip_sub], waist_twist,
            offset = (0,0,0), weight = 0.5, n = "waist_ry_ORI")
        cmds.setAttr("waist_ry_ORI.interpType", 2)
        
    ### breath_grp under chest_sub drives the joint
        util.lock(self.breath, ["rx","ry","rz","sx","sy","sz"])
        # ADD ty & attr together
        breath_add = cmds.shadingNode(
                "plusMinusAverage", n = "chestbreath_ty_ADD", au = True)
        cmds.connectAttr(self.breath+".chest_breath", f"{breath_add}.input1D[0]")
        cmds.connectAttr(self.breath+".ty", f"{breath_add}.input1D[1]")
        # MULT by 0.5 to soften manipulation a bit
        breath_mult = cmds.shadingNode(
                "multiplyDivide", n = "chestbreath_soften_MULT", au = True)
        cmds.setAttr(f"{breath_mult}.input2", 0.3, 0.3, 0.3)
        cmds.connectAttr(f"{breath_add}.output1D", f"{breath_mult}.input1X")
        cmds.connectAttr(f"{breath_mult}.outputX", f"{self.breath_drive}.ty")
        breath_drive = breath_mult+".outputX"

    ### bendy chain from pelvis to chest
        # setup
        mod_name = "spine"
        base_driver = self.hip_jnt
        head_driver = self.chest_up_jnt
        forwardaxis = "y"
        upaxis = "-z"
        mid_ctrl = self.waist
        # jointchain
        radius = cmds.joint(base_driver, q = True, radius = True)[0] * 1.5
        rotord = cmds.joint(base_driver, q = True, roo = True)
        spine_jnts = bendy.jointchain(
                mod_name = mod_name,
                number = 8,
                start_obj = base_driver,
                end_obj = head_driver,
                radius = radius,
                rotord = rotord,
                orient = "vertical")
        cmds.sets(spine_jnts[1:-1], add = "bind_joints")
        cmds.sets(spine_jnts, add = "joints")
        cmds.parent(spine_jnts[0], base_driver)
        # ikSpline curve
        crv_points = [self.hip_jnt, spine_jnts[1], self.waist_jnt, 
                      self.chest_jnt, spine_jnts[-2],self.chest_up_jnt]
        curve = bendy.crv(mod_name+"_ikSpline_CRV", crv_points, 3)
        bendy.ikspline(
            mod_name = mod_name, 
            start_jnt = spine_jnts[0],  
            end_jnt = spine_jnts[-1], 
            forwardaxis = forwardaxis, 
            upaxis = upaxis,
            base_driver = base_driver, 
            head_driver = head_driver,
            mid_ctrl = mid_ctrl,
            curve = curve)
        # skin = f"{mod_name}_ikSpline_SKIN"
        # # first 2 CVs driven by hip jnt
        # cmds.skinPercent(skin, curve+".cv[1]", 
        #                  transformValue = (f"{mod_name}_bendy_1_JNT", 1))
        # # top 2 CVs driven by chest
        # cmds.skinPercent(skin, curve+".cv[3]", 
        #                  transformValue = (f"{mod_name}_bendy_3_JNT", 1))
        # cmds.skinPercent(skin, curve+".cv[4]", 
        #                  transformValue = (f"{mod_name}_bendy_3_JNT", 1))
        # util.mtx_hook(self.chest_jnt, f"{mod_name}_bendy_3_JNT", force = True)
        # unbind skin: skinCluster -e  -ub spine_ikSpline_CRVShape
        skin = f"{mod_name}_ikSpline_SKIN"
        # unbind and remake
        cmds.skinCluster("spine_ikSpline_CRVShape", e = True, unbind = True)
        cmds.delete([f"{mod_name}_bendy_1_JNT",
                     f"{mod_name}_bendy_2_JNT",
                     f"{mod_name}_bendy_3_JNT"])
        cmds.skinCluster(
            [self.hip_jnt, self.waist_jnt, self.chest_jnt, self.chest_up_jnt],
            curve,
            name = skin,
            toSelectedBones = True,
            bindMethod = 0,
            skinMethod = 0,
            normalizeWeights = 1,
            maximumInfluences = 1)
        cmds.skinPercent(skin, curve+".cv[0]", 
                         transformValue = ("hip_JNT", 1))
        cmds.skinPercent(skin, curve+".cv[1]", 
                         transformValue = ("hip_JNT", 1))
        cmds.skinPercent(skin, curve+".cv[2]", 
                         transformValue = ("waist_JNT", 1))
        cmds.skinPercent(skin, curve+".cv[3]", 
                         transformValue = ("chest_JNT", 1))
        cmds.skinPercent(skin, curve+".cv[4]", 
                         transformValue = ("chest_up_JNT", 1))
        cmds.skinPercent(skin, curve+".cv[5]", 
                         transformValue = ("chest_up_JNT", 1))
        
    ### parent ribcage to spine_end
        cmds.parent(self.ribcage_jnt, spine_jnts[-2])
    
    ### connect ctrls to joints    
        connections = {
            self.hip_sub : self.hip_jnt,
            self.waist : self.waist_jnt,
            self.breath_drive : self.chest_jnt,
            self.chest_up : self.chest_up_jnt,
            self.ribcage : self.ribcage_jnt}
        for ctrl in list(connections):
            suffix = ctrl.split("_")[-1]
            jnt = connections[ctrl]
            cmds.connectAttr(f"{ctrl}.rotateOrder", f"{jnt}.rotateOrder")
            cmds.parentConstraint(ctrl, jnt, w = 1, n = ctrl.replace(suffix, "PC"))
            cmds.scaleConstraint(ctrl, jnt, offset = (1,1,1), w = 1, 
                                 n = ctrl.replace(suffix, "SCL"))
            
    ### ribcage helper setup
        socket = self.chest_up_socket
        upch_ang = helpers.anglelocs(
                spine_jnts[-1], socket, (0,1,0), (0,0,1), (1,0,0))
        ribs_buff = util.buffer(self.ribcage, "spineFollow_GRP", spine_jnts[-2])
        help_grp = util.buffer(self.ribcage, "helper_GRP")
        lungs_grp = self.ribcage
        util.mtx_zero([ribs_buff, lungs_grp, help_grp])
        cmds.parentConstraint(spine_jnts[-2], ribs_buff, mo = True, weight = 1, 
                              n = "ribcage_PC")
        # ribs_buff inherits global_scale through hierarchy
        helpers.calibrate(upch_ang, help_grp, ["tz","rx","sy"], ["rz"])
        
    ### ribcage scale with breathing -> sx, sz, ty, rx
        dist = util.distance(self.chest_jnt, self.chest_up_jnt)
        # for scale: remap -dist <-> dist into 0.5 <-> 1.5 
            # 1-attr & 1+attr  into  outputMin & outputMax
        # sx
        lung_sx_rmv = util.remap(
                "lung_volume_sx_RMV", breath_drive, -dist, dist, 0.5, 1.5)
        sx_add = cmds.shadingNode(
                "plusMinusAverage", n = "lungs_sxTuning_ADD", au = True)
        cmds.setAttr(sx_add+".input3D[0].input3Dx", 1)
        cmds.connectAttr("BODY_TUNING.lungs_sx", sx_add+".input3D[1].input3Dx")
        cmds.connectAttr(sx_add+".output3Dx", lung_sx_rmv+".outputMax")
        sx_sub = cmds.shadingNode(
                "plusMinusAverage", n = "lungs_sxTuning_SUB", au = True)
        cmds.setAttr(sx_sub+".input3D[0].input3Dx", 1)
        cmds.setAttr(sx_sub+".operation", 2) # subtract
        cmds.connectAttr("BODY_TUNING.lungs_sx", sx_sub+".input3D[1].input3Dx")
        cmds.connectAttr(sx_sub+".output3Dx", lung_sx_rmv+".outputMin")
        # connect into breathing
        cmds.connectAttr(lung_sx_rmv+".outValue", lungs_grp+".sx")
        # sz
        lung_sz_rmv = util.remap(
                "lung_volume_sz_RMV", breath_drive, -dist, dist, 0.5, 1.5)
        sz_add = cmds.shadingNode(
                "plusMinusAverage", n = "lungs_szTuning_ADD", au = True)
        cmds.setAttr(sz_add+".input3D[0].input3Dx", 1)
        cmds.connectAttr("BODY_TUNING.lungs_sz", sz_add+".input3D[1].input3Dx")
        cmds.connectAttr(sz_add+".output3Dx", lung_sz_rmv+".outputMax")
        sz_sub = cmds.shadingNode(
                "plusMinusAverage", n = "lungs_szTuning_SUB", au = True)
        cmds.setAttr(sz_sub+".input3D[0].input3Dx", 1)
        cmds.setAttr(sz_sub+".operation", 2) # subtract
        cmds.connectAttr("BODY_TUNING.lungs_sz", sz_sub+".input3D[1].input3Dx")
        cmds.connectAttr(sz_sub+".output3Dx", lung_sz_rmv+".outputMin")
        # connect into breathing
        cmds.connectAttr(lung_sz_rmv+".outValue", lungs_grp+".sz")
        # for rot or t: tuning_attr mult with breath_ctrl output
        # ty
        ty_mult = cmds.shadingNode(
                "multDoubleLinear", n = "lungs_tyTuning_MULT", au = True)
        cmds.connectAttr("BODY_TUNING.lungs_ty", ty_mult+".input1")
        cmds.connectAttr(breath_drive, ty_mult+".input2")
        # connect into breathing
        cmds.connectAttr(ty_mult+".output", lungs_grp+".ty")
        # rx
        rx_mult = cmds.shadingNode(
                "multDoubleLinear", n = "lungs_rxTuning_MULT", au = True)
        cmds.connectAttr("BODY_TUNING.lungs_rx", rx_mult+".input1")
        cmds.connectAttr(breath_drive, rx_mult+".input2")
        # connect into breathing
        cmds.connectAttr(rx_mult+".output", lungs_grp+".rx")
        
    ### lock attributes
        util.lock([self.chest, self.chest_sub, self.chest_up, self.hip, self.hip_sub, 
                  self.body, self.cog, self.fly],
                  ["sx","sy","sz"])
        util.lock(self.breath, ["tx","tz","rx","ry","rz","sx","sy","sz"])


if __name__ == "__main__":
    
    pass