import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyNeck(object):
    
    def __init__(self):
        
        self.module_name = "neck"
        self.proxy_dict = {
            "neck_PRX" : (
                [0, 145, 0], "sphere", 1.5, "yellow", 
                ["tx","ry","rz","s"]),
            "head_PRX" : (
                [0, 167, 5], "cube", 3, "red", 
                ["tx","r","s"]),
            "head_end_PRX" : (
                [0, 183, 5], "octahedron", 1, "pink", 
                ["tx","tz","r","s"])
        }
        proxies = list(self.proxy_dict)
        self.neck = proxies[0]
        self.head = proxies[1]
        self.head_end = proxies[2]

    def build_proxy(self, proxy_socket):
        
        pneck = rig.make_proxies(self.proxy_dict, 
            proxy_socket, "neck")
        
        cmds.parent(self.head_end, self.head)
        
        line1 = Nurbs.lineconnect(
                self.module_name, (self.neck, self.head, self.head_end))
        cmds.parent(line1, f"{self.module_name}_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
    

if __name__ == "__main__":
    
    test = ProxSpine()
    test.build_base()
    test.build_proxy()
        
    
    pass