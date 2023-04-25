import maya.cmds as cmds

from utils.controls import Controls
from utils import util

if __name__ == "__main__":
    
    circle = Controls.double_circle_ctrl('test', 0.5, 'green')
    util.addAttrSeparator(circle)
    test = Controls()
    print(test)
    
