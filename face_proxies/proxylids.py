import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyLids(object):
    
    def __init__(self):
        
        self.module_name = "lids"
        
        self.vtx_grp = "L_lid_vtx_GRP"
        
        h = 1
        self.proxy_dict = {
            "L_lidcorner_in_PRX" : (
                [-1.65, 0, 0], "sphere", 0.1, "blue", 
                ["rx", "s"]),
            "L_uplid_tear_PRX" : (
                [-1.4, h/5, 0], "sphere", 0.06, "sky", 
                ["rx","s"]),
            "L_uplid_in_PRX" : (
                [-0.9, h*0.85, 0], "sphere", 0.1, "sky", 
                ["rx","s"]),
            "L_uplid_main_PRX" : (
                [0, h, 0], "sphere", 0.1, "blue", 
                ["rx","s"]),
            "L_uplid_out_PRX" : (
                [0.9, h*0.85, 0], "sphere", 0.1, "sky", 
                ["rx","s"]),
            "L_lidcorner_out_PRX" : (
                [1.5, 0, 0], "sphere", 0.1, "blue", 
                ["rx","s"]),
            "L_lowlid_tear_PRX" : (
                [-1.4, -h/5, 0], "sphere", 0.06, "sky", 
                ["rx","s"]),
            "L_lowlid_in_PRX" : (
                [-0.9, -h*0.85, 0], "sphere", 0.1, "sky", 
                ["rx","s"]),
            "L_lowlid_main_PRX" : (
                [0, -h, 0], "sphere", 0.1, "blue", 
                ["rx","s"]),
            "L_lowlid_out_PRX" : (
                [0.9, -h*0.85, 0], "sphere", 0.1, "sky", 
                ["rx","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.corner_in = self.proxies[0]
        self.uplid_tear = self.proxies[1]
        self.uplid_in = self.proxies[2]
        self.uplid_main = self.proxies[3]
        self.uplid_out = self.proxies[4]
        self.corner_out = self.proxies[5]
        self.lowlid_tear = self.proxies[6]
        self.lowlid_in = self.proxies[7]
        self.lowlid_main = self.proxies[8]
        self.lowlid_out = self.proxies[9]

    def build_proxy(self, proxy_socket):
        mov_grp = cmds.group(n = "position_lidsprx_GRP", em = True)
        cmds.parent(mov_grp, proxy_socket)
        plids = rig.make_proxies(self.proxy_dict, 
            mov_grp, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.1, 0.1, 0.1)
# degree 2 or 3?? that is the question
        deg = 2
        up_crv = Nurbs.lineconnect("uplid_prx", self.proxies[:6], degree = deg)
        low = [self.corner_in, self.lowlid_tear, self.lowlid_in, self.lowlid_main, 
               self.lowlid_out, self.corner_out]
        low_crv = Nurbs.lineconnect("lowlid_prx", low, degree = deg)
        cmds.parent([up_crv, low_crv], self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
        
    # create 24 locators for vtx selection replacement
        vtx_grp = cmds.group(n = self.vtx_grp, em = True, p = mov_grp)
        incr = 2
        gap = 0
        for nr in range(24):
            loc = cmds.spaceLocator(n = f"lids_vtx_{nr+1}_eLOC")[0]
            cmds.setAttr(loc+"Shape.localScale", 0.1, 0.1, 0.1)
            cmds.move(gap, 0, 0, loc)
            cmds.parent(loc, vtx_grp)
            gap = gap + incr
        cmds.move(0, 0, -2, mov_grp, r = True)
        cmds.move(3, 160, 12, mov_grp, r = True)
            
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyLids()
    test.build_proxy(socket)
        
    
    pass