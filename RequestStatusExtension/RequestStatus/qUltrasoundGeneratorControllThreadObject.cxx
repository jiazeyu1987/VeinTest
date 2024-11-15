#include "qUltrasoundGeneratorControllThreadObject.h"

void qUltrasoundGeneratorControllThreadObject::set_special_cmd(QString key, unsigned char* packet, QStringList valuelist) {
	if (key == "OldSetPower") {
		packet[2] = 0x03;
		packet[3] = 0x03;
		int power = valuelist[4].toInt();
		int hi = floor(power / 25);
		int low = round((power - hi * 25) / 25.0 * 255);
		packet[6] = hi;
		packet[7] = low;
	}
	else if (key == "SetVoltage") {
		packet[1] = 0xBA;
		packet[2] = 0x02;
		packet[3] = 0x02;
		int voltage = valuelist[4].toInt();
		int voltage_hi = int(voltage / 256);
		int voltage_low = int(voltage - voltage_hi * 256);
		packet[5] = voltage_hi;
		packet[4] = voltage_low;
		packet[6] = 0xA9;
	}
	else if (key == "SetPower") {
		packet[2] = 0x03;
		packet[3] = 0x03;
		qDebug() << valuelist[4].toInt() << "," << valuelist[5].toInt() << "," << valuelist[6].toInt() << "," << valuelist[7].toInt() << "," << valuelist[8].toInt() << "  sssssssss";
		int frequency = valuelist[4].toInt();
		int hi = int(frequency / 256);
		int low = int(frequency - hi * 256);
		packet[7] = hi;
		packet[6] = low;

		int voltage = valuelist[5].toInt();
		int voltage_hi = int(voltage / 256);
		int voltage_low = int(voltage - voltage_hi * 256);
		packet[9] = voltage_hi;
		packet[8] = voltage_low;

		int width = valuelist[6].toInt();
		int width_hi = int(width / 256);
		int width_low = int(width - width_hi * 256);
		packet[11] = width_hi;
		packet[10] = width_low;

		int cycle = valuelist[7].toInt();
		int cycle_hi = int(cycle / 256);
		int cycle_low = int(cycle - cycle_hi * 256);
		packet[13] = cycle_hi;
		packet[12] = cycle_low;

		int total = valuelist[8].toInt();
		int total_hi = int(total / 256);
		int total_low = int(total - total_hi * 256);
		packet[15] = total_hi;
		packet[14] = total_low;
	}
	else if (key == "StartGenerator") {
		packet[2] = 0x03;
		packet[3] = 0x04;
		packet[6] = valuelist[4].toInt();
	}
	else if (key == "SetWorkStatus") {
		packet[2] = 0x03;
		packet[3] = 0x02;
		packet[6] = valuelist[4].toInt();
	}
}