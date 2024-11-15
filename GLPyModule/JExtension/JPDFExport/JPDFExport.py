import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget

class JPDFExport(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JPDFExport"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""



#
# JPDFExportWidget
#

class JPDFExportWidget(JBaseExtensionWidget):

  scale_width = 3.4
  scale_height = 3.4
  def setup(self):
    super().setup()

  def draw_label(self, painter, info, xpos, ypos, width, height, flag, fontPixelSize):
    x_ = xpos * self.scale_width
    y_ = ypos * self.scale_height
    width_ = width * self.scale_width
    height_ = height * self.scale_height
    rect = qt.QRect(x_, y_, width_, height_)
    font = painter.font()
    font.setPixelSize(fontPixelSize * self.scale_width)
    painter.setFont(font)
    painter.drawText(rect, flag, info)
 

  def draw_round_rect(self, painter, xpos, ypos, width, height, radius):
    x_ = xpos * self.scale_width
    y_ = ypos * self.scale_height
    width_ = width * self.scale_width
    height_ = height * self.scale_height
    rect = qt.QRect(x_, y_, width_, height_)
    painter.drawRoundRect(rect, radius, radius)
 

  def draw_color_block(self, painter, xpos, ypos, width, height):
    x_ = xpos * self.scale_width
    y_ = ypos * self.scale_height
    width_ = width * self.scale_width
    height_ = height * self.scale_height
    brush = qt.QBrush()
    brush.setColor(qt.QColor("#FF0"))
    brush.setStyle(qt.Qt.SolidPattern)
    painter.setBrush(brush)
    rect = qt.QRect(x_, y_, width_, height_)
    painter.drawRect(rect)
    brush.setStyle(qt.Qt.NoBrush)
    painter.setBrush(brush)
 

  def draw_image(self, painter, xpos, ypos, width, height, image):
    x_ = xpos * self.scale_width
    y_ = ypos * self.scale_height
    width_ = width * self.scale_width
    height_ = height * self.scale_height
    painter.drawPixmap(x_, y_, width_, height_, image)
 

  def paint_title(self, painter, title, info):
    self.draw_label(painter, title, 24, 18, 160, 29, qt.Qt.AlignLeft, 20)
    self.draw_label(painter, info, 294, 18, 300, 29, qt.Qt.AlignLeft, 20)
 

  def paint_line(self, painter):
    x0 = 13
    y0 = 68
    x1 = 696
    y1 = y0
    x0_ = x0 * self.scale_width
    y0_ = y0 * self.scale_height
    x1_ = x1 * self.scale_width
    y1_ = y1 * self.scale_height

    pen = qt.QPen(qt.Qt.black, 3)
    painter.setPen(pen)
    painter.drawLine(x0_, y0_, x1_, y1_)
    pen1 = qt.QPen(qt.Qt.black, 2)
    painter.setPen(pen1)
 

  def pdf_export(self, filename):
    pdfWriter = qt.QPdfWriter(filename)
    pdfWriter.setPageSize(qt.QPagedPaintDevice.A4)
    pdfWriter.setResolution(300)
    margin = 0
    pdfWriter.setPageMargins(qt.QMarginsF(margin, margin, margin, margin))
    painter = qt.QPainter(pdfWriter)
    self.paint_title(painter, '111', '222')
    self.paint_line(painter)

    xpos1 = 24
    xpos3 = 394
    ypos = 88
    lastPos = 976
    interType = 43
    picWidth = 671
    picHeight = 373
    pageNum = 1
    labelWidth = 160
    contentWidth = 160
    ablationWidth = 300

    self.draw_color_block(painter, xpos1, ypos, 8, 20)
    self.draw_label(painter, "Basic Information", 36, ypos - 3, 250, 26, qt.Qt.AlignLeft, 18)
    painter.end()
