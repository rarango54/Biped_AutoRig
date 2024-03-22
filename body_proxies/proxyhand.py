import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyHand(object):
    
    def __init__(self, proxy_socket = None):
        self.module_name = "hand"
        self.proxy_dict = {
            "L_finger_meta_PRX" : (
                [0, 0, 4], "cube", 1.2, "purple", 
                ["s"]),
            "L_finger_1_PRX" : (
                [0, 0, 12], "sphere", 0.6, "purple", 
                ["rz","s"]),
            "L_finger_2_PRX" : (
                [0, 0, 16], "sphere", 0.6, "purple", 
                ["tx","ry","rz","s"]),
            "L_finger_3_PRX" : (
                [0, 0, 18], "sphere", 0.6, "purple", 
                ["tx","ry","rz","s"]),
            "L_finger_end_PRX" : (
                [0, 0, 20], "sphere", 0.4, "purple", 
                ["tx","ty","r","s"])}
        
        self.finger = list(self.proxy_dict)
        self.index = [x.replace("finger", "index") for x in self.finger]
        self.middle = [x.replace("finger", "middle") for x in self.finger]
        self.ring = [x.replace("finger", "ring") for x in self.finger]
        self.pinky = [x.replace("finger", "pinky") for x in self.finger]
        self.thumb = [x.replace("finger", "thumb") for x in self.finger]
        self.thumb.remove("L_thumb_3_PRX")
        self.finger_prxs = self.index[:-1]
        self.finger_prxs.extend(self.middle[:-1])
        self.finger_prxs.extend(self.ring[:-1])
        self.finger_prxs.extend(self.pinky[:-1])
        self.finger_prxs.extend(self.thumb[:-1])
        self.onlyfinger_prxs = self.index[1:-1]
        self.onlyfinger_prxs.extend(self.middle[1:-1])
        self.onlyfinger_prxs.extend(self.ring[1:-1])
        self.onlyfinger_prxs.extend(self.pinky[1:-1])
        self.onlyfinger_prxs.extend(self.thumb[1:-1])
        
        if proxy_socket:
            self.build_proxy(proxy_socket)

    def build_proxy(self, proxy_socket):
        hand = cmds.group(n = "hand_proxy_GRP", em = True)
        # gap between finger chains
        gap = 2
        fingers = []
        for nr, name in enumerate(["index", "middle", "ring", "pinky", "thumb"]):
            # run make proxies
            finger = rig.make_proxies(self.proxy_dict, 
                proxy_socket, name)
            meta = finger[0]
            knuckle = finger[1]
            middle = finger[2]
            tip = finger[3]
            end = finger[4]
            grp = f"{name}_proxy_GRP"
            fingers.append(grp)
            # parent and rig
            cmds.parent(end, tip)
            cmds.parent(tip, middle)
            cmds.parent(middle, knuckle)
            cmds.parent(knuckle, meta)
            # knubuff = util.buffer(knuckle)
            # cmds.parentConstraint(
            #         meta, knubuff, mo = True, skipRotate = ["x","y","z"], weight = 1)
            # line connect
            line = Nurbs.lineconnect(name, finger)
            cmds.parent(line, grp)
            # move into position
            if nr == 0: # index
                cmds.move(-gap,0,-0.2*gap, finger[0], relative = True)
            if nr == 2: # ring
                cmds.move(gap,0,-0.5*gap, finger[0], relative = True)
            if nr == 3: # pinky
                cmds.move(2*gap,0,-gap, finger[0], relative = True)
            if nr == 4: # thumb
                cmds.setAttr(finger[0] + ".rotateOrder", 2)
                cmds.move(-1.5*gap, -0.5*gap, -2.5*gap, finger[0], relative = True)
                cmds.rotate(45, -45, 45, finger[0])
            rig.proxy_lock(self.proxy_dict)  
            # rename PRXs
            for prx in finger:
                new_name = prx.replace("finger", name)
                cmds.rename(prx, new_name)
            # group all chain_grps into the hand grp
            cmds.parent(grp, hand)
        # thumb with one less proxy
        cmds.delete("L_thumb_end_PRX")
        cmds.delete("thumb_line_CRV.cv[4]")
        cmds.rename("L_thumb_3_PRX", "L_thumb_end_PRX")
        cmds.parent(hand, proxy_socket, relative = True)
        cmds.rotate(0, 90, 0, hand, relative = True)
        
        
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "socket", em = True)
    phand = ProxyHand()
    phand.build_proxy(socket)

    print(phand.thumb)
    
    pass