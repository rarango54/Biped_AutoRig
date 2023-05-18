import maya.cmds as cmds

from utils.ctrl_library import Control

    
def make_proxies(proxy_dict, parent_grp, module_name):
    """dict setup = {"name" : 
        ( [pos], "shape", size, "color", [lock axes] )}
    """
    module_grp = cmds.group(n=f"{module_name}_proxy_GRP", em=True)
    cmds.parent(module_grp, parent_grp)
    for proxy in list(proxy_dict):
            shape = proxy_dict[proxy][1]
            size = proxy_dict[proxy][2]
            color = proxy_dict[proxy][3]
            
            loc = cmds.spaceLocator(n=proxy, a=True)[0]
            
            temp_obj = eval(
                f'Control.{shape}("temp", {size}, "{color}")'
                )
            temp_shape = cmds.listRelatives(temp_obj, s=True)
            for s in temp_shape:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
            cmds.parent(temp_shape, loc, r=True, s=True)
            new_shapes = cmds.listRelatives(loc, s=True)
            for s in new_shapes:
                cmds.rename(s, f"{loc}Shape")
            cmds.delete(temp_obj)
            
            cmds.xform(loc, t=proxy_dict[proxy][0])
            
            
            cmds.parent(loc, module_grp)
            previous = proxy
            
    return list(proxy_dict)

def proxy_lock(proxy_dict):
    for proxy in list(proxy_dict):
        lock_axes = proxy_dict[proxy][4]
        for axis in lock_axes:
            cmds.setAttr(f"{proxy}.{axis}", l=True)

def make_joints(proxies_list, rot_order, radius):
    cmds.select(cl=True)
    for proxy in proxies_list:    # skip proxies that don't need joints
        fitted_pos = cmds.xform(proxy, q=True, rp=True, ws=True)
        j = cmds.joint(
            n=proxy.replace("PRX", "JNT"), p=fitted_pos, 
            roo=rot_order, rad=4
            )
        cmds.sets(j, add="joints")

    

if __name__ == "__main__":
    
    parent = cmds.group(n="test", em=True)
    proxy_dict = {
            "cog_PRX" : (
                [0, 100, 0], "cube", 10, "yellow", 
                ["tx","ry","rz","s"]),
            "hip_PRX" : (
                [0, 100, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "waist_PRX" : (
                [0, 112.5, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "chest_PRX" : (
                [0, 125, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "chest_up_PRX" : (
                [0, 140, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "spine_end_PRX" : (
                [0, 155, 0], "cube", 6, "sky", 
                ["tx","r","s"])
        }
    make_proxies(proxy_dict, parent, "spine")
    
    pass