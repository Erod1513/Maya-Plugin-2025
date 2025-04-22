from MayaUtilis import *
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc

def TryAction(actionFunc):
    def wrapper(*args, **kwargs):
        try:
            actionFunc(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error!", f"{e}")

        return wrapper
    
class AnimClip:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min = True)
        self.frameMax = mc.playbackOptions(q=True, max= True)
        self.shouldExport = True

class MayaToUE:
    def __init__(self):
        self.rootjnt =""
        self.models = set()
        self.animations : list[AnimClip] = []
        self.fileName = ""
        self.saveDir = ""

    def AddNewAnimClip(self):
        self.animations.append(AnimClip())
        return self.animations[-1]

    def AddSelectedMeshes(self):
        selection = mc.ls(sl=True)

        if not selection:
            raise Exception("No meshes selected, please select all the meshes of your rig")
        
        meshes = []
        for sel in selection:
            if IsMesh(sel):
                meshes.append(sel)

        if len(meshes) == 0:
            raise Exception("No Mesh selected, please select all the meshes of your rig")
        
        self.models = meshes
        
        


    def AddRootJoint(self):
        if not self.rootjnt:
            raise Exception ("no root jnt assigned, please add the root joint of your rig first")
        
        if mc.objExists(self.rootjnt):
            currentRootPos = mc.xform(self.rootjnt, q = True, ws=True, t=True)
            if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
                raise Exception ("current root jnt is at origin already, no need to make a new one")
            
        mc.select(cl=True)
        rootJntName = self.rootjnt + "_root"
        mc.joint(n=rootJntName)
        mc.parent(self.rootjnt, rootJntName)
        self.rootjnt = rootJntName

    def SetSelectedJointAsRoot(self):
     selection = mc.ls(sl = True, type="joint")
     if not selection:
        raise Exception("wrong selection please select the root joint of your rig!")
     
     self.rootjnt = selection[0]

class AnimClipWidget(QWidget):
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        shouldExportCheckbox = QCheckBox()
        shouldExportCheckbox.setChecked(self.animClip.shouldExport)
        self.masterLayout.addWidget(shouldExportCheckbox)
        shouldExportCheckbox.toggled.connect(self.ShouldExportCheckBoxToggled)

        subfixLabel = QLabel("Subfix: ")
        self.masterLayout.addWidget(subfixLabel)

        subfixEdit = QLineEdit()
        subfixEdit.setValidator(QRegExpValidator("\w+"))
        subfixEdit.setText(self.animClip.subfix)
        subfixEdit.textChanged.connect(self.SubfixTextChanged)
        self.masterLayout.addWidget(subfixEdit)

        minFrameLabel = QLabel("Min: ")
        self.masterLayout.addWidget(minFrameLabel)
        minFrameLineEdit = QLineEdit()
        minFrameLineEdit.setValidator(QIntValidator())
        minFrameLineEdit.setText(str(int(self.animClip.frameMin)))
        minFrameLineEdit.textChanged.connect(self.MinFrameChanged)
        self.masterLayout.addWidget(minFrameLineEdit)


        maxFrameLabel = QLabel("Max: ")
        self.masterLayout.addWidget(maxFrameLabel)
        maxFrameLineEdit = QLineEdit()
        maxFrameLineEdit.setValidator(QIntValidator())
        maxFrameLineEdit.setText(str(int(self.animClip.frameMax)))
        maxFrameLineEdit.textChanged.connect(self.MaxFrameChanged)
        self.masterLayout.addWidget(maxFrameLineEdit)

        setRangeBtn = QPushButton("[-]")
        setRangeBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRangeBtn)

        deleteBtn = QPushButton("x")
        deleteBtn.clicked.connect(self.self.DeleteBtnClicked)
        self.masterLayout.addWidget(deleteBtn)
    
    def DeleteBtnClicke(self):
        self.deleteLater()

    def SetRangeBtnClicked(self):
        mc.playbackOptions(e=True, min= self.animClip.frameMin, max= self.animClip.frameMax)
        mc.playbackOptions(e=True, ast= self.animClip.frameMin, aet= self.animClip.frameMax)
    
    def MaxFrameChanged(self, newVal):
        self.animClip.frameMax = int(newVal)

    def MinFrameChanged(self, newVal):
        self.animClip.frameMin = int(newVal)
        

    def SubfixTextChanged(self, newText):
        self.animClip.subfix = newText

    def ShouldExportCheckBoxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

class MayaToUEWidget(MayaWindow):
    def GetWidgetUniqueName(self):
        return "MayaToUEWidget"
    

    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()

        self.setWindowTitle("Maya to UE")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectedAsRootJntBtn = QPushButton("Set Root Joint")
        setSelectedAsRootJntBtn.clicked.connect(self.SetSelectionAsRootJntBtnClicked)
        self.masterLayout.addWidget(setSelectedAsRootJntBtn)

        addRootJntBtn = QPushButton("Add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntBtnClicked)
        self.masterLayout.addWidget(addRootJntBtn)

        self.meshList = QListWidget()
        self.masterLayout.addWidget(self.meshList)
        self.meshList.setMaximumHeight(100)

        addMeshesBtn = QPushButton("Add Meshes")
        addMeshesBtn.clicked.connect(self.AddMeshesBtnClicked)
        self.masterLayout.addWidget(addMeshesBtn)

        addAnimEntryBtn = QPushButton("Add Animation clip")
        addAnimEntryBtn.clicked.connect(self.AddAnimEntryBtnClicked)
        self.masterLayout.addWidget(addAnimEntryBtn)

        self.animClipEntryLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.animClipEntryLayout)

    @TryAction
    def  AddAnimEntryBtnClicked(self):
        newAnimClip = self.mayaToUE.AddNewAnimClip()
        newAnimClipWidget = AnimClipWidget(newAnimClip)
        self.animClipEntryLayout.addWidget(newAnimClipWidget)

    @TryAction
    def AddMeshesBtnClicked(self):
        self.mayaToUE.AddSelectedMeshes()
        self.meshList.clear()
        self.meshList.addItems(self.mayaToUE.models)


    @TryAction
    def AddRootJntBtnClicked(self):
        self.mayaToUE.AddRootJoint()
        self.rootJntText.setText(self.mayaToUE.rootJnt)


    @TryAction
    def SetSelectionAsRootJntBtnClicked(self):
            self.mayaToUE.SetSelectedJointAsRoot()
            self.rootJntText.setText(self.mayaToUE.rootJnt)
       


MayaToUEWidget().show()        