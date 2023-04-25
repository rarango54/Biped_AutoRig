import maya.cmds as cmds

class Control(object):
    """ description of the class """
        
    @classmethod
    def double_circle_ctrl(cls, name, radius, color='green', rotOrder='xzy'):
        ctrl = cmds.group(n=name, em=True, w=True)
        for i in [1, 0.9]:
            circle = cmds.circle(n=name, c=(0,0,0), nr=(0,1,0), sw=360, r=i*radius, d=3, ch=0)[0]
            shape = cmds.listRelatives(circle, c=True, s=True)
            cmds.parent(shape, ctrl, r=True, s=True)
            cmds.delete(circle)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def stack_circles_ctrl(cls, name, radius, color='pink', rotOrder='zxy'):
        ctrl = cmds.group(n=name, em=True, w=True)
        for i in [1, -1]:
            circle = cmds.circle(n=name, c=(0,i*radius/30,0), nr=(0,1,0), sw=360, r=radius, d=3, ch=0)[0]
            shape = cmds.listRelatives(circle, c=True, s=True)
            cmds.parent(shape, ctrl, r=True, s=True)
            cmds.delete(circle)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def swoop_circle_ctrl(cls, name, radius, color='yellow', rotOrder='zyx'):
        ctrl = cmds.circle(c=(0,0,0), nr=(0,1,0),r=radius,d=3,s=8,ch=0)[0]
        for n, i in enumerate([[3,7], [1,5]]):
            for p in i:
                if n == 0:
                    factor = 1
                else:
                    factor = -1
                cmds.setAttr(f'{ctrl}.controlPoints[{p}].yValue', radius/1.5 * factor)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def square_ctrl(cls, name, size, color='brown', rotOrder='xyz'):
        len=size/2
        ctrl = cmds.curve(n=name, d=1,p=[(-len,0,-len),(-len,0,len),(len,0,len),(len,0,-len),(-len,0,-len)])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def box_ctrl(cls, name, width, height, depth, color='yellow', rotOrder='xyz'):
        wid = width/2
        hei=height/2
        dep=depth/2
        ctrl = cmds.curve(n=name, d=1,p=[(-wid,hei,-dep),(-wid,-hei,-dep),(wid,-hei,-dep),(wid,hei,-dep),(wid,hei,dep),(wid,-hei,dep),(wid,-hei,-dep),(wid,-hei,dep),(-wid,-hei,dep),(-wid,-hei,-dep),(-wid,-hei,dep),(-wid,hei,dep),(-wid,hei,-dep),(wid,hei,-dep),(wid,hei,dep),(-wid,hei,dep)])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def metacarpal_ctrl(cls, name, size, color='blue', rotOrder='zyx'):
        length = 0.75 * size
        ctrl = cmds.circle(n=name,c=[0, size, length/3],nr=[1,0,0],sw=360,r= length, d=3, s=8,ch=0)[0]
        for n in [4,5,6]:
            shape = cmds.listRelatives(ctrl, s=True)[0]
            cmds.setAttr(shape +f'.controlPoints[{n}].yValue', size)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def finger_ctrl(cls, name, width, length, color='blue', rotOrder='zyx'):
        wid = width/2
        len = length
        ctrl = cmds.curve(n=name, d=1,p=[(-wid,wid,wid/3),(-wid,-wid,wid/3),(wid,-wid,wid/3),(wid,wid,wid/3),(wid,wid,len),(wid,-wid,len),(wid,-wid,wid/3),(wid,-wid,len),(-wid,-wid,len),(-wid,-wid,wid/3),(-wid,-wid,len),(-wid,wid,len),(-wid,wid,wid/3),(wid,wid,wid/3),(wid,wid,len),(-wid,wid,len)])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def metaMaster_ctrl(cls, name, size, color='blue', rotOrder='zyx'):
        len = size * 2.5
        wid = size * 0.5
        hei = size * 1.5
        ctrl = cmds.curve(n=name, d=3,p=[(0,-hei/2,0),(0,-hei/2,len),(0,-hei/2,len),(0,-hei/2,len),(wid,-hei/4,len),(wid,hei/4,len),(0,hei/2,len),(0,hei/2,len),(0,hei/2,len),(0,hei/2,0),(0,hei/2,0),(0,hei/2,0),(wid,hei/4,0),(wid,-hei/4,0),(0,-hei/2,0)])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    # FK
    # sphere
    # switcher
    # pyramid
    # bendy
    # shoulder

    @classmethod
    def flip_ctrl(cls, ctrl, orient='z', scale=(1,1,1)):
        """ choose orientation of ctrl's shape & then invert it on any axis """
        
        orients = {
            'x'  :   [f'{ctrl}.rotateY', 90],
            'y'  :   [f'{ctrl}.rotateX', -90],
            'z'  :   None,
            '-x' :   [f'{ctrl}.rotateY', -90],
            '-y' :   [f'{ctrl}.rotateX', 90],
            '-z' :   [f'{ctrl}.rotateY', 180],
        }
        if orient is not 'z':
            cmds.setAttr(orients[orient][0], orients[orient][1])
            cmds.makeIdentity(ctrl, a=True, r=1)
        cmds.setAttr(f'{ctrl}.scaleX', scale[0])
        cmds.setAttr(f'{ctrl}.scaleY', scale[1])
        cmds.setAttr(f'{ctrl}.scaleZ', scale[2])
        cmds.makeIdentity(ctrl, a=True, s=1)
        
    def ctrl_config(self, ctrl, color, rotOrder):
        """ only to be used inside the 'Controls' classmethods
        assign color to shapes + rename shapes to match transform name + define rotate order """
        
        colors = {
            'yellow':   17,
            'brown' :   24,
            'blue'  :    6,
            'sky'   :   18,
            'red'   :   13,
            'pink'  :   20,
            'green' :   14
            }
        if color not in colors:
            color = 'green'
            
        shapes = cmds.listRelatives(ctrl, c=True, s=True)
        for s in shapes:
            cmds.setAttr(f'{s}.overrideEnabled', 1)
            cmds.setAttr(f'{s}.overrideColor', colors[color])
            
            cmds.rename(s, f'{ctrl}Shape')
        
        rotOrders = {
            'xyz'   :   0,
            'yzx'   :   1,
            'zxy'   :   2,
            'xzy'   :   3,
            'yxz'   :   4,
            'zyx'   :   5
        }
        cmds.setAttr(f'{ctrl}.ro', rotOrders[rotOrder])

if __name__ == "__main__":
    
    #Control.finger_ctrl('finger_CTRL', 0.1, 0.3)
    #Control.double_circle_ctrl('global_CTRL', 0.5, 'skyblue')
    Control.box_ctrl('cog_CTRL', 0.5, 0.05, 0.3)
    #Control.metacarpal_ctrl('meta_CTRL', 0.5)
    #Control.flip_ctrl('meta_CTRL', 'x', (-1,-1,1))
    #Control.metaMaster_ctrl('metaMaster_CTRL', 0.3)
    pass
