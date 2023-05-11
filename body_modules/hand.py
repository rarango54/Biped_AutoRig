import maya.cmds as cmds

from utils import util
from utils.ctrl_Library import Control


###############################
######## HAND MODULE ##########
###############################

class HandRig(object):
    
    def __init__(self, side):
        """
        defines set of finger joints based on string names; index, middle, ring, pinky, thumb
        creates finger, metacarpal, metaMaster ctrls
        connects joints to ctrls
        connects ctrls to metaMaster
        """
        
        # test for correct keyword
        if type(side) != str or len(side) > 1:
            raise RuntimeError("choose either 'L' or 'R' as the keyword argument")
        
        self.side = side
        self.indexJnts = [f'{side}_index_{x}_JNT' for x in [4,3,2,1]]
        self.middleJnts = [f'{side}_middle_{x}_JNT' for x in [4,3,2,1]]
        self.ringJnts = [f'{side}_ring_{x}_JNT' for x in [4,3,2,1]]
        self.pinkyJnts = [f'{side}_pinky_{x}_JNT' for x in [4,3,2,1]]
        self.thumbJnts = [f'{side}_thumb_{x}_JNT' for x in [3,2,1]]
        
        #self.thumbCtrls = [x.replace('JNT', 'CTRL') for x in self.thumbJnts]
        
        self.handCtrlGrp = self.parent_setup(self.side)
        self.ctrlSize = util.get_distance(self.middleJnts[-1], self.middleJnts[-2]) / 2 # meta to knuckle
        self.fingerCtrls = self.finger_controls(self.side)
        self.metaMaster = self.meta_master(self.side)
        self.lock_attrs()
        
    def parent_setup(self, side):
        # parent setup to follow arm
        fingerGrp = cmds.group(n=f'{side}_hand_ctrl_GRP',em=True,p='ctrls_GRP')
        parentJoint = f'{side}_hand_JNT'
        cmds.connectAttr(f'{parentJoint}.worldMatrix[0]', fingerGrp+'.offsetParentMatrix')
        return fingerGrp

    def finger_controls(self, side):
        if side == 'L':
            color = 'blue'
        if side == 'R':
            color = 'red'
        # rotOrder is set by default to 'zyx' in the classmethod
        
        fingers = [self.indexJnts, self.middleJnts, self.ringJnts, self.pinkyJnts, self.thumbJnts]
        fingerCtrls = [] # append each ctrl in following loop
        
        for finger in fingers: # finger = joint chain
            for fj in finger: # f = single joint, starting with tip
                name = fj.replace('JNT', 'CTRL')
                fjChild = cmds.listRelatives(fj, c=True)[0]
                ctrlLength = util.get_distance(fj, fjChild)
                
                if fj == finger[-1]:
                    fc = Control.metacarpal_ctrl(name, self.ctrlSize, color)
                else:
                    fc = Control.finger_ctrl(name, self.ctrlSize, ctrlLength, color)
                cmds.matchTransform(fc, fj, pos=True,rot=True, scl=True)
                
                fingerCtrls.append(fc)
                
                if side == 'R': # flip ctrl's shape orientation so it points to finger tip
                    Control.flip_ctrl(fc, 'z', (1, -1, -1))
                    
                # parent next ctrl to current one, moving up the chain backwards
                if fj == finger[0]: # skip finger tip ctrl
                    continue
                else: 
                    nr = int(fc.split('_')[-2])
                    cmds.parent(fc.replace(str(nr), str(nr+1)), fc, a=True)
                    util.insert_scaleInvJoint(fc)
                    if fj == finger[-1]:
                        cmds.parent(fc, self.handCtrlGrp)
        
        util.zero_transforms(fingerCtrls)
        return fingerCtrls
    
    def meta_master(self, side):
        if side == 'L':
            color = 'blue'
        if side == 'R':
            color = 'red'
        
        metaMaster = Control.metaMaster_ctrl(f'{side}_metaMaster_CTRL', self.ctrlSize, color)
        mov = 1
        if side == 'R':
            Control.flip_ctrl(metaMaster, 'z', (-1, -1, -1))
            mov = -1
        cmds.parent(metaMaster, self.handCtrlGrp)
        cmds.matchTransform(metaMaster, self.pinkyJnts[-1], pos=True,rot=True)
        cmds.move(mov*self.ctrlSize, 0, 0, metaMaster, r=True, ls=True)
        util.zero_transforms(metaMaster)
        
        return metaMaster

    def connect_fingers(self, metaMaster, fingerCtrls):
        metaJnts = [self.indexJnts[-1], self.middleJnts[-1], self.ringJnts[-1], self.pinkyJnts[-1]]
        metaCtrls = [x.replace('JNT', 'CTRL') for x in metaJnts]

    def lock_attrs(self):
        thumbBaseJnt = self.thumbJnts[-1]
        thumbBaseCtrl = thumbBaseJnt.replace('_JNT', '_CTRL')
        for ctrl in self.fingerCtrls:
            if ctrl == thumbBaseCtrl:
                continue # skip thumb's meta
            for channel in ['tx','ty','tz']:
                cmds.setAttr(f'{ctrl}.{channel}', lock=True,k=False,cb=False)

if __name__ == "__main__":
    
    #L_handRig = HandRig()
    #L_fingerCtrls = finger_controls('L')
    #R_fingerCtrls = finger_controls('R')
    
    L_handRig = HandRig('L')
    R_handRig = HandRig('R')
    #print(R_handRig.fingerCtrls)

    pass