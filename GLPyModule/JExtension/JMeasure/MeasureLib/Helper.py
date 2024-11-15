from __main__ import vtk, slicer

class JMeasureTool:
  layout = None
  btn = None
  label = None
  slider = None
  timer = None
  para = {}
  def __init__(self,layoutin,btnin,labelin):
    self.label = labelin
    self.layout = layoutin
    self.btn = btnin

