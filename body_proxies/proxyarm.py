import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyArm(object):
    
    def __init__(self):
        
        self.module_name = "L_arm"
        height = 146
        self.proxy_dict = {
            "L_clavicle_PRX" : (
                [1.5, height, 10], "cube", 2, "green", 
                ["r","s"]),
            "L_uparm_PRX" : (
                [17, height, 0], "cube", 3, "green", 
                ["rx","s"]),
            "L_lowarm_PRX" : (
                [46, height, -5], "sphere", 1.5, "grass", 
                ["ty","r","s"]),
            "L_hand_PRX" : (
                [75, height, 0], "octahedron", 1.5, "green", 
                ["ty", "rz", "rx", "s"]),
            "L_hand_end_PRX" : (
                [85, height, 0], "sphere", 1.3, "grass", 
                ["ty","r","s"]),
            "L_polevector_PRX" : (
                [45, height, -65], "octahedron", 2.5, "green", 
                ["t","r","s"]),
        }

    def build_proxy(self, proxy_socket):
        proxies = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)

        clav = proxies[0]
        uparm = proxies[1]
        lowarm = proxies[2]
        hand = proxies[3]
        hand_end = proxies[4]
        polev = proxies[5]
        
        # rotate to anticipate joint orientation
        for i in proxies:
            if i == polev or polev:
                continue
            cmds.rotate(0,90,0, i)
        
        lowarm_buff = util.buffer(lowarm)
        cmds.parent(polev, lowarm_buff)
        cmds.connectAttr(f"{lowarm}.tx", f"{polev}.tx")
        
        cmds.pointConstraint((hand, uparm), lowarm_buff, mo=True,
                n=lowarm_buff.replace("GRP", "POINT"))
        cmds.parent(hand_end, hand)
        cmds.parent([hand, lowarm_buff], uparm)
        
        # line
        line1 = Nurbs.lineconnect(
                self.module_name, (clav, uparm, lowarm, hand, hand_end))
        line2 = Nurbs.lineconnect(f"{self.module_name}_pv", (lowarm, polev))
        cmds.parent((line1, line2), f"{self.module_name}_proxy_GRP")
                        
        rig.proxy_lock(self.proxy_dict)    

if __name__ == "__main__":
    
    test = ProxSpine()
    test.build_base()
    test.build_proxy()
        
    
    pass