import maya.cmds as cmds

class Nurbs(object):
    """all classmethods return a single transform with
    correctly named nurbsCruve Shapes
    
    default rotation orders:
        globals     :   xzy
        limbs       :   zyx
        spine       :   zyx
        neck        :   yzx   
    """
    
    # keep dimension input to only 1 "size" or "radius" where possible
    
    @classmethod
    def sphere(cls, name, radius, color='sky', rotOrder='xyz'):
        ctrl = cmds.group(n=name, em=True, w=True)
        for ori in [(0,1,0), (1,0,0), (0,0,1)]:
            circle = cmds.circle(n=name, c=(0,0,0), nr=ori,
                sw=360, r=radius, d=3, ch=0
                )[0]
            shape = cmds.listRelatives(circle, c=True, s=True)
            cmds.parent(shape, ctrl, r=True, s=True)
            cmds.delete(circle)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def double_circle(cls, name, radius, color='green', rotOrder='xzy'):
        ctrl = cmds.group(n=name, em=True, w=True)
        for i in [1, 0.9]:
            circle = cmds.circle(n=name, c=(0,0,0), nr=(0,1,0),
                sw=360, r=i*radius, d=3, ch=0
                )[0]
            shape = cmds.listRelatives(circle, c=True, s=True)
            cmds.parent(shape, ctrl, r=True, s=True)
            cmds.delete(circle)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def arrow(cls, name, size, color="brown", rotOrder="xzy"):
        le = size
        wid = size
        ctrl = cmds.curve(n=name, d=1,p=[
            (wid/3,0,-le),(wid/2,0,0),
            (0.8*wid,0,-le/5),(wid,0,le/7),
            (0,0,le),
            (-wid,0,le/7),(-0.8*wid,0,-le/5),
            (-wid/2,0,0),(-wid/3,0,-le),
            (wid/3,0,-le)]
            )
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def stack_circles(cls, name, radius, color='pink', rotOrder='zxy'):
        ctrl = cmds.group(n=name, em=True, w=True)
        for i in [1, -1]:
            circle = cmds.circle(n=name, c=(0,i*radius/30,0), nr=(0,1,0),
                sw=360, r=radius, d=3, ch=0
                )[0]
            shape = cmds.listRelatives(circle, c=True, s=True)
            cmds.parent(shape, ctrl, r=True, s=True)
            cmds.delete(circle)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def swoop_circle(cls, name, radius, color='yellow', rotOrder='zyx'):
        ctrl = cmds.circle(n=name, c=(0,0,0), nr=(0,1,0),
            r=radius,d=3,s=8,ch=0)[0]
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
    def square(cls, name, size, color='brown', rotOrder='xyz'):
        len=size/2
        ctrl = cmds.curve(n=name, d=1, p=[(-len,0,-len),(-len,0,len),
            (len,0,len),(len,0,-len),(-len,0,-len)]
            )
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def box(cls, name, width, height, depth, color='yellow', rotOrder='xyz'):
        wid = width/2
        hei = height/2
        dep = depth/2
        ctrl = cmds.curve(n=name, d=1,p=[
            (-wid,hei,-dep),(-wid,-hei,-dep),(wid,-hei,-dep),(wid,hei,-dep),
            (wid,hei,dep),(wid,-hei,dep),(wid,-hei,-dep),(wid,-hei,dep),
            (-wid,-hei,dep),(-wid,-hei,-dep),(-wid,-hei,dep),(-wid,hei,dep),
            (-wid,hei,-dep),(wid,hei,-dep),(wid,hei,dep),(-wid,hei,dep)
            ])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def cube(cls, name, size, color='yellow', rotOrder='xyz'):
        ctrl = cls.box(name, size, size, size, color, rotOrder)
        return ctrl
    
    @classmethod
    def octahedron(cls, name, size, color='yellow', rotOrder='xyz'):
        x = size
        bottom = (0,-x*1.3,0)
        tip = (0,x*1.3,0)
        ctrl = cmds.curve(n=name, d=1,p=[
            (x,0,-x),bottom,(x,0,x),(-x,0,x),bottom,(-x,0,-x),(x,0,-x),
            (x,0,x),tip,(-x,0,x),(-x,0,-x),tip,(x,0,-x)
            ])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def metacarpal(cls, name, size, color='blue', rotOrder='zyx'):
        length = 0.75 * size
        ctrl = cmds.circle(n=name,c=[0, size, length/3],
            nr=[1,0,0],sw=360,r= length, d=3, s=8,ch=0
            )[0]
        for n in [4,5,6]:
            shape = cmds.listRelatives(ctrl, s=True)[0]
            cmds.setAttr(shape +f'.controlPoints[{n}].yValue', size)
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl

    @classmethod
    def fk_box(cls, name, width, length, color='blue', rotOrder='zyx'):
        wid = width/2
        len = length
        ctrl = cmds.curve(n=name, d=1,p=[
            (-wid,wid,wid/3),(-wid,-wid,wid/3),(wid,-wid,wid/3),(wid,wid,wid/3),
            (wid,wid,len),(wid,-wid,len),(wid,-wid,wid/3),(wid,-wid,len),
            (-wid,-wid,len),(-wid,-wid,wid/3),(-wid,-wid,len),(-wid,wid,len),
            (-wid,wid,wid/3),(wid,wid,wid/3),(wid,wid,len),(-wid,wid,len)
            ])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def metaMaster(cls, name, size, color='blue', rotOrder='zyx'):
        len = size * 2.5
        wid = size * 0.5
        hei = size * 1.5
        ctrl = cmds.curve(n=name, d=3,p=[
            (0,-hei/2,0),(0,-hei/2,len),(0,-hei/2,len),(0,-hei/2,len),
            (wid,-hei/4,len),(wid,hei/4,len),(0,hei/2,len),(0,hei/2,len),
            (0,hei/2,len),(0,hei/2,0),(0,hei/2,0),(0,hei/2,0),
            (wid,hei/4,0),(wid,-hei/4,0),(0,-hei/2,0)
            ])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def shoulder(cls, name, size, color='blue', rotOrder='zyx'):
        # distance, width, length
        d = size * 0.8
        w = size * 0.1
        s = size * 0.5
        h = size * 0.8
        ctrl = cmds.curve(n=name, d=3,p=[
            (-s,0,d),(-s,0,d+w),(-s,h/2,d+w),(0,h,d+w),(s,h/2,d+w),
            (s,0,d+w),(s,0,d),(s,0,d-w),(s,h/2,d-w),(0,h,d-w),
            (-s,h/2,d-w),(-s,0,d-w),(-s,0,d)
            ])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def switcher(cls, name, size, color='blue', rotOrder='xyz'):
        # depth, width1 = narrower tip, width2 = wider butt
        d = size
        w1 = size * 0.3
        w2 = size * 0.6
        ctrl = cmds.curve(
            n=name, d=1,p=[
            (0,0,d),(w1,0,d),(w2,0,-d),(0,0,-d),(0,w2,-d),(0,w1,d),
            (0,0,d),(-w1,0,d),(-w2,0,-d),(0,0,-d),(0,-w2,-d),(0,-w1,d),
            (0,0,d)])
        cls.ctrl_config(cls, ctrl, color, rotOrder)
        return ctrl
    
    @classmethod
    def lineconnect(cls, proxymodule, nodes):
        objects = [nodes] if isinstance(nodes, str) else nodes
        positions = []
        args = {}
        for n, obj in enumerate(objects):
            pos = cmds.xform(obj, q = True, t = True, worldSpace = True)
            positions.append(pos)
            args[f"p{n}"] = pos
        curve = eval(
            f"cmds.curve(n = f'{proxymodule}_line_CRV', degree = 1, p = {positions})")
        shape = cmds.rename(
                    cmds.listRelatives(curve, children = True, shapes = True),
                    f"{curve}Shape")
        for n, obj in enumerate(nodes):
            # connect objs through decomp_mtx to curve's control cvs
            dmtx = cmds.createNode("decomposeMatrix", n = f"{proxymodule}_cv{n}_DM")
            cmds.connectAttr(f"{obj}.worldMatrix[0]", f"{dmtx}.inputMatrix")
            cmds.connectAttr(f"{dmtx}.outputTranslateX", 
                             f"{curve}Shape.controlPoints[{n}].xValue")
            cmds.connectAttr(f"{dmtx}.outputTranslateY", 
                             f"{curve}Shape.controlPoints[{n}].yValue")
            cmds.connectAttr(f"{dmtx}.outputTranslateZ", 
                             f"{curve}Shape.controlPoints[{n}].zValue")
        # drawingOverride settings
        cmds.setAttr(f'{shape}.overrideEnabled', 1)
        cmds.setAttr(f"{shape}.overrideDisplayType", 2)
        cmds.setAttr(f"{shape}.alwaysDrawOnTop", 1)
        return curve
    # FK
    # bendy

    @classmethod
    def flip_shape(cls, ctrl, orient='z', scale=(1,1,1)):
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
        """ only to be used inside the 'Nurbs' classmethods
        assign color to shapes + rename shapes to match transform name + define rotate order """
        colors = {
            'yellow':   17,
            'brown' :   24,
            'blue'  :    6,
            'sky'   :   18,
            'red'   :   13,
            'pink'  :   20,
            'green' :   14,
            'grass' :   27,
            'grey'  :   3,
            'white' :   16,}
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
            'zyx'   :   5,}
        cmds.setAttr(f'{ctrl}.ro', rotOrders[rotOrder])

if __name__ == "__main__":
    
    Nurbs.switcher("test", 2, "green")
    pass
