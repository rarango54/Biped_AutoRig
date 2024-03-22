import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


h = 155
f = 7

class ProxyTongue(object):
    
    def __init__(self):
        
        self.module_name = "tongue"
        
        self.proxy_dict = {
            "tongue_base_PRX" : (
                [0, h, f], "sphere", 0.2, "violet", 
                ["tx","rz", "s"]),
            "tongue_1_PRX" : (
                [0, h, f+0.4], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
            "tongue_2_PRX" : (
                [0, h, f+0.8], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
            "tongue_3_PRX" : (
                [0, h, f+1.2], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
            "tongue_4_PRX" : (
                [0, h, f+1.6], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
            "tongue_5_PRX" : (
                [0, h, f+2], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
            "tongue_6_PRX" : (
                [0, h, f+2.4], "sphere", 0.1, "purple", 
                ["tx","rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.base = self.proxies[0]
        self.mid = self.proxies[3]
        self.tip = self.proxies[-1]

    def build_proxy(self, proxy_socket):
        ptongue = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        
        rig.proxy_lock(self.proxy_dict)

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyTongue()
    test.build_proxy(socket)
        
    
    pass