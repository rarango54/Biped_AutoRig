import maya.cmds as cmds


class ProxyRig(object):
    
    
    def __init__(self):
        
        
        print("instance created successfully")
        
        self.proxy_dict = {
            "hip"       :   [0, 1, 0],
            "waist"     :   [0, 1.15, 0],
            "chest"     :   [0, 1.3, 0],
            "upChest"   :   [0, 1.5, 0]
        }
        self.arm_proxy = {
            "clavicle"  :   [0.02, 1.6, 0.05],
            "upArm"     :   [0.2, 1.6, 0],
            "elbow"     :   [0.4, 1.6, 0],
            "wrist"     :   [0.6, 1.6, 0]
        }
        self.proxy_template = {
            **self.spine_proxy,
            **self.arm_proxy
        }

    def build(self):
        """Locator Rig with limited transforms
        to match model pose and define skeleton joints
        """
        pass


if __name__ == "__main__":
    
    test = ProxyRig()
    for i in test.proxy_template:
        print(test.proxy_template[i])