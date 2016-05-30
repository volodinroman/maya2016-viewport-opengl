import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaRender as OpenMayaRender

from PySide import QtCore, QtGui
from shiboken import wrapInstance

import math 

class KeyboardEvents(QtCore.QObject):
    def __init__(self, view3D = OpenMayaUI.M3dView.active3dView()):
        super(KeyboardEvents, self).__init__()

        self.view = view3D
        self.K_Ctrl = False
        self.K_Esc = False
        self.K_Shift = False
        self.K_Alt = False
        self.K_Enter = False
    
    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.Type.KeyPress:

            if event.key() == QtCore.Qt.Key_Control:
                self.K_Ctrl = True
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Shift:
                self.K_Shift = True
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Escape:
                self.K_Esc = True
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Alt:
                self.K_Alt = True
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Return:
                self.K_Enter = True
                self.view.refresh(True, True)


        if event.type() == QtCore.QEvent.Type.KeyRelease:

            if event.key() == QtCore.Qt.Key_Control:
                self.K_Ctrl = False
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Shift:
                self.K_Shift = False
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Escape:
                self.K_Esc = False
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Alt:
                self.K_Alt = False
                self.view.refresh(True, True)

            if event.key() == QtCore.Qt.Key_Return:
                self.K_Enter = False
                self.view.refresh(True, True)

class MouseEvents(QtCore.QObject):
    def __init__(self, view3D = OpenMayaUI.M3dView.active3dView()):
        super(MouseEvents, self).__init__()

        self.view = view3D
        self.M_Button_Left = False
        self.M_Button_Right = False
        self.M_Move = False
        self.M_posX = 0
        self.M_posY = 0
        self.editMode = False

    
    def eventFilter(self, obj, event):

        if event.type() == QtCore.QEvent.Type.MouseButtonPress:

            if event.button() == 1:
                self.M_posX = event.pos().x()
                self.M_posY = event.pos().y()
                self.M_Button_Left = True
                self.view.refresh(True, True)

            if event.button() == 2:
                self.M_posX = event.pos().x()
                self.M_posY = event.pos().y()
                self.M_Button_Right = True
                self.view.refresh(True, True)

        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:

            if event.button() == 1:
                self.M_Button_Left = False
                self.view.refresh(True, True)

            if event.button() == 2:
                self.M_Button_Right = False
                self.view.refresh(True, True)

        if event.type()==QtCore.QEvent.Type.MouseMove:

            self.M_posX=event.pos().x()
            self.M_posY=event.pos().y()
            self.M_Move=True
            self.view.refresh(True, True)

        if self.editMode:
            return True

class ViewportPainter(object):

    def __init__ (self):

        self.callback = None
        self.currentModelPanel = None
        self.unit = 1.0
        self.glFT = None
        self.qt_Active_View = None
        self.qt_Maya_Window = None

        self.view3D = OpenMayaUI.M3dView.active3dView()
        self.userKeyboardEvents = KeyboardEvents(self.view3D)
        self.userMouseEvents = MouseEvents(self.view3D)

        self.initializeGL()
        self.initializeCallback()


    def initializeGL(self):

        #scene measure units
        unit = cmds.currentUnit(q=1, linear=1)
        if unit == "m":
            self.unit = float(self.unit) * 100.0

        self.glFT = OpenMayaRender.MHardwareRenderer.theRenderer().glFunctionTable()

    def initializeCallback(self):

        #get current model panel
        self.currentModelPanel = cmds.getPanel(wf = 1)
        if "modelPanel" not in self.currentModelPanel:
            self.currentModelPanel = cmds.getPanel(vis = 1)
            for i in self.currentModelPanel:
                if "modelPanel" in i:
                    self.currentModelPanel = i


        #try removing old callbacks from memory
        try:
            OpenMayaUI.MUiMessage.removeCallback(self.callBack)
        except:
            pass

        #create a callback that is registered after a frame is drawn with a 3D content but before 2D content
        self.callback = OpenMayaUI.MUiMessage.add3dViewPostRenderMsgCallback(self.currentModelPanel, self.update)
        self.view3D.refresh(True, True)

        #create QT maya window event filter
        main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
        self.qt_Maya_Window = wrapInstance(long(main_window_ptr), QtCore.QObject)
        self.qt_Maya_Window.installEventFilter(self.userKeyboardEvents) 

        #create viewport event filter
        active_view_ptr = self.view3D.widget()
        self.qt_Active_View = wrapInstance(long(active_view_ptr), QtCore.QObject)
        self.qt_Active_View.installEventFilter(self.userMouseEvents)

        cmds.inViewMessage( amg='<hl>Tool:</hl> Use <hl>"Esc"</hl> to cancel the tool', pos='botLeft', fade=True )

        print "Initialized..."

    def uninitializeCallback(self):
        OpenMayaUI.MUiMessage.removeCallback(self.callback) #remove 3dView Render Callback

        self.qt_Maya_Window.removeEventFilter(self.userKeyboardEvents) #remove QT Callback
        self.qt_Active_View.removeEventFilter(self.userMouseEvents) #remove QT Callback

        OpenMayaUI.M3dView.active3dView().scheduleRefresh()   

        print "Uninitialized..."



    def getMouseIntersect(self):

        sourcePnt = OpenMaya.MPoint(0,0,0)
        rayDir = OpenMaya.MVector(0,0,0)
        maximumDistance = 9999999999
        viewHeight = self.view3D.portHeight()
        
        hitNormal = OpenMaya.MVector()
        
        intersectedObject = None
        intersectedPoint = OpenMaya.MFloatPoint()
        intersectedFace = 0

        hitFace = OpenMaya.MScriptUtil()
        hitFace.createFromInt(0)
        hitFacePtr = hitFace.asIntPtr()

        hitDistance = OpenMaya.MScriptUtil(0.0)
        hitDistancePtr = hitDistance.asFloatPtr()

        self.view3D.viewToWorld(int(self.userMouseEvents.M_posX), int(viewHeight - self.userMouseEvents.M_posY), sourcePnt, rayDir)

        
        direction = OpenMaya.MFloatVector(rayDir.x, rayDir.y, rayDir.z).normal()

        iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kMesh)

        while not iter.isDone():

            node =iter.thisNode()
            dagPath = OpenMaya.MDagPath.getAPathTo(node)

            hitPoint = OpenMaya.MFloatPoint()
            source = OpenMaya.MFloatPoint(sourcePnt.x, sourcePnt.y, sourcePnt.z)
            direction = OpenMaya.MFloatVector(direction.x,direction.y,direction.z)

            if dagPath.isVisible():
                mesh = OpenMaya.MFnMesh(dagPath)
                intersected = mesh.closestIntersection(source, direction, None, None, False, OpenMaya.MSpace.kWorld, 9999999999, True, None, hitPoint, hitDistancePtr, hitFacePtr, None, None, None, 0.0001)
                
                if intersected:
                    intersectionDistance = hitDistance.getFloat(hitDistancePtr)
                    if intersectionDistance < maximumDistance:
                        maximumDistance = intersectionDistance
                        intersectedPoint = hitPoint
                        intersectedFace =  OpenMaya.MScriptUtil(hitFacePtr).asInt()
                        mesh.getClosestNormal(OpenMaya.MPoint(intersectedPoint),hitNormal,OpenMaya.MSpace.kWorld)
                        intersectedObject = dagPath.fullPathName()

            iter.next()

        if intersectedPoint.x + intersectedPoint.y + intersectedPoint.z == 0:
            return None, None, None
        else:
            return intersectedPoint, intersectedFace, intersectedObject


    def update(self, *args):
        pass

