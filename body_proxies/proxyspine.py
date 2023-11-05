import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxySpine(object):
    
    def __init__(self):
        
        # self.char_height = char_height
        
        self.module_name = "spine"
        self.base_prx = "global_PRX"
        hip = 100
        self.proxy_dict = {
            "fly_PRX" : (
                [0, 135, 0], "sphere", 4, "blue", 
                ["tx","ry","rz","s"]),
            "cog_PRX" : (
                [0, 115, 0], "sphere", 3, "blue", 
                ["tx","ry","rz","s"]),
            "body_PRX" : (
                [0, hip, 0], "cube", 10, "yellow", 
                ["tx","ry","rz","s"]),
            "hip_PRX" : (
                [0, hip, 0], "cube", 5, "sky", 
                ["tx","r","s"]),
            "waist_PRX" : (
                [0, hip+7, 0], "sphere", 2, "sky", 
                ["tx","r","s"]),
            "chest_PRX" : (
                [0, hip+14, 0], "sphere", 2, "sky", 
                ["tx","r","s"]),
            "chest_up_PRX" : (
                [0, hip+33, 0], "octahedron", 1.5, "sky", 
                ["tx","r","s"]),
            # "spine_end_PRX" : (
            #     [0, 155, 0], "octahedron", 2, "sky", 
            #     ["tx","r","s"])
        }
        
    def build_base(self):
        global_prx = Nurbs.double_circle(self.base_prx, 50)
        cmds.connectAttr(f"{global_prx}.sy", f"{global_prx}.sx")
        cmds.connectAttr(f"{global_prx}.sy", f"{global_prx}.sz")
        cmds.setAttr(f"{global_prx}.sx", e=True, cb=True, k=False, l=True)
        cmds.setAttr(f"{global_prx}.sz", e=True, cb=True, k=False, l=True)
        

    def build_proxy(self, proxy_socket):
        
        spine = rig.make_proxies(self.proxy_dict, 
            proxy_socket, "spine")
        # hip & spine_end drive the 3 middle spine proxies
        hip = spine[3]
        waist = spine[4]
        chest = spine[5]
        chest_up = spine[6]
        end = spine[-1]
        for nr, i in enumerate(spine[4:-1]):
            cmds.parent(i, hip)
            buff = util.buffer_grp(i, "buffer_prx_GRP")
            pc = cmds.pointConstraint((end, hip), buff, 
                n=i.replace("PRX", "POINT"))[0]
            w0 = (nr+1)/3
            w1 = 1-w0
            cmds.setAttr(f"{pc}.{end}W0", w0)
            cmds.setAttr(f"{pc}.{hip}W1", w1)
        cmds.parent((hip, end), spine[0])
        
        line1 = Nurbs.lineconnect(
                self.module_name, (hip, waist, chest, chest_up, end))
        cmds.parent(line1, f"{self.module_name}_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
    

if __name__ == "__main__":
    
    test = ProxSpine()
    test.build_base()
    test.build_proxy()
        
    
    pass