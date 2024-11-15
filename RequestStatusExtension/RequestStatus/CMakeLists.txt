
#-----------------------------------------------------------------------------
set(MODULE_NAME RequestStatus)
set(MODULE_TITLE ${MODULE_NAME})

string(TOUPPER ${MODULE_NAME} MODULE_NAME_UPPER)

set(BOOST_ROOT "C:/Boost")
find_package(Boost REQUIRED COMPONENTS system thread program_options)

#-----------------------------------------------------------------------------
add_subdirectory(Logic)
add_subdirectory(Widgets)
#-----------------------------------------------------------------------------
set(MODULE_EXPORT_DIRECTIVE "Q_SLICER_QTMODULES_${MODULE_NAME_UPPER}_EXPORT")

# Current_{source,binary} and Slicer_{Libs,Base} already included
set(MODULE_INCLUDE_DIRECTORIES
  ${CMAKE_CURRENT_SOURCE_DIR}/Logic
  ${CMAKE_CURRENT_BINARY_DIR}/Logic
  ${CMAKE_CURRENT_SOURCE_DIR}/Widgets
  ${CMAKE_CURRENT_BINARY_DIR}/Widgets
  ${Boost_INCLUDE_DIRS}
  ) 

set(MODULE_SRCS
  qSlicer${MODULE_NAME}Module.cxx
  qSlicer${MODULE_NAME}Module.h
  qSlicer${MODULE_NAME}ModuleWidget.cxx
  qSlicer${MODULE_NAME}ModuleWidget.h
  WorkerThread.h
  qReceiveThreadBaseObject.h
  qReceiveThreadBaseObject.cxx
  qControlThreadBaseObject.h
  qControlThreadBaseObject.cxx
  qIMEControllThreadObject.h
  qIMEControllThreadObject.cxx
  qIMEReceiveThreadObject.h
  qIMEReceiveThreadObject.cxx
  qNDIControllThreadObject.h
  qNDIControllThreadObject.cxx
  qNDIReceiveThreadObject.h
  qNDIReceiveThreadObject.cxx
  qElibotControllThreadObject.h
  qElibotControllThreadObject.cxx
  qElibotReceiveThreadObject.h
  qElibotReceiveThreadObject.cxx
  qURControllThreadObject.h
  qURControllThreadObject.cxx
  qURReceiveThreadObject.h
  qURReceiveThreadObject.cxx
  qUSBHidControllThreadObject.cxx
  qUSBHidControllThreadObject.h
  qUSBHidReceiveThreadObject.cxx
  qUSBHidReceiveThreadObject.h
  qWaterColdingReceiveThreadObject.h
  qWaterColdingControllThreadObject.h
  qWaterColdingReceiveThreadObject.cxx
  qWaterColdingControllThreadObject.cxx
  qUltrasoundGeneratorReceiveThreadObject.h
  qUltrasoundGeneratorControllThreadObject.h
  qUltrasoundGeneratorReceiveThreadObject.cxx
  qUltrasoundGeneratorControllThreadObject.cxx
  SystemCRC.h
  SystemCRC.cpp
  qPowerReceiveThreadObject.h
  qPowerControllThreadObject.h
  qPowerReceiveThreadObject.cxx
  qPowerControllThreadObject.cxx
  qRegisterReceiveThreadObject.h
  qRegisterControllThreadObject.h
  qRegisterReceiveThreadObject.cxx
  qRegisterControllThreadObject.cxx
  qSystemReceiveThreadObject.h
  qSystemReceiveThreadObject.cxx
  JQLibrary/jqcpumonitor.h
  JQLibrary/jqcpumonitor.inc
  JQLibrary/jqcpumonitor.cpp
  ElibotLib/robotUtils.cxx
  ElibotLib/robotUtils.h
  ElibotLib/json.hpp 
  qDeviceReceiveThreadObject.h
  qDeviceControllThreadObject.h
  qDeviceReceiveThreadObject.cxx
  qDeviceControllThreadObject.cxx

  qUltraImageReceiveThreadObject.h
  qUltraImageControllThreadObject.h
  qUltraImageReceiveThreadObject.cxx
  qUltraImageControllThreadObject.cxx
  )

set(MODULE_MOC_SRCS
  qSlicer${MODULE_NAME}Module.h
  qSlicer${MODULE_NAME}ModuleWidget.h
  qReceiveThreadBaseObject.h
  qControlThreadBaseObject.h
  qIMEControllThreadObject.h
  qIMEReceiveThreadObject.h 
  qNDIControllThreadObject.h
  qNDIReceiveThreadObject.h 
  qElibotControllThreadObject.h
  qElibotReceiveThreadObject.h
  qURControllThreadObject.h
  qURReceiveThreadObject.h
  qUSBHidReceiveThreadObject.h
  qUSBHidControllThreadObject.h
  qWaterColdingControllThreadObject.h
  qWaterColdingReceiveThreadObject.h
  qPowerReceiveThreadObject.h
  qPowerControllThreadObject.h
  qRegisterReceiveThreadObject.h
  qRegisterControllThreadObject.h
  qUltrasoundGeneratorReceiveThreadObject.h
  qUltrasoundGeneratorControllThreadObject.h
  ElibotLib/robotUtils.h
  qSystemReceiveThreadObject.h
  JQLibrary/jqcpumonitor.h
  qDeviceReceiveThreadObject.h
  qDeviceControllThreadObject.h
  qUltraImageReceiveThreadObject.h
  qUltraImageControllThreadObject.h
  ) 

set(MODULE_UI_SRCS
  Resources/UI/qSlicer${MODULE_NAME}ModuleWidget.ui
  )
 
link_directories(UltraSDK/Target/bin64)
link_directories(UltraSDK/Target/lib64)
link_directories(USBLib/Release)
set(JLib 
	hidapi.lib
  UltraSDK.lib
  ) 
 
link_directories(URLib/libs)
set(URLib 
	rtde.lib)

set(MODULE_TARGET_LIBRARIES
  vtkSlicer${MODULE_NAME}ModuleLogic
  qSlicer${MODULE_NAME}ModuleWidgets
  ${Boost_SYSTEM_LIBRARY}
  ${Boost_THREAD_LIBRARY}
  ${JLib} 
  ${URLib}
  )
 
set(MODULE_RESOURCES
  Resources/qSlicer${MODULE_NAME}Module.qrc
  )

option(DEBUG_ALIGN "Enable debug alignment" OFF)

include_directories(UltraSDK/Target/include)
include_directories(USBLib/include)
include_directories(ur_rtde)
 
if (DEBUG_ALIGN)
    message("Debug online alignment in NIR STEREO Camera")
    add_definitions(-DDEBUG_ALIGN_MODULE)
    include_directories(IMELib/include D:/medical_projects/breathcurve/MarkerAlign/ D:/medical_projects/breathcurve/build/MarkerAlign)
    set(CMAKE_BUILD_TYPE "Release")
    if(CMAKE_BUILD_TYPE MATCHES "Debug")
        list(APPEND MODULE_TARGET_LIBRARIES AimPosition2.3.3d)
        link_directories(IMELib/Debug)
        message(status " Debug Build")
    elseif (CMAKE_BUILD_TYPE MATCHES "Release")
        list(APPEND MODULE_TARGET_LIBRARIES AimPosition2.3.3 qSlicerMarkerAlignModule qSlicerMarkerAlignModuleWidgets vtkSlicerMarkerAlignModuleLogic)
        link_directories(IMELib/Release D:/medical_projects/breathcurve/build/lib/Slicer-5.2/qt-loadable-modules/Release)
        message(status " Release Build")
    endif()
else()
    message("Don't Debug online alignment in NIR STEREO Camera")
    include_directories(IMELib/include)
    set(CMAKE_BUILD_TYPE "Release")
    if(CMAKE_BUILD_TYPE MATCHES "Debug")
        list(APPEND MODULE_TARGET_LIBRARIES AimPosition2.3.3d)
        link_directories(IMELib/Debug)
        message(status " Debug Build")
    elseif (CMAKE_BUILD_TYPE MATCHES "Release")
        list(APPEND MODULE_TARGET_LIBRARIES AimPosition2.3.3)
        link_directories(IMELib/Release)
        message(status " Release Build")
    endif()
endif()

#-----------------------------------------------------------------------------
slicerMacroBuildLoadableModule(
  NAME ${MODULE_NAME}
  TITLE ${MODULE_TITLE}
  EXPORT_DIRECTIVE ${MODULE_EXPORT_DIRECTIVE}
  INCLUDE_DIRECTORIES ${MODULE_INCLUDE_DIRECTORIES}
  SRCS ${MODULE_SRCS}
  MOC_SRCS ${MODULE_MOC_SRCS}
  UI_SRCS ${MODULE_UI_SRCS}
  TARGET_LIBRARIES ${MODULE_TARGET_LIBRARIES}
  RESOURCES ${MODULE_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
