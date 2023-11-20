import maya.cmds as cmds

from utils import util
from misc import module_template as mt

from body_proxies.proxyspine import ProxySpine
from body_proxies.proxyneck import ProxyNeck
from body_proxies.proxyarm import ProxyArm
from body_proxies.proxyleg import ProxyLeg

from body_modules.base import Base
from body_modules.spine import Spine
from body_modules.neck import Neck
from body_modules.arm import Arms
from body_modules.leg import Legs

class BaseRig(object):
    
    def __init__(self):
        
        # self.char_name = char_name
        return


    def construct_proxy(self):
        # pmodule = ProxyModule()
        pspine = ProxySpine()
        pneck = ProxyNeck()
        parm = ProxyArm()
        pleg = ProxyLeg()
        
        # pmodule.build_proxy(pspine.base_prx)
        pspine.build_base()
        pspine.build_proxy(pspine.base_prx)
        pneck.build_proxy(pspine.base_prx)
        parm.build_proxy(pspine.base_prx)
        pleg.build_proxy(pspine.base_prx)
    
    def construct_rig(self):
        # module = Module()
        base = Base()
        spine = Spine()
        neck = Neck()
        arms = Arms()
        legs = Legs()
        
        # build_rig(
                # joint_socket,
                # ctrl_socket, 
                # ik_ctrlparent, (opt.)
                # [spaces])
        
        base.setup()
        base.build_rig()
        spine.build_rig(
                joint_socket = base.root_jnt, 
                ctrl_socket = base.global_sub_ctrl, 
                spaces = [None])
        # neck.build_rig(
        #         joint_socket = spine.chest_up_jnt, 
        #         ctrl_socket = spine.chest_up_ctrl, 
        #         spaces = [None])
        arms.build_rig(
                joint_socket = spine.chest_up_jnt, 
                ctrl_socket = spine.chest_up_ctrl, 
                spaces = [None])
        legs.build_rig(
                joint_socket = spine.hip_jnt, 
                ctrl_socket = spine.hip_ctrl, 
                spaces = [None])
        
        base = ProxySpine()    
        cmds.hide(base.base_prx)

def test_build(rig = True, bindSkin = True):
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
    character = BaseRig()
    character.construct_proxy()
    if rig == False:
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
            maximumInfluences = 2)


if __name__ == "__main__":
    
    test_build(rig = True, bindSkin = True)

    pass