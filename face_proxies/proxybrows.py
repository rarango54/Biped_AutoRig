import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyBrows(object):
    
    def __init__(self):
        
        self.module_name = "brows"
        
        self.vtx_grp = "L_brow_vtx_GRP"
        
        h = 166
        f = 12
        self.proxy_dict = {
            "L_brow_in_PRX" : (
                [1, h, f], "sphere", 0.4, "green", 
                ["rz", "s"]),
            "L_brow_curr_PRX" : (
                [1.6, h, f], "sphere", 0.2, "grass", 
                ["rz","s"]),
            "L_brow_mid_PRX" : (
                [2.75, h, f], "sphere", 0.3, "grass", 
                ["rz","s"]),
            "L_brow_out_PRX" : (
                [4.5, h, f], "sphere", 0.4, "green", 
                ["rz","s"]),
            "L_brow_end_PRX" : (
                [5.3, h-1, f], "sphere", 0.2, "grass", 
                ["rz","s"]),
            "L_brow_anchor_PRX" : (
                [6.1, h-2, f], "sphere", 0.2, "green", 
                ["rz","s"]),
            "L_brow_main_PRX" : (
                [2.75, h, f*1.1], "octahedron", 0.3, "purple", 
                ["rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.bin = self.proxies[0]
        self.bcurr = self.proxies[1]
        self.bmid = self.proxies[2]
        self.bout = self.proxies[3]
        self.bend = self.proxies[4]
        self.banchor = self.proxies[5]
        self.bmain = self.proxies[6]

    def build_proxy(self, proxy_socket):
        pbrows = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        line1 = Nurbs.lineconnect(
                self.module_name, (self.bin, self.bcurr, self.bmid, self.bout, 
                self.bend, self.banchor))
        cmds.parent(line1, self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
        
    # create 11 locators for vtx selection replacement
        vtx_grp = cmds.group(
                n = self.vtx_grp, em = True, p = self.module_name+"_proxy_GRP")
        incr = 2
        gap = 0
        for nr in range(11):
            loc = cmds.spaceLocator(n = f"brows_vtx_{nr+1}_LOC")[0]
            cmds.setAttr(loc+"Shape.localScale", 0.3, 0.3, 0.3)
            cmds.move(gap, 0, 0, loc)
            cmds.parent(loc, vtx_grp)
            gap = gap + incr
            
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyBrows()
    test.build_proxy(socket)
        
    
    pass