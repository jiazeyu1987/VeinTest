#include "qDeviceControllThreadObject.h"
#include "qDeviceReceiveThreadObject.h"
void qDeviceControllThreadObject::send_thread_cmd(QString cmd) {
    {
        QStringList list1 = cmd.split(", ");
        if (list1.length() < 2) {
            return;
        }
        if (list1[0] != "Device") {
            return;
        }
        if (list1[1] == "SetGapMax") {
            if (list1.length() == 3)
                obj->gap_max = list1[2].toInt();
            return;
        }
    }
}

