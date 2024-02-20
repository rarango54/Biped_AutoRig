import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


h = 157
f = 10

class ProxyNose(object):
    
    def __init__(self):
        
        self.module_name = "nose"
        
        self.proxy_dict = {
            "nose_base_PRX" : (
                [0, h, f], "sphere", 0.5, "yellow", 
                ["tx","rz", "s"]),
            "nose_tip_PRX" : (
                [0, h, f+3], "sphere", 0.1, "green", 
                ["tx","rz","s"]),
            "L_nostril_PRX" : (
                [1, h, f+1], "sphere", 0.2, "green", 
                ["rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.base = self.proxies[0]
        self.tip = self.proxies[1]
        self.nostril = self.proxies[2]

    def build_proxy(self, proxy_socket):
        pmouth = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        
        rig.proxy_lock(self.proxy_dict)

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyNose()
    test.build_proxy(socket)
        
    
    pass