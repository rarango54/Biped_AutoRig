import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


h = 158
f = 11

class ProxyCheeks(object):
    
    def __init__(self):
        
        self.module_name = "cheeks"
        
        self.proxy_dict = {
            "L_cheek_inner_PRX" : (
                [1.5, h, f], "sphere", 0.2, "sky", 
                ["rz", "s"]),
            "L_cheek_main_PRX" : (
                [3, h, f], "sphere", 0.3, "blue", 
                ["rz","s"]),
            "L_cheek_bone_PRX" : (
                [4.5, h, f], "sphere", 0.2, "sky", 
                ["rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.inner = self.proxies[0]
        self.main = self.proxies[1]
        self.bone = self.proxies[2]

    def build_proxy(self, proxy_socket):
        pmouth = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        
        rig.proxy_lock(self.proxy_dict)

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyCheeks()
    test.build_proxy(socket)
        
    
    pass