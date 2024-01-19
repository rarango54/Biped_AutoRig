import maya.cmds as cmds

from constructor import BodyRig

def launch_ui():
    if cmds.window("Rig_UI", exists=True):
        cmds.deleteUI("Rig_UI")

    ui = cmds.window("Rig_UI", title="Rig_UI")
    layout = cmds.columnLayout(adj = True)
    cmds.text(
        label="Human Auto-Rig", 
        font="boldLabelFont", 
        align="center", h=50, w=130)
    cmds.separator()
    cmds.text(
        label="""Naming Convention:
        {side}_{components}_#_{obj type}
        e.g. L_index_3_JNT""", h=50)
    cmds.separator()
    cmds.rowColumnLayout(p=layout, adj = True, nc=2)
    cmds.button(label = "Proxy", w=130, c="build_proxy()")
    cmds.button(label = "Delete Proxy", w=130, c="delete_proxy()")
    
    cmds.button(label="Rigify", w=130, c="build_rig()")
    cmds.button(label="Delete Rig", w=130, c="delete_rig()")
    
    cmds.rowColumnLayout(p=layout, adj = True, nc=1)
    cmds.separator()
    cmds.text(label = "Tools", h=30)
    cmds.separator()
    cmds.rowColumnLayout(p=layout, adj = True, nc=2)
    
    cmds.button(label="Angle Reader", w=130, c="")
    cmds.button(label="Stretch Helper", w=130, c="")
    # cmds.button(label="Build Skeleton", w=130, c="")
    # cmds.button(label="UpdateSkeleton", w=130, c="")
        # export skin weights
        # delete rig
        # build rig
        # reapply weights
    # cmds.button(label="Callisthenic Anim", w=130, c="")
    
    cmds.rowColumnLayout(p=layout, adj = True, nc=1)
    cmds.separator()
    cmds.text(label = "Finish up", h=30)
    cmds.button(label="Master", w=200, c="master()")
    

    cmds.showWindow()


def build_proxy():
    bod_rig = BodyRig()
    bod_rig.construct_proxy()

def delete_proxy():
    cmds.delete("global_PRX")

def build_rig():
    char_rig = BodyRig()
    char_rig.construct_rig()

def delete_rig():
    # exceptions
    leftovers = cmds.listRelatives("global_PRX", allDescendents = True)
    leftovers.append("global_PRX")
    prxlines = cmds.ls("*prx_DM")
    leftovers.extend(prxlines)
    dn = cmds.ls(defaultNodes = True)
    ud = cmds.ls(undeletable = True)
    g = cmds.listRelatives("geo_GRP", children = True, shapes = False)
    if g:
        cmds.parent(g, world = True)
        leftovers.extend(g)
    leftovers.extend(ud)
    leftovers.extend(dn)
    # curve info nodes first to avoid error
    ci = cmds.ls("*_CI")
    cmds.delete(ci)
    # delete everything except leftovers
    all_nodes = cmds.ls()
    for node in leftovers:
        if node in all_nodes:
            all_nodes.remove(node)
        
    cmds.delete(all_nodes)
    cmds.setAttr("global_PRX.v", 1)
    
def master():
    # delete proxies
    if cmds.objExists("global_PRX"):
        cmds.delete("global_PRX")
    # hide shape nodes on all anim CTRLs
    allControls = cmds.ls("*_CTRL")
    for ctrl in allControls:
        shapes = cmds.listRelatives(ctrl, shapes=True)
        if shapes:
            for sh in shapes:
                cmds.setAttr(f"{sh}.isHistoricallyInteresting", 0)
            
    # import all References
    cmds.ls(r = True)
    # get list of all top-level refs in scene
    all_ref_paths = cmds.file(q=True, reference=True) or []
    for ref_path in all_ref_paths:
        # Only import if it's loaded, otherwise it would error
        if cmds.referenceQuery(ref_path, isLoaded=True):  
            cmds.file(ref_path, importReference=True)  # Import the reference
            # If ref had nested references they will now become top-level references
            # so recollect them
            new_ref_paths = cmds.file(q=True, reference=True)
            if new_ref_paths:
                for new_ref_path in new_ref_paths:
                    # Only add on ones that we don't already have.
                    if new_ref_path not in all_ref_paths:  
                        all_ref_paths.append(new_ref_path)
    # Delete namespaces
    def num_children(ns):
        return ns.count(':')
    defaults = ['UI', 'shared']
    namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
    # reverse the list, so that namespaces with more children are at the front of the list.
    namespaces.sort(key=num_children, reverse=True)
    for ns in namespaces:
        try:
            cmds.namespace(rm=ns, mnr = True)
        except RuntimeError as e:
            # namespace isn't empty, so you might not want to kill it?
            pass
    
    # hide visibility attribute on all ctrls
    ctrls = cmds.ls("*_CTRL")
    for c in ctrls:
        cmds.setAttr(f"{c}.v", lock = True, k = False, cb = False)
    
    return

if __name__ == "__main__":
    
    launch_ui()
    # all_nodes = cmds.ls()
    # for i in all_nodes:
    #     print(i)