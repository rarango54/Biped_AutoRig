import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class ProxyEye(object):
    
    def __init__(self):
        
        self.module_name = "eye"
        h = 160
        x = 3
        self.proxy_dict = {
            "L_eye_PRX" : (
                [x, h, 9], "sphere", 1.5, "red", 
                ["rx","rz"]),
            "L_iris_PRX" : (
                [x, h, 10.3], "cube", 0.5, "pink", 
                ["tx","ty","r","s"]),
            "L_pupil_PRX" : (
                [x, h, 10.3], "sphere", 0.1, "pink", 
                ["t","r","s"]),
            "aim_PRX" : (
                [x, h, 60], "octahedron", 1.5, "red", 
                ["tx","ty","r","s"]),
        }
        proxies = list(self.proxy_dict)
        self.eye = proxies[0]
        self.iris = proxies[1]
        self.pupil = proxies[2]
        self.aim = proxies[-1]

    def build_proxy(self, proxy_socket):
        
        peye = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        
        cmds.parent(self.iris, self.eye)
        cmds.parent(self.pupil, self.iris)
        
        cmds.pointConstraint(self.eye, self.aim, mo = True, weight = 1, skip = "z")
        
        line1 = Nurbs.lineconnect(
                self.module_name, (self.eye, self.aim))
        cmds.parent(line1, self.module_name+"_proxy_GRP")
        
        rig.proxy_lock(self.proxy_dict)
    

if __name__ == "__main__":
    
    socket = cmds.group(n = "proxy_test_GRP", em = True)
    test = ProxyEye()
    test.build_proxy(socket)
        
    
    pass