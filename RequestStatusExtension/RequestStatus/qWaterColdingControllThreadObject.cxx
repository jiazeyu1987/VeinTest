#include "qWaterColdingControllThreadObject.h"

void qWaterColdingControllThreadObject::set_special_cmd(QString key, unsigned char* packet, QStringList valuelist) {
	std::unordered_map<QString, int> cmdToCode = {
	{"SetFan", 1},    // 设置风扇
	{"SetWaterPump", 2},  // 设置水泵
	{"SetVacuumPump", 3},  // 设置真空泵
	{"SetWaterBox", 4},  // 设置水箱
	{"SetColdFanPower", 5},  // 设置制冷风扇电源
	{"SetStepPara", 6},  // 设置步进参数
	{"SetOxygen", 7},  // 设置氧浓度
	{"Set24VPower", 8},  // 设置24V电源
	{"SetValve", 9},  // 设置阀门
	{"SetVMotorOrigin", 10},  // 设置电机回原点
	{"SetReferenceTemp", 11},  // 设置参考温度
	{"ManualHeating", 12},  // 手动制热
	{"SetCompressor", 13},  // 设置压缩机
	{"SetWaterBladderPID", 14},  // 设置水囊PID参数
	{"SetWaterBoxPID", 15},  // 设置水箱PID参数
	{"GetWorkStatus", 16}  // 读取工作状态
	};

	qDebug() << "Packet data:" << valuelist;

	qDebug() << "Send To cmd:" << key;
	auto it = cmdToCode.find(key);
	switch (it->second)
	{
	case 1:
		packet[2] = 0x03;
		packet[3] = 0x03;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		break;
	case 2:
		packet[2] = 0x03;
		packet[3] = 0x04;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		break;
	case 3:
		packet[2] = 0x03;
		packet[3] = 0x05;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		break;
	case 4:
		packet[2] = 0x03;
		packet[3] = 0x07;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		packet[9] = valuelist[7].toInt();
		packet[10] = valuelist[8].toInt();
		break;
	case 5:
		packet[2] = 0x03;
		packet[3] = 0x08;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		break;
	case 6:
		packet[2] = 0x03;
		packet[3] = 0x09;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		packet[9] = valuelist[7].toInt();
		packet[10] = valuelist[8].toInt();
		packet[11] = valuelist[9].toInt();
		packet[12] = valuelist[10].toInt();
		break;
	case 7:
		packet[2] = 0x03;
		packet[3] = 0x0A;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		packet[9] = valuelist[7].toInt();
		packet[10] = valuelist[8].toInt();
		packet[11] = valuelist[9].toInt();
		break;
	case 8:
		packet[2] = 0x03;
		packet[3] = 0x0B;
		packet[6] = valuelist[4].toInt();
		break;
	case 9:
		packet[2] = 0x03;
		packet[3] = 0x0C;
		packet[6] = valuelist[4].toInt();
		break;
	case 10:
		packet[2] = 0x03;
		packet[3] = 0x0D;
		packet[6] = valuelist[4].toInt();
		break;
	case 11:
		packet[2] = 0x03;
		packet[3] = 0x0E;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		packet[9] = valuelist[7].toInt();
		packet[10] = valuelist[8].toInt();
		break;
	case 12:
		packet[2] = 0x03;
		packet[3] = 0x0F;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		break;
	case 13:
		packet[2] = 0x03;
		packet[3] = 0x10;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		break;
	case 14:
		packet[2] = 0x04;
		packet[3] = 0x01;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		break;
	case 15:
		packet[2] = 0x04;
		packet[3] = 0x02;
		packet[6] = valuelist[4].toInt();
		packet[7] = valuelist[5].toInt();
		packet[8] = valuelist[6].toInt();
		break;
	case 16:
		packet[2] = 0x02;
		packet[3] = 0x02;
		break;
	default:
		break;
	}
}