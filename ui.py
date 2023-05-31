import maya.cmds as cmds

from constructor import BaseRig

char_name_input = None

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
        {side}_{component}_#_{obj type}
        e.g. L_index_3_JNT""", h=50)
    cmds.separator()
    
    global char_name_input
    char_name_input = cmds.textField(w = 130, text="character_name")
    
    cmds.rowColumnLayout(p=layout, adj = True, nc=2)
    cmds.button(label = "Create Proxies", w=130, c="build_proxy()")
    cmds.button(label = "Delete Proxies", w=130, c="delete_proxy()")
    
    cmds.button(label="Build Rig", w=130, c="build_rig()")
    cmds.button(label="Delete Rig", w=130, c="delete_rig()")
    
    # cmds.button(label="Build Skeleton", w=130, c="")
    # cmds.button(label="UpdateSkeleton", w=130, c="")
    # cmds.button(label="Callisthenic Anim", w=130, c="")
    
    # cmds.button(label="Export Master File", w=130, c="")
    

    cmds.showWindow()


def build_proxy():
    char_name = cmds.textField(char_name_input, q=True, text=True)
    char_rig = BaseRig(char_name)
    char_rig.construct_proxy()

def delete_proxy():
    cmds.delete("global_PRX")

def build_rig():
    char_name = cmds.textField(char_name_input, q=True, text=True)
    char_rig = BaseRig(char_name)
    char_rig.construct_rig()

def delete_rig():
    joints = cmds.listRelatives("joints_GRP", ad=True)
    ctrls = cmds.listRelatives("ctrls_GRP", ad=True)
    misc = cmds.listRelatives("misc_GRP", ad=True)
    cmds.delete(joints)
    cmds.delete(ctrls)
    cmds.delete(misc)

if __name__ == "__main__":
    
    launch_ui()