#ifndef __qSlicerRequestStatusModuleWidgetqURReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqURReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
#include "QMutex.h"
#include <ur_rtde/rtde_receive_interface.h>
#include <bitset>
class qURReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
    void GetRobotStatus();
    void GetFlangePos();
    void GetVirtualOutput();
    void GetTcpPos();
    void GetToolNumber();
    void GetCollapseState();
    void GetCollapseSensitivity();
    void GetSpeed();
    void GetJointPositions();
    void GetJointVelocities();
    void GetSafetyStatusBit();
    void GetFreedriveStatus();
    void GetDigitalInStatus();
    void GetMainVoltage();
    void GetRobotVoltage();
    void GetRobotCurrent();
    void GetJointVoltage();
    void GetJointCurrent();
    void GetJointTemperatures();
    void GetProgramRunningStatus();
public:
    ur_rtde::RTDEReceiveInterface* handler = nullptr;
    std::string CONNECT_STATUS = "connect_status";
    std::string FLANGE_POS = "flange_pos";
    std::string VIRTUAL_OUTPUT = "virutal_output";
    std::string TCP_POS = "tcp_pos";
    std::string TOOL_NUMBER = "tool_number";
    std::string COLLAPSE_STATE = "collapse_state";
    std::string COLLAPSE_SENSITIVITY = "collapse_sensitivity";
    std::string SPEED = "speed";
    std::string JOINT_POSITIONS = "joint_positions";
    bool IS_FREEDRIVE_STATE = false;
};


#endif