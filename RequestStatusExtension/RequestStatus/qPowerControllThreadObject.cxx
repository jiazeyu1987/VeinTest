#include "qPowerControllThreadObject.h"

void qPowerControllThreadObject::set_special_cmd(QString key, unsigned char* packet, QStringList valuelist) {

    if (key == "SetPower") {
        packet[2] = 0x03;
        packet[3] = 0x03;
        int power = valuelist[4].toInt();
        packet[6] = (power >> 8) & 0xFF;
        packet[7] = power & 0xFF;
    }
    else if (key == "StartGenerator") {
        packet[2] = 0x03;
        packet[3] = 0x04;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "ResetMCU") {
        packet[2] = 0x03;
        packet[3] = 0x01;
    }
    else if (key == "NDIPower") {
        packet[2] = 0x03;
        packet[3] = 0x07;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "WaterPower") {
        packet[2] = 0x03;
        packet[3] = 0x06;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "PCPower") {
        packet[2] = 0x03;
        packet[3] = 0x05;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "RobotPower") {
        packet[2] = 0x03;
        packet[3] = 0x04;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "PAPower") {
        packet[2] = 0x03;
        packet[3] = 0x03;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "SetFan") {
        packet[2] = 0x03;
        packet[3] = 0x09;
        packet[6] = valuelist[4].toInt();
    }
    else if (key == "SetRobotControl") {
        packet[2] = 0x03;
        packet[3] = 0x08;
        packet[6] = valuelist[4].toInt();
        packet[7] = valuelist[5].toInt();
        packet[8] = valuelist[6].toInt();
        packet[9] = valuelist[7].toInt();
    }
}
