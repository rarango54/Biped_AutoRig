import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


h = 154
f = 10.5

class ProxyTeeth(object):
    
    def __init__(self):
        
        self.module_name = "teeth"
        
        self.proxy_dict = {
            "upteeth_PRX" : (
                [0, h, f], "sphere", 0.3, "yellow", 
                ["tx","ry","rz", "s"]),
            "L_upteeth_1_PRX" : (
                [0.5, h, f], "sphere", 0.2, "brown", 
                ["r","s"]),
            "L_upteeth_2_PRX" : (
                [1, h, f], "sphere", 0.2, "brown", 
                ["r","s"]),
            "L_upteeth_3_PRX" : (
                [1.5, h, f], "sphere", 0.2, "brown", 
                ["r","s"]),
            "L_upteeth_4_PRX" : (
                [2, h, f], "sphere", 0.2, "brown", 
                ["r","s"]),
        }
        self.upprx = list(self.proxy_dict)
        self.lowprx = [x.replace("up", "low") for x in self.upprx]
        self.upmain = self.upprx[0]
        self.lowmain = self.lowprx[0]

    def build_proxy(self, proxy_socket):
        pteeth = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.upprx:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        for p in pteeth[1:]:
            cmds.parent(p, pteeth[0])
        
        rig.proxy_lock(self.proxy_dict)
        lowteeth = cmds.duplicate(pteeth[0], n = self.lowmain, 
                                  renameChildren = True)
        for t in lowteeth:
            suffix = t.split("_")[-1]
            lowname = t.replace("up", "low")
            newname = lowname.replace(suffix, "PRX")
            cmds.rename(t, newname)
        cmds.move(0,1,0, self.lowprx[0], r = True)

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyTeeth()
    test.build_proxy(socket)
        
    
    pass