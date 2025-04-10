from PySide2.QtGui import QColor
from PySide2.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget  #here we're just importing / downloading what we need to make certain funtions witin our code work properly
from PySide2.QtCore import Qt, Signal      # this is imports a window type which would be the window flags
from maya.OpenMaya import MVector
import maya.OpenMayaUI as omui
import maya.mel as mel
import shiboken2    # This allows to cast the level pointer into python pipeline so we can use it (pointers being memory addresses)

def GetMayaMainWindow()->QMainWindow:        #this provides the framework for building the main application window lines 6 - 9
    mainWindow = omui.MQtUtil.mainWindow()          # this will retrive the main window from Maya
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgetWithName(name): #this is an incur funcution
    for widget in GetMayaMainWindow().findChildren(QWidget, name): #this helps delete widget with the name, so for each weighted inside of the SMA window that have the name assigned and will be deleted later
        widget.deleteLater()  # this letter means that the window will get destroyed when things are ggeting cleared up, so its not being deleted imm editely but will be marked to be trashed that would need to be collected

class MayaWindow(QWidget):     # when we use the QWidget instance for this class, it help set its title and geometry and then displays it
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow()) #the maya window being the super construtor is the parent and this particular widget get parented to the main maya window
        DeleteWidgetWithName(self.GetWidgetUniqueName()) #Deletes widget with name name self. getwindow with uniquw name with whatever been there gets remove first and creates a new one with the same name
        self.setWindowFlags(Qt.WindowType.Window) # this is stating that this is a window and not any other widget that is in a random spot, and doesnt go away when minimizing and maximizing Maya
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self): #this just helps set the widget to any unique name we give it
        return "frugbkejrbgkjdbfg"
    

import maya.cmds as mc

class LimbRigger: # allows all these the inital values of the three joints of the limb and also creates a defualt size for the controllers within this class and its constuctor
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.controllerColor = QColor()

    def FindJointsBasedOnSelection(self):
        try: # this allows a fraction to be initialize the three values under and will become the top, middle, and end joints
            self.root = mc.ls(sl = True, type = "joint") [0] # the first selection of the rig so if there is a occuring error it will let the user know
            self.mid = mc.listRelatives(self.root, c = True, type = "joint")[0]
            self.end = mc.listRelatives(self.mid, c = True, type = "joint")[0]
        except Exception as e: # captures the exception here and raises it back
            raise Exception ("wrong selection, please select the first joint o fthe limb")

    def CreateFKControllerForJoint(self,jntName): #break down sections into smaller task which in turn creates the FkCtrls and joints with name functions
        ctrlName = "ac_l_fk_" + jntName # creates a name this joint
        ctrlGrpName = ctrlName + "_grp" # ctreate a name for this joint group
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0)) # this is the radius of the cicle which would equal to the controller size we created
        mc.group(ctrlName, n=ctrlGrpName) # is establishing the group name
        mc.matchTransform(ctrlGrpName, jntName) # to match transformation with the controls group based on the name
        mc.orientConstraint(ctrlName, jntName) # this creates  the constraint for the joints which will use the names we had set up
        return ctrlName, ctrlGrpName #will return the control name and the control group name
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply = True)
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def CreatePlusController(self,name):
        mel.eval(f"curve -n {name} -d 1 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.001627 0 4.014998 -p 6.027885 0 4.001211 -p 6.012511 0 4.997947 -p 5.012602 0 5.034713 -p 5.02592 0 5.999881 -p 3.989075 0 6.000681 -p 3.994619 0 5.003642 -p 2.996706 0 5.029282 -p 3.009883 0 3.989389 -p 3.988429 0 4.00692 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 ;")
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def GetObjectLocation(self, objectName):
        x,y,z = mc.xform(objectName, q = True, ws = True, t = True)
        return MVector(x,y,z)
    

    def PrintVector(self, vector):
        print(f"<{vector.x}, {vector.y}, {vector.z}>")
        

    def RigLimb(self): # this creates the controller for the three joints, roots, middle, and end. recalling two values the controller and group controller
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl) # this line is parrenting the groups through a established heirechy
        mc.parent(endCtrlGrp, midCtrl) # this line parents the end CTRL group and CTRL mid together and linking them to the end controller to the mid controller

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientContraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        self.PrintVector(rootJntLoc)


        ikHandleName = "ikhandle_" + self.end
        mc.ikHandle(n=ikHandleName, sol="ikRPsolver", sj = self.root, ee=self.end)

        poleVectorLocatopmVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVector = MVector(poleVectorLocatopmVals[0], poleVectorLocatopmVals[1], poleVectorLocatopmVals[2])
        poleVector.normalize()

        endJntLoc = self.GetObjectLocation(self.end)
        rootToEndVector = endJntLoc - rootJntLoc

        poleVectorCtrlLoc = rootJntLoc + rootToEndVector / 2 + poleVector * rootToEndVector.length()
        poleVectorCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n=poleVectorCtrl)
        poleVectorCtrlGrp = poleVectorCtrl + "_grp"
        mc.group(poleVectorCtrl, n=poleVectorCtrlGrp)
        mc.setAttr(poleVectorCtrlGrp + ".t", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, typ= "double3")

        mc.poleVectorConstraint(poleVectorCtrl, ikHandleName)

        ikfkBlendCtrl = "ac_ikfk_blend_" + self.root
        ikfkBlendCtrl, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrl)
        mc.setAttr(ikfkBlendCtrlGrp + ".t", rootJntLoc.x*2, rootJntLoc.y, rootJntLoc.z*2, typ="double3")

        ikfkBlendAttrName = "sc_ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttrName, min = 0, max= 1, k=True)
        ikfkBlendAttr = ikfkBlendCtrl + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikHandleName}.ikBlend={ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}. v={poleVectorCtrlGrp}.v={ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientContraint}.{endCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientContraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

        topGrpName = f"{self.root}_rig_grp"
        mc.group({rootCtrlGrp,ikEndCtrlGrp,poleVectorCtrlGrp,ikfkBlendCtrlGrp}, n= topGrpName)
        mc.parent(ikHandleName,ikEndCtrl)
 
        mc.setAttr(topGrpName+".overrideEnabled", 1)
        mc.setAttr(topGrpName+".overrideRGBColors",1)
 

class ColorPicker(QWidget):
    colorChanged = Signal(QColor)
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.pickColorBtn = QPushButton()
        self.pickColorBtn.setStyleSheet(f"background-color:black")
        self.pickColorBtn.clicked.connect(self.PickColorBtnClicked)
        self.masterLayout.addWidget(self.pickColorBtn)

    def PickColorBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.pickColorBtn.setStyleSheet(f"background-color:{self.color.name()}")
        self.colorChanged.emit(self.color)



class LimbRiggerWidget(MayaWindow): #this is going to be based on the window while using the same constructor but a diffrent parent
    def __init__(self):
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("limb Rigger")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout) # this gives us a layout to work with all dependent of the visual elements you add in will be laid out here


        toolTipLabel = QLabel("select the first joint of the limb, and press the auto find button") # this is the first joint of the limb
        self.masterLayout.addWidget(toolTipLabel) # this makes us a lable that will be added to the layout


        self.jntsListLineEdit = QLineEdit() # this is just a text field
        self.masterLayout.addWidget(self.jntsListLineEdit) # this allows our text field to be edited / typed into
        self.jntsListLineEdit.setEnabled(False) #set the enabled to the files so here it has been set to not enabled

        autoFindJntBtn = QPushButton() # Helps to create the button
        autoFindJntBtn.clicked.connect(self.AutoFindJntBtnClicked) #This says when button is found it can be clicked
        self.masterLayout.addWidget(autoFindJntBtn) 

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1,30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLable = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeSliderChanged)

        colorPicker = ColorPicker()
        colorPicker.colorChanged.connect(self.ColorPickerChanged)
        self.masterLayout.addWidget(colorPicker)


        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLable)
        self.masterLayout.addLayout(ctrlSizeLayout)

        rigLimbBtn = QPushButton("rig limb") # a button that instance and initaites the rigging proccess for the limb
        rigLimbBtn.clicked.connect(lambda: self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)
 
   

    def ColorPickerChanged(self, newColor: QColor):
        self.rigger.controllerColor[0] = newColor.redF()
        self.rigger.controllerColor[1] = newColor.greenF()
        self.rigger.controllerColor[2] = newColor.blueF()

    def CtrlSizeSliderChanged(self, newValue):
        self.ctrlSizeLable.setText(f"{newValue}")
        self.rigger.controllerSize = newValue

    def AutoFindJntBtnClicked(self):
        try:
            self.rigger.FindJointsBasedOnSelection()
            self.jntsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}") # this list and edits the joints text diplays
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}") # Queue messege box that displays what errors that may have occured.


limbRiggerWidget = LimbRiggerWidget() 
limbRiggerWidget.show()     # when we press Alt Shift M this send the code to maya and allows a window we customed made to show up into Maya.

GetMayaMainWindow()

