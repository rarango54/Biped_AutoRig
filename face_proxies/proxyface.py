import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyFace(object):
    
    def __init__(self):
        
        self.module_name = "face"
        self.base_prx = "face_PRX"

    def build_base(self):
        face_prx = Nurbs.triangle(self.base_prx, 40, 40, "green")
        cmds.move(0, 170, 0, face_prx)
        cmds.connectAttr(face_prx+".sy", face_prx+".sx")
        cmds.connectAttr(face_prx+".sy", face_prx+".sz")
        cmds.setAttr(face_prx+".sx", e=True, cb=True, k=False, l=True)
        cmds.setAttr(face_prx+".sz", e=True, cb=True, k=False, l=True)
    

if __name__ == "__main__":
    
    test = ProxyEye()
    test.build_base()
    test.build_proxy(test.base_prx)
        
    
    pass