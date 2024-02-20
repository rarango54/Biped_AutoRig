import maya.cmds as cmds

from utils import util
from misc import module_template as mt

from face_proxies.proxyface import ProxyFace
from face_proxies.proxybrows import ProxyBrows
from face_proxies.proxyeye import ProxyEye
from face_proxies.proxylids import ProxyLids
from face_proxies.proxyorbitals import ProxyOrbitals
from face_proxies.proxymouth import ProxyMouth
from face_proxies.proxynose import ProxyNose
from face_proxies.proxycheeks import ProxyCheeks

from face_modules.face import Face
from face_modules.brows import Brows
from face_modules.eyes import Eyes
from face_modules.lids import Lids
from face_modules.orbitals import Orbitals
from face_modules.mouth import Mouth
from face_modules.nose import Nose
from face_modules.cheeks import Cheeks

class FaceRig(object):
    
    def __init__(self):
        
        # self.char_name = char_name
        return


    def construct_proxy(self):
        # pmodule = ProxyModule()
        pface = ProxyFace()
        peye = ProxyEye()
        pbrows = ProxyBrows()
        plids = ProxyLids()
        porbs = ProxyOrbitals()
        pmouth = ProxyMouth()
        pnose = ProxyNose()
        pcheeks = ProxyCheeks()
        # pteeth = ProxyTeeth()
        # ptongue = ProxyTongue()
        
        # pmodule.build_proxy(pface.base_prx)
        pface.build_base()
        peye.build_proxy(pface.base_prx)
        pbrows.build_proxy(pface.base_prx)
        plids.build_proxy(pface.base_prx)
        porbs.build_proxy(pface.base_prx)
        pmouth.build_proxy(pface.base_prx)
        pnose.build_proxy(pface.base_prx)
        pcheeks.build_proxy(pface.base_prx)
    
    def construct_rig(self):
        ### just for testing ###
        cmds.select(clear = True)
        head_jnt_test = cmds.joint(n = "head_JNT", p = (0,160,0))
        head_ctrl_test = cmds.circle(n = "head_CTRL", nr = (0,0,1), r = 20)[0]
        global_ctrl_test = cmds.circle(n = "global_CTRL", r = 50)[0]
        body_ctrl_test = cmds.circle(n = "body_CTRL", r = 10)[0]
        cmds.matchTransform(head_ctrl_test, head_jnt_test, pos = True)
        cmds.move(0, 100, 0, body_ctrl_test)
        cmds.parent(head_ctrl_test, body_ctrl_test)
        cmds.parent(body_ctrl_test, global_ctrl_test)
        
        # module = Module()
        face = Face()
        brows = Brows()
        eyes = Eyes()
        lids = Lids(tearduct = True)
        orbs = Orbitals()
        mouth = Mouth()
        nose = Nose()
        cheeks = Cheeks()
        
        # build_rig(
                # joint_socket,
                # ctrl_socket, 
                # ik_ctrlparent, (opt.)
                # [spaces])
        
        face.setup()
        mouth.build_rig(
                joint_socket = head_jnt_test, 
                ctrl_socket = head_ctrl_test)
        nose.build_rig(
                joint_socket = head_jnt_test, 
                ctrl_socket = head_ctrl_test,
                lipcorners = ["L_lipcorner_macroOut_GRP", "R_lipcorner_macroOut_GRP"])
        cheeks.build_rig(
                joint_socket = head_jnt_test, 
                ctrl_socket = head_ctrl_test,
                lipcorners = ["L_lipcorner_macroOut_GRP", "R_lipcorner_macroOut_GRP"])
        brows.build_rig(
                joint_socket = head_jnt_test, 
                ctrl_socket = head_ctrl_test)
        eyes.build_rig(
                joint_socket = head_jnt_test, 
                ctrl_socket = head_ctrl_test, 
                spaces = [head_ctrl_test, body_ctrl_test, global_ctrl_test])
        lids.build_rig(
                joint_socket = eyes.socket_jnt, 
                ctrl_socket = eyes.socket)
        orbs.build_rig(
                joint_socket = eyes.socket_jnt, 
                ctrl_socket = eyes.socket,
                lidcorner_ctrls = [lids.corner_in, lids.corner_out])
        
        pface = ProxyFace()
        cmds.hide(pface.base_prx)
### all components which don't deform the geo directly are in "misc_GRP"
        # cmds.hide("misc_GRP")

def test_build(proxy = True, rig = True, bindSkin = True):
    character = FaceRig()
    if proxy == True:
        cmds.file(newFile = True, force = True)
        cmds.modelEditor("modelPanel4", e = True, jointXray = True)
        path = cmds.workspace(q = True, rootDirectory = True )
        bustpath = path + "assets/Minerva_Bust.mb"
        bust = cmds.file(
                bustpath,
                i = True, typ = "mayaBinary", ignoreVersion = True, renameAll = True, 
                namespace = "Minerva_Bust",
                options = "v=0;", importTimeRange = "keep",
                returnNewNodes = True)[0]
        # reposition persp camera
        cmds.xform("persp", t = (108, 168, 102), ro = (-4, 49, 0), a = True)
        cmds.viewFit("perspShape", all = True)
        # vis layer
        cmds.select(
            ["Minerva_Bust:min_body_geo", 
            "Minerva_Bust:min_hair_combined_geo",
            "Minerva_Bust:min_eyes_geo",
            "Minerva_Bust:min_brows_geo",
            "Minerva_Bust:min_lashes_geo",
            "Minerva_Bust:min_teeth_geo",
            "Minerva_Bust:min_tongue_geo",
            "Minerva_Bust:min_highlight_L_geo",
            "Minerva_Bust:min_highlight_R_geo",
            ])
        layer = cmds.createDisplayLayer(name = "bust", number = 1, noRecurse = True)
        cmds.setAttr(f"{layer}.displayType", 2)
        # create proxies
        character.construct_proxy()
    if rig == False:
        return
    # create rig
    character.construct_rig()
    cmds.setAttr("head_JNT.drawStyle", 2) # None
    cmds.hide("face_PRX")
    if bindSkin == False:
        return
    body_joints = cmds.sets("fbind_joints", q = True)
    cmds.select(clear = True)
    cmds.skinCluster(
            body_joints,
            "min_body_geo",
            name = "test_SKIN",
            toSelectedBones = True,
            bindMethod = 0,
            skinMethod = 0,
            normalizeWeights = 1,
            maximumInfluences = 3)


if __name__ == "__main__":
    
    test_build(proxy = False,
               rig = True, 
               bindSkin = False
               )

    pass