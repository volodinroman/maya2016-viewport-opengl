from ViewportPainter import *

class Example(ViewportPainter):
    def __init__(self):
        
        self.hitPoint = None 
        self.hitFace = None
        self.hitObject = None
        self.hitObjectDag = None
        self.editing = True
        self.closestX = None
        self.closestY = None
        self.closestIndex = None
        self.structData = [] # DagPath | HitFaceID | [U,V] | HitPoint
        self.controlPoints = []
        self.curveList = []

        super(Example, self).__init__()

    def drawRect2D(self, worldPoint, radius = 5):
        point = worldPoint

        xPtrInit = OpenMaya.MScriptUtil()
        yPtrInit = OpenMaya.MScriptUtil()
        xPtr = xPtrInit.asShortPtr()
        yPtr = yPtrInit.asShortPtr()
        
        pointFix = OpenMaya.MPoint(worldPoint.x, worldPoint.y, worldPoint.z)
        
        self.view3D.worldToView(pointFix, xPtr, yPtr)
        
        xcoord = OpenMaya.MScriptUtil().getShort(xPtr)
        ycoord = OpenMaya.MScriptUtil().getShort(yPtr)


        # self.view3D.beginGL()
        # self.glFT.glPushAttrib(OpenMayaRender.MGL_ALL_ATTRIB_BITS )
        self.glFT.glPushMatrix()
        # self.glFT.glDrawBuffer( OpenMayaRender.MGL_FRONT )
        self.glFT.glDisable( OpenMayaRender.MGL_DEPTH_TEST )
        # Setup the Orthographic projection Matrix.
        self.glFT.glMatrixMode( OpenMayaRender.MGL_PROJECTION )
        self.glFT.glLoadIdentity()
        self.glFT.glOrtho( 0.0, float(self.view3D.portWidth()), 0.0, float(self.view3D.portHeight()), -1.0, 1.0 )
        self.glFT.glMatrixMode( OpenMayaRender.MGL_MODELVIEW )
        self.glFT.glLoadIdentity()
        self.glFT.glTranslatef(0.0, 0.375, 0.0)


        self.glFT.glColor4f(1, 0, 0, 1) #0.2
        self.glFT.glBegin(OpenMayaRender.MGL_POLYGON) 

        self.glFT.glVertex2f(xcoord - radius,  ycoord - radius)
        self.glFT.glVertex2f(xcoord - radius,  ycoord + radius)
        self.glFT.glVertex2f(xcoord + radius,  ycoord + radius)
        self.glFT.glVertex2f(xcoord + radius,  ycoord - radius)

        self.glFT.glEnd() 



        # Restore the state of the matrix from stack
        self.glFT.glMatrixMode( OpenMayaRender.MGL_MODELVIEW )
        self.glFT.glPopMatrix()
        # Restore the previous state of these attributes
        self.glFT.glPopAttrib()

    def draw(self):

        self.glFT.glPushAttrib(OpenMayaRender.MGL_ALL_ATTRIB_BITS) #save all stackable states
        self.view3D.beginGL() #setup port for drawing native OpenGL calls
        self.glFT.glClearDepth(0.0)
        self.glFT.glDepthFunc(OpenMayaRender.MGL_ALWAYS)
        self.glFT.glEnable( OpenMayaRender.MGL_BLEND )
        self.glFT.glBlendFunc( OpenMayaRender.MGL_SRC_ALPHA, OpenMayaRender.MGL_ONE_MINUS_SRC_ALPHA )

        fnMesh = None
        self.controlPoints = []

        #recreate control points for every callback
        if len(self.structData) > 0:
            for i in self.structData: 
                fnMesh = OpenMaya.MFnMesh(i[0])  
                point = OpenMaya.MPoint(0,0,0)
                u = i[2][0]
                v = i[2][1]
                util = OpenMaya.MScriptUtil()
                util.createFromList([u, v], 2)
                uvFloat2Ptr = util.asFloat2Ptr()
                fnMesh.getPointAtUV(i[1], point, uvFloat2Ptr, OpenMaya.MSpace.kWorld)
                self.controlPoints.append(point)

        if self.controlPoints:
            self.glFT.glColor4f(1, 1, 0, 1)
            for i in range(len(self.controlPoints) - 1):
                p1 = self.controlPoints[i]
                p2 = self.controlPoints[i+1]

                self.glFT.glBegin(OpenMayaRender.MGL_LINES) 
                self.glFT.glVertex3f(p1.x, p1.y, p1.z)
                self.glFT.glVertex3f(p2.x, p2.y, p2.z)
                self.glFT.glEnd()

        #Draw Locators by control points
        if self.controlPoints:
            for i in self.controlPoints:
                self.drawRect2D(i, 3)

        self.view3D.endGL()#eng openGL drawings
        self.glFT.glPopAttrib() #restores values of state variables, changed by glPushAttrib

    #Overwritten update method 
    def update(self, *args):

        if self.userKeyboardEvents.K_Esc:
            self.uninitializeCallback()
            return


        if self.userKeyboardEvents.K_Ctrl:
            self.userMouseEvents.editMode = True
            
            '''Mouse press'''
            if self.userMouseEvents.M_Button_Left:

                self.hitPoint, self.hitFace, self.hitObject = self.getMouseIntersect() 

                if self.hitObject: #intersection was successfull

                    #get UV at hitPoint
                    dagPath = OpenMaya.MDagPath()
                    selectionList = OpenMaya.MSelectionList()
                    selectionList.clear()
                    selectionList.add(self.hitObject)
                    selectionList.getDagPath(0, dagPath)
                    self.hitObjectDag = dagPath
                    fnMesh = OpenMaya.MFnMesh(dagPath)
                    util = OpenMaya.MScriptUtil()
                    util.createFromList([0.0, 0.0], 2)
                    uvPoint = util.asFloat2Ptr()
                    fnMesh.getUVAtPoint(OpenMaya.MPoint(self.hitPoint.x, self.hitPoint.y, self.hitPoint.z), uvPoint, OpenMaya.MSpace.kWorld, "map1", None)
                    u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
                    v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)
                    
                    #fill up StructData with a New Element
                    uv = []
                    uv.append(u)
                    uv.append(v)
                    data = []
                    data.append(dagPath) 
                    data.append(self.hitFace) 
                    data.append(uv)
                    data.append(self.hitPoint)

                    # if self.editing == False  and self.closestIndex == None and not self.userKeyboardEvents.K_Alt:
                    if self.editing == False:
                        self.structData.append(data) #we add a new element to StructData

                    else:

                        lastPoint = self.structData[-1][3]
                        vector = OpenMaya.MVector(self.hitPoint.x - lastPoint.x, self.hitPoint.y - lastPoint.y, self.hitPoint.z - lastPoint.z)
                        
                        if vector.length() > 0.5:
                            self.structData.append(data) #we add a new element to StructData

                    self.editing = True

            '''Mouse release'''
            if not self.userMouseEvents.M_Button_Left:

                self.editing = False #stop editing, next time we will add a new element
                self.userMouseEvents.editMode = False

                if self.structData and self.controlPoints:

                    curveCV = []
                    for i in self.controlPoints:

                        point = []
                        point.append(i.x)
                        point.append(i.y)
                        point.append(i.z)
                        curveCV.append(point)

                    if len(curveCV) >= 4:

                        curve = cmds.curve( p=curveCV )
                        cmds.rebuildCurve(curve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=6, d=3, tol=0)
                        self.curveList.append(curve)
                    self.structData = []

        if not self.userKeyboardEvents.K_Ctrl:

            if len(self.curveList) >= 2:

                surface = cmds.loft(self.curveList, ch=0, u=1, c=0, ar=0, d=3, ss=1, rn=1, po=0, rsn = True)[0]
                poly = cmds.nurbsToPoly(surface, mnd=1, ch=0, f=0, pt=1, pc=200, chr=0.9, ft=0.01, mel = 0.001, d=0.1, ut=1, un=3, vt=1, vn=3, uch=0, ucr=0, cht=0.2, es=0, ntr=0, mrt=0, uss=1)
                cmds.delete(self.curveList)
                cmds.delete(surface)
                cmds.polyNormal(poly[0], normalMode = 0, userNormalMode = 0, ch=0)

                self.uninitializeCallback()

        if len(self.structData) == 0: 

            return

        self.draw()
        

def main():
    instance = Example()