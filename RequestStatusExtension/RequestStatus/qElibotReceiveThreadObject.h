#ifndef __qSlicerRequestStatusModuleWidgetqElibotReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqElibotReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
#include <ElibotLib/robotUtils.h>
#include "QMutex.h"
class qElibotReceiveThreadObject : public qReceiveThreadBaseObject
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
public:
    std::string CONNECT_STATUS = "connect_status";
    std::string FLANGE_POS = "flange_pos";
    std::string VIRTUAL_OUTPUT = "virutal_output";
    std::string TCP_POS = "tcp_pos";
    std::string TOOL_NUMBER = "tool_number";
    std::string COLLAPSE_STATE = "collapse_state";
    std::string COLLAPSE_SENSITIVITY = "collapse_sensitivity";
    std::string SPEED = "speed";
    RobotConntroller conntro;
};


#endif