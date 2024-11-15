#ifndef __qSlicerRequestStatusModuleWidgetqDeviceReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqDeviceReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include "QMutex.h"
#include <qReceiveThreadBaseObject.h>
class qDeviceReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
public:
    int tick = 1;
    qDeviceReceiveThreadObject();
    ~qDeviceReceiveThreadObject();
};


#endif