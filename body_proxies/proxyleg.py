import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyLeg(object):
    
    def __init__(self):
        
        self.module_name = "L_leg"
        side = 10
        knee_h = 50
        self.proxy_dict = {
            "L_upleg_PRX" : (
                [side, 95, 0], "cube", 3, "green", 
                ["r", "s"]),
            "L_knee_PRX" : (
                [side, knee_h+5, 4], "sphere", 1.5, "grass", 
                ["t", "r", "s"]),
            "L_lowleg_PRX" : (
                [side, knee_h-5, 4], "sphere", 1.5, "grass", 
                ["tx", "r", "s"]),
            "L_foot_PRX" : (
                [side, 7, 0], "cube", 3, "green", 
                ["tx", "tz", "r", "s"]),
            "L_toes_PRX" : (
                [side, 1, 13], "octahedron", 1.5, "green", 
                ["tx", "r", "s"]),
            "L_toes_end_PRX" : (
                [side, 1, 21], "sphere", 1.3, "grass", 
                ["tx", "ty", "r", "s"]),
            "L_knee_master_PRX" : (
                [side, knee_h, 4], "cube", 3, "green", 
                ["tx", "r", "sx", "sz"]),
            "L_legpv_PRX" : (
                [side, knee_h, 65], "arrow", 4, "green", 
                ["t", "r", "s"]),
        }
        proxies = list(self.proxy_dict)
        self.upleg = proxies[0]
        self.knee = proxies[1]
        self.lowleg = proxies[2]
        self.foot = proxies[3]
        self.toes = proxies[4]

    def build_proxy(self, proxy_socket):
        proxies = rig.make_proxies(self.proxy_dict, proxy_socket, self.module_name)

        upleg = proxies[0]
        knee = proxies[1]
        lowleg = proxies[2]
        foot = proxies[3]
        toes = proxies[4]
        toes_end = proxies[5]
        knee_master = proxies[6]
        polev = proxies[7]
        
        cmds.parent((knee, lowleg), knee_master)
        cmds.parent(toes, foot)
        cmds.parent(toes_end, toes)
        cmds.pointConstraint(upleg, foot, mo = True, skip = "y", weight = 1)
        cmds.pointConstraint(upleg, knee_master, mo = True, skip = ("y", "z"), weight = 1)
        cmds.pointConstraint(knee_master, polev, mo = True, weight = 1)
        
        line1 = Nurbs.lineconnect(
                self.module_name, (upleg, knee, lowleg, foot, toes, toes_end))
        line2 = Nurbs.lineconnect(f"{self.module_name}_pv", (knee_master, polev))
        cmds.parent((line1, line2), f"{self.module_name}_proxy_GRP")
                        
        rig.proxy_lock(self.proxy_dict)    

if __name__ == "__main__":
    
    test = ProxSpine()
    test.build_base()
    test.build_proxy()
        
    
    pass