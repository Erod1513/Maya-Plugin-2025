from PySide2.QtWidgets import QMainWindow,  QWidget # This imports all the ui widgets we are using to set up the LimbRigger.
from PySide2.QtCore import Qt  #Importing the QT core from Pyside to our Maya Plug in
import maya.OpenMayaUI as omui #this import for the maya Ui so it can be established in the code.
import shiboken2 #This allows to cast levels pointer into python
import maya.cmds as mc

def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
    
    for s in shapes:
        if mc.objectType("mesh"):
            return True
        
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"

def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetLowerStream(obj):
    return mc.listConnections(obj, s=False, d=True, sh=True)

def GetAllConnectionsIn(obj, nextFunc, filiter = None):
    allFound = []
    nexts = nextFunc(obj)
    serachDepth = 100
    while nexts and serachDepth > 0:
        serachDepth -= 1
        for next in nexts:
            allFound.add(next)

        nexts = nextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in allFound]
    
    if not filter:
        return List(allFound)
    
    filtered = []
    for found in allFound:
        if filter(found):
            filtered.append(found)
    
    return filtered


def GetMayaMainWindow(): #This make the maya window 
    mainWindow = omui.MQtUtil.mainWindow() #this retrieves the windw from maya
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow)
  
def DeleteWidgetWithName(name):
    for widget in GetMayaMainWindow().findChildren(QMainWindow, name):
        widget.deleteLater() # The window will be destory for next time when getting clean up.

class MayaWidow(QWidget):
    def __init__(self):
        super().__init__(parent = GetMayaMainWindow()) #with this line make it into a child of the main window.
        DeleteWidgetWithName(self.GetWidgetUniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetUniqueName())

    def GetWidgetUniqueName(self):
        return""