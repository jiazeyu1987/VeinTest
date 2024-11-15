import slicer,vtk,ctk,qt,os
import slicer.util as util



class SubProject:
  main = None
  TagMaps = {}
  def __init__(self,main):
    self.main = main

  def init_sub_project(self):
    print("init_sub_project")
   
  
  def after_init_from_data(self):
    from RDNTool.RDNFSM import RDNFSM
    util.rdn_communicate_log_init()
    util.global_data_map['fsm'] = RDNFSM()

    util.global_data_map['width'] = 1920
    util.global_data_map['height'] = 1080
    util.global_data_map['gap'] = 9
    util.global_data_map['offset'] = 0
    
    slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)