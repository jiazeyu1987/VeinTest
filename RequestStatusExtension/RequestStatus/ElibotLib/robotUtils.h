#ifndef __robotUtils_h
#define __robotUtils_h

#include <string>
#include <Winsock2.h>
#include <iostream>
#include <fstream>
#include <ctime>
#include "json.hpp"
#include <vector>
#include "QMutex.h"
using json = nlohmann::json;


struct FunctionResult {
	
	int successCode;  
	std::vector<std::string> msgList;   

	FunctionResult() : successCode(0), msgList({}) {

	}
};
class RobotConntroller {

public:
	RobotConntroller();
	FunctionResult connectEtController(std::string ip, int port);
    void disconnectEtController();
    json moveByJoint(double targetPos[6], int speed = 20, int acc = 20, int dec = 20);
    json setSysVarV(int vnum, double targetPose[6]);
	std::vector<float> getBaseFlangePose();
	json sendCmd(std::string method, json Params, int id, ...);
    std::vector<float> stringToVector(std::string jsonstr);
	json positiveKinematic(std::string jointInformation);
	json inverseKinematic(std::string poseInformation, int unit_type = 0);
	int default_speed = 30;
	int default_acc = 20;
	int default_dec = 20;
	QMutex mutex;
public:
	SOCKADDR_IN server_addr;
	SOCKET ServerSocket;
	int ServerAddrSize;
	json params;
};
#endif
