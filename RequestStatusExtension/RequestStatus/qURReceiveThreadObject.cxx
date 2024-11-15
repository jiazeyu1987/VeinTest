#include "qURReceiveThreadObject.h"


void qURReceiveThreadObject::OnReceiveObjectInnerTick() {
    GetRobotStatus();
    //GetCollapseSensitivity();
    //GetCollapseState();
    //GetToolNumber();
   // GetVirtualOutput();
    //GetFlangePos();
    GetTcpPos();
    //GetSpeed();
    GetJointPositions();
    GetJointVelocities();
    GetSafetyStatusBit();
    GetFreedriveStatus();
    GetDigitalInStatus();
    GetMainVoltage();
    GetRobotVoltage();
    GetRobotCurrent();
    GetJointVoltage();
    GetJointCurrent();
    GetJointTemperatures();
    GetProgramRunningStatus();
}



void qURReceiveThreadObject::GetSpeed() {
    if (handler) {
        std::string str1= "";
        std::vector<double> spes = handler->getActualTCPSpeed();
        for (int i = 0; i < spes.size(); i++) {
            str1 = str1 + QString::number(spes[i]).toStdString() + " ";
        }
        map_info[SPEED] = str1;
    }
}

void qURReceiveThreadObject::GetCollapseSensitivity() {
}

void qURReceiveThreadObject::GetCollapseState() {
}

void qURReceiveThreadObject::GetToolNumber() {
}

void qURReceiveThreadObject::GetTcpPos() {
	if (handler) {
		std::string str1 = "";
		std::vector<double> spes = handler->getActualTCPPose();
		for (int i = 0; i < spes.size(); i++) {
			str1 = str1 + QString::number(spes[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
		map_info[TCP_POS] = str1;
	}
}

void qURReceiveThreadObject::GetVirtualOutput() {
}

void qURReceiveThreadObject::GetRobotStatus() {
	if (handler && handler->isConnected()) {
		map_info[CONNECT_STATUS] = "3";
		//qDebug() << "GetRobotStatus ------  is 3";
	}
	else {
		map_info[CONNECT_STATUS] = "-1";
		//qDebug() << "GetRobotStatus ------  is 1";
	}
}

void qURReceiveThreadObject::GetFlangePos() {
}

void qURReceiveThreadObject::GetJointPositions() {
	if (handler) {
		std::string str1 = "";
		std::vector<double> spes = handler->getActualQ();
		for (int i = 0; i < spes.size(); i++) {
			str1 = str1 + QString::number(spes[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
		map_info[JOINT_POSITIONS] = str1;
	}
}

void qURReceiveThreadObject::GetJointVelocities() {
    if (handler) {
        std::string str1 = "";
		std::vector<double> spes = handler->getActualQd();
		for (int i = 0; i < spes.size(); i++) {
			str1 = str1 + QString::number(spes[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
		map_info["joint_velocities"] = str1;
    }
}

void qURReceiveThreadObject::GetFreedriveStatus() {
    // if (handler) {
    //     uint32_t stat = handler->getRobotStatus();
    //     bool res = (stat >> 2) & 1;
    //     map_info["IS_FREEDRIVE_STATE"] = res ? "1" : "0";
    // }
    map_info["IS_FREEDRIVE_STATE"] = IS_FREEDRIVE_STATE ? "1" : "0";
}

void qURReceiveThreadObject::GetDigitalInStatus() {
    if (handler) {
        bool res_ti_0 = handler->getDigitalInState(16);
        bool res_ti_1 = handler->getDigitalInState(17);
        map_info["IS_DIGITAL_TOOL_INPUT_0"] = res_ti_0 ? "1" : "0";
        map_info["IS_DIGITAL_TOOL_INPUT_1"] = res_ti_1 ? "1" : "0";
    }
}

void qURReceiveThreadObject::GetMainVoltage() {
    if (handler) {
        double res = handler->getActualMainVoltage();
        map_info["main_voltage"] = QString::number(res).toStdString();
    }
}

void qURReceiveThreadObject::GetRobotVoltage() {
    if (handler) {
        double res = handler->getActualRobotVoltage();
        map_info["robot_voltage"] = QString::number(res).toStdString();
    }
}

void qURReceiveThreadObject::GetRobotCurrent() {
    if (handler) {
        double res = handler->getActualRobotCurrent();
        map_info["robot_current"] = QString::number(res).toStdString();
    }
}

void qURReceiveThreadObject::GetJointVoltage() {
    if (handler) {
        std::string str1 = "";
        std::vector<double> res = handler->getActualJointVoltage();
        for (int i = 0; i < res.size(); i++) {
			str1 = str1 + QString::number(res[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
        map_info["joint_voltage"] = str1;
    }
}

void qURReceiveThreadObject::GetJointCurrent() {
    if (handler) {
        std::string str1 = "";
        std::vector<double> res = handler->getActualCurrent();
        for (int i = 0; i < res.size(); i++) {
			str1 = str1 + QString::number(res[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
        map_info["joint_current"] = str1;
    }
}

void qURReceiveThreadObject::GetJointTemperatures() {
    if (handler) {
        std::string str1 = "";
        std::vector<double> res = handler->getJointTemperatures();
        for (int i = 0; i < res.size(); i++) {
			str1 = str1 + QString::number(res[i]).toStdString() + ",";
		}
		if (str1.length() > 0)
			str1.pop_back();
        map_info["joint_temperature"] = str1;
    }
}

void qURReceiveThreadObject::GetSafetyStatusBit() {
	if (handler) {
		uint32_t bits = handler->getSafetyStatusBits();
		std::bitset<11> safety_bits(bits);
		map_info["IS_NORMAL_MODE"] = safety_bits[0] ? "1" : "0";
		map_info["IS_REDUCED_MODE"] = safety_bits[1] ? "1" : "0";
		map_info["IS_PROTECTIVE_STOPPED"] = safety_bits[2] ? "1" : "0";
		map_info["IS_RECOVERY_MODE"] = safety_bits[3] ? "1" : "0";
		map_info["IS_SAFEGUARD_STOPPED"] = safety_bits[4] ? "1" : "0";
		map_info["IS_SYSTEM_EMERGENCY_STOPPED"] = safety_bits[5] ? "1" : "0";
		map_info["IS_ROBOT_EMERGENCY_STOPPED"] = safety_bits[6] ? "1" : "0";
		map_info["IS_EMERGENCY_STOPPED"] = safety_bits[7] ? "1" : "0";
		map_info["IS_VIOLATION"] = safety_bits[8] ? "1" : "0";
		map_info["IS_FAULT"] = safety_bits[9] ? "1" : "0";
		map_info["IS_STOPPED_DUE_TO_SAFETY"] = safety_bits[10] ? "1" : "0";
	}
}

void qURReceiveThreadObject::GetProgramRunningStatus() {
    if (handler) {
        uint32_t bits = handler->getRobotStatus();
        std::bitset<11> status_bits(bits);
        map_info["IS_PROGRAM_RUNNING"] = status_bits[1] ? "1" : "0";
    }
}