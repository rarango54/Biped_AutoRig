import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyOrbitals(object):
    
    def __init__(self):
        
        self.module_name = "orbitals"
        
        self.vtx_grp = "L_orb_vtx_GRP"
        
        h = 1.5
        self.proxy_dict = {
            "L_orbcorner_in_PRX" : (
                [-1.8, 0, 0], "sphere", 0.1, "red", 
                ["rx", "s"]),
            "L_uporb_in_PRX" : (
                [-1, h*0.85, 0], "sphere", 0.1, "pink", 
                ["rx","s"]),
            "L_uporb_main_PRX" : (
                [0, h, 0], "sphere", 0.1, "red", 
                ["rx","s"]),
            "L_uporb_out_PRX" : (
                [1, h*0.85, 0], "sphere", 0.1, "pink", 
                ["rx","s"]),
            "L_orbcorner_out_PRX" : (
                [1.7, 0, 0], "sphere", 0.1, "red", 
                ["rx","s"]),
            "L_loworb_in_PRX" : (
                [-1, -h*0.85, 0], "sphere", 0.1, "pink", 
                ["rx","s"]),
            "L_loworb_main_PRX" : (
                [0, -h, 0], "sphere", 0.1, "red", 
                ["rx","s"]),
            "L_loworb_out_PRX" : (
                [1, -h*0.85, 0], "sphere", 0.1, "pink", 
                ["rx","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.corner_in = self.proxies[0]
        self.uporb_in = self.proxies[1]
        self.uporb_main = self.proxies[2]
        self.uporb_out = self.proxies[3]
        self.corner_out = self.proxies[4]
        self.loworb_in = self.proxies[5]
        self.loworb_main = self.proxies[6]
        self.loworb_out = self.proxies[7]

    def build_proxy(self, proxy_socket):
        mov_grp = cmds.group(n = "position_orbsprx_GRP", em = True)
        cmds.parent(mov_grp, proxy_socket)
        porbs = rig.make_proxies(self.proxy_dict, 
            mov_grp, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.1, 0.1, 0.1)
# degree 2 or 3?? that is the question
        deg = 2
        up_crv = Nurbs.lineconnect("uporb_prx", self.proxies[:5], degree = deg)
        low = [self.corner_in, self.loworb_in, self.loworb_main, 
               self.loworb_out, self.corner_out]
        low_crv = Nurbs.lineconnect("loworb_prx", low, degree = deg)
        cmds.parent([up_crv, low_crv], self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
        
    # create 24 locators for vtx selection replacement
        vtx_grp = cmds.group(n = self.vtx_grp, em = True, p = mov_grp)
        incr = 2
        gap = 0
        for nr in range(24):
            loc = cmds.spaceLocator(n = f"orbs_vtx_{nr+1}_LOC")[0]
            cmds.setAttr(loc+"Shape.localScale", 0.1, 0.1, 0.1)
            cmds.move(gap, 2, 0, loc)
            cmds.parent(loc, vtx_grp)
            gap = gap + incr
        cmds.move(0, 0, -2, mov_grp, r = True)
        cmds.move(3, 160, 12, mov_grp, r = True)
            
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = Proxyorbs()
    test.build_proxy(socket)
        
    
    pass