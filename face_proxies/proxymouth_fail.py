import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyMouth(object):
    
    def __init__(self):
        
        self.module_name = "mouth"
        
        self.vtx_grp = "lips_vtx_GRP"
        h = 150
        f = 16
        lip = 0.2
        self.proxy_dict = {
            "jaw_PRX" : (
                [0, h, 0], "sphere", 1, "purple", 
                ["tx","r", "s"]),
            "jaw_break_PRX" : (
                [0, h-5, f/2], "sphere", 1, "blue", 
                ["tx","r","s"]),
            "chin_PRX" : (
                [0, h-5, f], "sphere", 0.5, "sky", 
                ["tx","r","s"]),
            "mouth_pivot_PRX" : (
                [0, h, f*0.8], "sphere", 0.6, "yellow", 
                ["tx","r","s"]),
            # add chin and mentalis joints
            "jaw_ctrl_PRX" : (
                [0, h-5, f], "circle", 0.6, "red", 
                ["tx","r","s"]),
            "mouth_ctrl_PRX" : (
                [0, h, f*1.2], "sphere", 0.6, "pink", 
                ["tx","r","s"]),
            "upcenter_PRX" : (
                [0, h+1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "upsneer_PRX" : (
                [3, h+1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "upout_PRX" : (
                [5, h+1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "uppinch_PRX" : (
                [6, h+1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowcenter_PRX" : (
                [0, h-1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowsneer_PRX" : (
                [3, h-1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowout_PRX" : (
                [5, h-1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "lowpinch_PRX" : (
                [6, h-1, f], "sphere", lip, "pink", 
                ["rx","rz","s"]),
            "corner_PRX" : (
                [7, h, f], "sphere", lip*2, "red", 
                ["rx","rz","s"]),
        }
        self.proxies = list(self.proxy_dict)
        self.jaw = self.proxies[0]
        self.jawb = self.proxies[1]
        self.jawchin = self.proxies[2]
        self.mouth = self.proxies[3]
        self.jawctrl = self.proxies[4]
        self.mouthctrl = self.proxies[5]
        
        self.upcenter = self.proxies[6]
        self.upsneer = self.proxies[7]
        self.upout = self.proxies[8]
        self.uppinch = self.proxies[9]
        
        self.lowcenter = self.proxies[10]
        self.lowsneer = self.proxies[11]
        self.lowout = self.proxies[12]
        self.lowpinch = self.proxies[13]
        
        self.corner = self.proxies[14]

    def build_proxy(self, proxy_socket):
        pmouth = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        for p in self.proxies:
            cmds.setAttr(p+"Shape.localScale", 0.2, 0.2, 0.2)
        
        cmds.parent(self.jawchin, self.jawb)
        
        crv = Nurbs.lineconnect("jaws_prx", self.proxies[0:2])
        cmds.parent(crv, self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
        
    # upLip & lowLip edgeloops -> 9 locators each
        vtx_grp = cmds.group(
                n = self.vtx_grp, em = True, p = self.module_name+"_proxy_GRP")
        
        for part in ["uplip", "lowlip"]:
            incr = 2
            gap = 0
            f = 18
            if part == "uplip":
                h = 152
                rang = 10
            else:
                h = 148
                rang = 9
            for nr in range(rang):
                if nr == 0:
                    name = f"{part}center_vtx_LOC"
                elif nr == 9:
                    name = f"lipcorner_vtx_LOC"
                else:
                    name = f"{part}_{nr}_vtx_LOC"
                loc = cmds.spaceLocator(n = name)[0]
                cmds.setAttr(loc+"Shape.localScale", 0.3, 0.3, 0.3)
                cmds.move(gap, h, f*1.2, loc)
                cmds.parent(loc, vtx_grp)
                gap = gap + incr
                
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyMouth()
    test.build_proxy(socket)
        
    
    pass