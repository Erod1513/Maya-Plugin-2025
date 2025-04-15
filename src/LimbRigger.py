from PySide2.QtGui import QColor
from PySide2.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget  #here we're just importing / downloading what we need to make certain funtions witin our code work properly
from PySide2.QtCore import Qt, Signal      
from maya.OpenMaya import MVector
import maya.OpenMayaUI as omui
import maya.mel as mel
import shiboken2   

def GetMayaMainWindow()->QMainWindow:       
    mainWindow = omui.MQtUtil.mainWindow()         
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)

def DeleteWidgetWithName(name): 
    for widget in GetMayaMainWindow().findChildren(QWidget, name):
        widget.deleteLater()  

class MayaWindow(QWidget):     
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow()) 
        DeleteWidgetWithName(self.GetWidgetUniqueName()) 
        self.setWindowFlags(Qt.WindowType.Window) 
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self): 
        return "frugbkejrbgkjdbfg"
    

import maya.cmds as mc

class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.controllerColor = [0,0,0]
        self.CreatedController = []

    def FindJointsBasedOnSelection(self):
        try: 
            self.root = mc.ls(sl = True, type = "joint") [0] 
            self.mid = mc.listRelatives(self.root, c = True, type = "joint")[0]
            self.end = mc.listRelatives(self.mid, c = True, type = "joint")[0]
        except Exception as e: 
            raise Exception ("wrong selection, please select the first joint o fthe limb")

    def CreateFKControllerForJoint(self,jntName): 
        ctrlName = "ac_l_fk_" + jntName 
        ctrlGrpName = ctrlName + "_grp" 
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0)) 
        mc.group(ctrlName, n=ctrlGrpName) 
        mc.matchTransform(ctrlGrpName, jntName) 
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName 
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -0.5 0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply = True)
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        self.CreatedController.append(name)
        return name, grpName
    
    def CreatePlusController(self,name):
        mel.eval(f"curve -n {name} -d 1 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.000584 0 3.007831 -p 5.001627 0 4.014998 -p 6.027885 0 4.001211 -p 6.012511 0 4.997947 -p 5.012602 0 5.034713 -p 5.02592 0 5.999881 -p 3.989075 0 6.000681 -p 3.994619 0 5.003642 -p 2.996706 0 5.029282 -p 3.009883 0 3.989389 -p 3.988429 0 4.00692 -p 3.998356 0 3.001427 -p 5.000584 0 3.007831 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 ;")
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        self.CreatedController.append(name)
        return name, grpName
    
    def ChangeControllerColors(self, rgbcolor):
        for ctrl in self.CreatedController:
            if mc.objExists(ctrl):
                mc.setAttr(ctrl + ".overrideEnabled", 1)
                mc.setAttr(ctrl+ ".overrideRGBcolors", 1)
                mc.setAttr(ctrl+".overrideColorRGB", rgbcolor[1], rgbcolor[2], type="double3")
    
    def GetObjectLocation(self, objectName):
        x,y,z = mc.xform(objectName, q = True, ws = True, t = True)
        return MVector(x,y,z)
    

    def PrintVector(self, vector):
        print(f"<{vector.x}, {vector.y}, {vector.z}>")
        

    def RigLimb(self): 
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl) 
        mc.parent(endCtrlGrp, midCtrl) 

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
        mc.setAttr(topGrpName+".overrideRGB", self.controllerColor[0], self.controllerColor[1], self.controllerColor[2], type="double3")
 

class ColorPicker(QWidget):
    colorChanged = Signal(QColor)
    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.color = QColor()
        self.setLayout(self.masterLayout)
        self.pickColorBtn = QPushButton()
        self.pickColorBtn.setStyleSheet(f"background-color:black")
        self.pickColorBtn.clicked.connect(self.PickColorBtnClicked)
        self.masterLayout.addWidget(self.pickColorBtn)

    def PickColorBtnClicked(self):
        self.color = QColorDialog.getColor()
        self.pickColorBtn.setStyleSheet(f"background-color:{self.color.name()}")
        self.colorChanged.emit(self.color)

            

class LimbRiggerWidget(MayaWindow): 
    def __init__(self):
        super().__init__()
        self.rigger = LimbRigger()
        self.setWindowTitle("limb Rigger")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout) 


        toolTipLabel = QLabel("select the first joint of the limb, and press the auto find button") 
        self.masterLayout.addWidget(toolTipLabel) 


        self.jntsListLineEdit = QLineEdit() 
        self.masterLayout.addWidget(self.jntsListLineEdit) 
        self.jntsListLineEdit.setEnabled(False) 

        autoFindJntBtn = QPushButton("Auto Find") 
        autoFindJntBtn.clicked.connect(self.AutoFindJntBtnClicked) 
        self.masterLayout.addWidget(autoFindJntBtn) 

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1,30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLable = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeSliderChanged)

        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLable)
        self.masterLayout.addLayout(ctrlSizeLayout)

        colorPicker = ColorPicker()
        colorPicker.colorChanged.connect(self.ColorPickerChanged)
        self.masterLayout.addWidget(colorPicker)

        rigLimbBtn = QPushButton("Rig limb") 
        rigLimbBtn.clicked.connect(lambda: self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)
        
        pickColorBtn = QPushButton("Color Change") # this will be changed as a proper color change color for the joints after the functions has been defined
        pickColorBtn.clicked.connect(self.ChangeControllerColorChange) # but for now it works the same as the rig limb button
        self.masterLayout.addWidget(pickColorBtn)

    def ColorPickerChanged(self, newColor: QColor):
        self.rigger.controllerColor[0] = newColor.redF()
        self.rigger.controllerColor[1] = newColor.greenF()
        self.rigger.controllerColor[2] = newColor.blueF()

    def ChangeControllerColorChange(self):
        self.rigger.ChangeControllerColors(self.rigger.controllerColor)

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

