import maya.cmds as cmds

from utils import util
from misc import module_template as mt

from body_proxies.proxyspine import ProxySpine
from body_proxies.proxyneck import ProxyNeck
from body_proxies.proxyarm import ProxyArm
from body_proxies.proxyleg import ProxyLeg
from body_proxies.proxyhand import ProxyHand

from body_modules.base import Base
from body_modules.spine import Spine
from body_modules.neck import Neck
from body_modules.arm import Arms
from body_modules.leg import Legs
from body_modules.hand import Hands

class BodyRig(object):
    
    def __init__(self):
        
        # self.char_name = char_name
        return


    def construct_proxy(self):
        # pmodule = ProxyModule()
        pspine = ProxySpine()
        pneck = ProxyNeck()
        parm = ProxyArm()
        pleg = ProxyLeg()
        phand = ProxyHand()
        
        # pmodule.build_proxy(pspine.base_prx)
        pspine.build_base()
        pspine.build_proxy(pspine.base_prx)
        pneck.build_proxy(pspine.base_prx)
        parm.build_proxy(pspine.base_prx)
        pleg.build_proxy(pspine.base_prx)
        phand.build_proxy(parm.hand)
        
    def construct_skeleton(self):
        base = Base()
        spine = Spine()
        neck = Neck()
        arms = Arms()
        legs = Legs()
        hands = Hands()
        
        base.setup()
        base.build_rig()
        spine.skeleton(joint_socket = base.root_jnt)
        neck.skeleton(joint_socket = spine.chest_up_jnt)
        arms.skeleton(joint_socket = spine.chest_up_jnt)
        legs.skeleton(joint_socket = spine.hip_jnt)
        hands.skeleton(joint_socket = arms.hand_jnt)
        
        base = ProxySpine()
        cmds.hide(base.base_prx)
    
    def construct_rig(self):
        # module = Module()
        base = Base()
        spine = Spine()
        neck = Neck()
        arms = Arms()
        legs = Legs()
        hands = Hands()
        
        # build_rig(
                # joint_socket,
                # ctrl_socket, 
                # ik_ctrlparent, (opt.)
                # [spaces])
        
        base.setup()
        base.build_rig()
        spine.build_rig(
                joint_socket = base.root_jnt, 
                ctrl_socket = base.global_sub, 
                spaces = [spine.body_sub, base.global_sub])
        neck.build_rig(
                joint_socket = spine.chest_up_jnt, 
                ctrl_socket = spine.chest_up_socket, 
                spaces = [base.global_sub, spine.body_sub, spine.breath_drive])
        arms.build_rig(
                joint_socket = spine.chest_up_jnt, 
                ctrl_socket = spine.chest_up_socket, 
                spaces = [base.global_sub, spine.body_sub, spine.breath_drive,
                          arms.shoulder_ik])
        legs.build_rig(
                joint_socket = spine.hip_jnt, 
                ctrl_socket = spine.hip_sub, 
                spaces = [base.global_sub, spine.body_sub, spine.hip_sub,
                          legs.hipjoint_ik])
        hands.build_rig(
                joint_socket = arms.hand_jnt,
                ctrl_socket = base.global_sub, 
                spaces = None)
        
        base = ProxySpine()
        cmds.hide(base.base_prx)
    # all components which don't deform the geo directly are in "misc_GRP"
        cmds.hide("misc_GRP")

def test_build(proxy = True, skeleton = False, rig = True, bindSkin = True):
    character = BodyRig()
    if proxy == True:
        cmds.file(newFile = True, force = True)
        cmds.modelEditor("modelPanel4", e = True, jointXray = True)
        path = cmds.workspace(q = True, rootDirectory = True )
        fbxpath = path + "assets/skinningDummy.fbx"
        dummy = cmds.file(
                fbxpath,
                i = True, typ = "FBX", ignoreVersion = True, renameAll = True, 
                namespace = "skinningDummy",
                options = "fbx", importTimeRange = "keep",
                returnNewNodes = True)[0]
        cmds.select(dummy)
        layer = cmds.createDisplayLayer(name = "skinDummy", number = 1, noRecurse = True)
        cmds.setAttr(f"{layer}.displayType", 2)
        # create proxies
        character.construct_proxy()
    if rig == False:
        if skeleton == True:
            character.construct_skeleton()
        return
    # create rig
    character.construct_rig()
    if bindSkin == False:
        return
    body_joints = cmds.sets("bind_joints", q = True)
    cmds.select(clear = True)
    cmds.skinCluster(
            body_joints,
            dummy,
            name = "test_SKIN",
            toSelectedBones = True,
            bindMethod = 0,
            skinMethod = 0,
            normalizeWeights = 1,
            maximumInfluences = 3)
    cmds.parent(dummy, "geo_GRP")


if __name__ == "__main__":
    
    test_build(proxy = False,
               skeleton = False, 
               rig = True, 
               bindSkin = False
               )

    pass