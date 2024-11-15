from Base.JBaseTest import JBaseTest
import vtk, qt, ctk, slicer, os
import slicer.util as util
class SNormalScalarManagerTest(JBaseTest):
  
  def runTest(self):
    self.module_path = os.path.realpath(__file__)
    self.module_directory = os.path.dirname(os.path.realpath(__file__))
    super().runTest()
  
  '''
  =============================================================================================
                                                case area
  =============================================================================================
  '''
  
  
  def case1(self):
    pass
  
  def case2(self):
    pass