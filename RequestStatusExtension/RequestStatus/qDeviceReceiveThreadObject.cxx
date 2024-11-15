#include "qDeviceReceiveThreadObject.h"

qDeviceReceiveThreadObject::qDeviceReceiveThreadObject() {}
qDeviceReceiveThreadObject::~qDeviceReceiveThreadObject() {}
void qDeviceReceiveThreadObject::OnReceiveObjectInnerTick() {
	tick++;
	map_info["tick"] = QString::number(tick).toStdString();
} 