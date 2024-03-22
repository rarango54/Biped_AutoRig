import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

HEIGHT = 150
FORW = 16

class ProxyMouth(object):
    
    def __init__(self):
        
        self.module_name = "mouth"
        
        self.vtx_grp = "lips_edgeloops_GRP"
        lip = 0.2
        self.proxy_dict = {
            "jaw_PRX" : (
                [0, HEIGHT, 0], "sphere", 1, "purple", 
                ["tx","r", "s"]),
            # "jaw_break_PRX" : (
            #     [0, HEIGHT-5, f/2], "sphere", 1, "blue", 
            #     ["tx","r","s"]),
            "chin_PRX" : (
                [0, HEIGHT-5, FORW], "sphere", 0.5, "sky", 
                ["tx","r","s"]),
            "mouth_pivot_PRX" : (
                [0, HEIGHT, FORW*0.8], "sphere", 0.6, "yellow", 
                ["tx","r","s"]),
            # add chin and mentalis joints
            "jaw_ctrl_PRX" : (
                [0, HEIGHT-5, FORW], "circle", 0.6, "red", 
                ["tx","r","s"]),
            "mouth_ctrl_PRX" : (
                [0, HEIGHT, FORW*1.2], "sphere", 0.6, "pink", 
                ["tx","r","s"]),
            "upcenter_PRX" : (
                [0, HEIGHT+1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "upsneer_PRX" : (
                [3, HEIGHT+1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "upout_PRX" : (
                [5, HEIGHT+1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "uppinch_PRX" : (
                [6, HEIGHT+1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowcenter_PRX" : (
                [0, HEIGHT-1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowsneer_PRX" : (
                [3, HEIGHT-1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowout_PRX" : (
                [5, HEIGHT-1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowpinch_PRX" : (
                [6, HEIGHT-1, FORW], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "corner_PRX" : (
                [7, HEIGHT, FORW], "sphere", lip*2, "red", 
                ["rx","rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.jaw = self.proxies[0]
        # self.jawb = self.proxies[1]
        self.jawchin = self.proxies[1]
        self.mpivot = self.proxies[2]
        self.jawctrl = self.proxies[3]
        self.mouthctrl = self.proxies[4]
        
        self.upcenter = self.proxies[5]
        self.upsneer = self.proxies[6]
        self.upout = self.proxies[7]
        self.uppinch = self.proxies[8]
        
        self.lowcenter = self.proxies[9]
        self.lowsneer = self.proxies[10]
        self.lowout = self.proxies[11]
        self.lowpinch = self.proxies[12]
        
        self.corner = self.proxies[13]

    def build_proxy(self, proxy_socket):
        pmouth = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        
        cmds.parent(self.jawchin, self.jaw)
        
        crv = Nurbs.lineconnect("jaws_prx", self.proxies[0:1])
        cmds.parent(crv, self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
        
    # upLip & lowLip edgeloops -> 9 locators each
        vtx_grp = cmds.group(
                n = self.vtx_grp, em = True, p = self.module_name+"_proxy_GRP")
        
        for part in ["uplip", "lowlip"]:
            incr = 2
            gap = 0
            lipforw = FORW + 2
            if part == "uplip":
                height = HEIGHT + 2
                loops = 19
                corners = True
            else:
                height = HEIGHT - 2
                loops = 15 # without corners
                corners = None
            for nr in range(loops):
                if corners:
                    if nr == 0:
                        name = f"R_lipcorner_loop_LOC"
                        size = 0.6
                    elif nr == loops-1:
                        name = f"L_lipcorner_loop_LOC"
                        size = 0.6
                    else:
                        name = f"{part}_{nr}_loop_LOC"
                        size = 0.3
                else:
                    name = f"{part}_{nr+1}_loop_LOC"
                    size = 0.3
                loc = cmds.spaceLocator(n = name)[0]
                cmds.setAttr(loc+"Shape.localScale", size, size, size)
                cmds.move(gap, height, lipforw*1.2, loc)
                cmds.parent(loc, vtx_grp)
                gap = gap + incr
                
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyMouth()
    test.build_proxy(socket)
        
    
    pass