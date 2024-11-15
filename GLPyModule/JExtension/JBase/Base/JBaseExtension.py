import vtk, qt, ctk, slicer, os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util




class JBaseExtensionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  TagMaps = {}
  classname = None
  filename = None
  uiWidget = None
  logic = None
  test = None
  paras = {}
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self.test = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    self.classname = self.__class__.__name__
    index = self.classname.find("Widget")
    if index != -1:
        self.filename = self.classname[:index]
    else:
      raise Exception("error class name of:",self.classname)
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout
    print("test", self.resourcePath('UI/%s.ui')%(self.filename))
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/%s.ui')%(self.filename))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    uiWidget.setMRMLScene(slicer.mrmlScene)
    self.uiWidget = uiWidget
    self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent, self.OnArchiveLoaded)
    self.TagMaps[util.SceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.SceneDestroyEvent, self.OnSceneDestroyEvent)
    self.TagMaps[util.BeforeSceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.BeforeSceneDestroyEvent, self.OnBeforeSceneDestroyEvent)

    # module_path = self.filename+"Logic"
    # import importlib
    # module = importlib.import_module(module_path)

    self.init_ui()

  def init_ui(self):
    pass

  def enter(self):
    print("--------------------------------")
    self.addEvent(True)
    
  def exit(self):
    self.addEvent(False)

  def addEvent(self,boolVal):
    return

  def OnArchiveLoaded(self,_a,_b):
    print(f"load archive from {self.__class__.__name__}")

  def OnSceneDestroyEvent(self,_a,_b):
    pass
  
  
  def OnBeforeSceneDestroyEvent(self,_a,_b):
    pass