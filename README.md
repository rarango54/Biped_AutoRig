# Biped_AutoRig

simplified 2 step auto rigger for symmetrical / semi-realistic human characters

- **1)**
user input only required for positioning proxy joint positions
- **2)**
full rig is then generated based on proxies

package is set up in following hierarchy:

*ui --> constructor --> body & proxy modules*

constructor calls on classes from body modules and feeds certain connection attributes (sockets) into other modules.
e.g. clavicle_ctrl should be parented under spine.chest_up_ctrl

body modules have a bunch of string attributes defined for all the joints and ctrls that are part of the module
proxy_dictionary contains position, shape, colour and locked axes data

**ToDo**:
- test if rig exports properly into unity and rumba
- fbx tests to blender
- add missing modules
- bendies
- helper joint system - maybe another user input step?
- UI button to finalise rig, i.e. import all namespaces, merge with root, remove shape nodes from channel box history, delete proxies etc.
- get animators to test rig

- how to connect face to body rig?
