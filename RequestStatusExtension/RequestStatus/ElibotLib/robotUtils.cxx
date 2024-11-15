#include "robotUtils.h"
#include "qdebug.h"
#include <vector>

RobotConntroller::RobotConntroller() {
}

void RobotConntroller::disconnectEtController() {
	closesocket(ServerSocket);
}

json RobotConntroller::sendCmd(std::string method, json Params, int id, ...) {
	mutex.lock();
	json send, recv_json, empty;
	try {
		char RecvBuf[1024] = "";
		std::string SendBuf = "";
		int send_len = 0, recv_len = 0, BufLen = 1024;
		auto s2 = Params.size();
		if (s2 == 0)
		{
			send = { {"jsonrpc","2.0"},{"method",method},{"id",id} };
		}
		else
		{
			send = { {"jsonrpc","2.0"},{"method",method},{"params",Params},{"id",id} };
		}
		std::string str = send.dump() + "\r\n";
		send_len = sendto(ServerSocket, str.c_str(), str.size(), 0, (SOCKADDR*)&server_addr, sizeof(server_addr));
		recv_len = recvfrom(ServerSocket, RecvBuf, BufLen, 0, (SOCKADDR*)&server_addr, &ServerAddrSize);
		QString myString = QString::fromUtf8(RecvBuf);
		QString ip = QString(inet_ntoa(server_addr.sin_addr));
		if (recv_len == -1) {
			mutex.unlock();
			return empty;
		}
		recv_json = json::parse(RecvBuf);
		int read_id = recv_json["id"];
		if (recv_json["result"] == nullptr)
		{
			recv_json["result"] = false;
			params.clear();
			mutex.unlock();
			return recv_json;
		}
		std::string read_result = recv_json["result"];
		int start = read_result.find("[");

		if (start > -1)
		{
			int end = read_result.find_last_of("]");
			if (end > -1)
			{
				std::string ret_str = read_result.substr(start + 1, end - 1);
				start = ret_str.find("[");
				while (start != -1) {
					ret_str.replace(start, std::string("[").length(), "");
					start = ret_str.find("[");
				}
				end = ret_str.find_last_of("]");
				while (end != -1) {
					ret_str.replace(end, std::string("]").length(), "");
					end = ret_str.find("]");
				}
				std::vector<double> result;
				std::string::size_type i = 0;
				std::string::size_type found = ret_str.find(",");
				while (found != std::string::npos) {
					result.push_back(atof(const_cast<const char*>(ret_str.substr(i, found - i).c_str())));
					i = found + 1;
					found = ret_str.find(",", i);
				}
				result.push_back(atof(const_cast<const char*>(ret_str.substr(i, ret_str.size(
				) - i).c_str())));
				recv_json["result"] = result;
			}
		}
		params.clear();
	}
	catch (const std::exception& e) {
		// �����쳣
		qDebug() << "catch exception:" << e.what();
	}
	mutex.unlock();
	return recv_json;
}

json RobotConntroller::moveByJoint(double targetPos[6], int speed, int acc, int dec) {
	json json_result, params;
	double targetPos_[6];
	for (int i = 0; i < 6; i++) {
		targetPos_[i] = targetPos[i];
	}
	params["targetPos"] = targetPos_, params["speed"] = speed, params["acc"] = acc, params["dec"] = dec;
	json_result = sendCmd("moveByJoint", params, 1);
	return json_result;
}

json RobotConntroller::setSysVarV(int vnum, double targetPose[6]) {
	json json_result, params;
	return json_result;
}

FunctionResult RobotConntroller::connectEtController(std::string ip, int port)
{
	ServerAddrSize = sizeof(server_addr);
	WORD w_req = MAKEWORD(2, 2);
	WSADATA wsadata;
	int err;
	FunctionResult ret_result = FunctionResult();
	err = WSAStartup(w_req, &wsadata);
	if (err != 0) {
		ret_result.msgList.push_back("Init socket failed!\n");
	}
	else {
		ret_result.msgList.push_back("Init socket successed!\n");
	}
	if (LOBYTE(wsadata.wVersion) != 2 || HIBYTE(wsadata.wHighVersion) != 2) {
		ret_result.msgList.push_back("Socket version not supported!\n");
		WSACleanup();
	}
	else {
		ret_result.msgList.push_back("Socket version matched!\n");
	}
	server_addr.sin_family = AF_INET;
	server_addr.sin_addr.S_un.S_addr = inet_addr(ip.c_str());
	server_addr.sin_port = htons(port);
	ServerSocket = socket(AF_INET, SOCK_STREAM, 0);
	int nZero = 0;
	setsockopt(ServerSocket, SOL_SOCKET, SO_SNDBUF, (char*)&nZero, sizeof(nZero));
	u_long is_non_block = 1;
	int ret = ioctlsocket(ServerSocket, FIONBIO, &is_non_block);
	ret = connect(ServerSocket, (struct sockaddr*)&server_addr, sizeof(server_addr
		));
	fd_set fsWrite;
	FD_ZERO(&fsWrite);
	FD_SET(ServerSocket, &fsWrite);
	struct timeval timeout;
	timeout.tv_sec = 1;
	timeout.tv_usec = 0;
	ret = select(0, 0, &fsWrite, 0, &timeout);
	if (ret == 0) {
		ret_result.msgList.push_back("Connect server failed! Please check your network or ip address!");
		ret_result.successCode = -1;
		return ret_result;
	}
	else
	{
		is_non_block = 0;
		ret = ioctlsocket(ServerSocket, FIONBIO, &is_non_block);
		ret_result.msgList.push_back("Connect server success!");
		ret_result.successCode = 1;
		return ret_result;
	}
}

std::vector<float> RobotConntroller::stringToVector(std::string jsonstr)
{
	std::vector<float> output_vec;
	std::string delimiter = ",";

	size_t pos = 0;
	while ((pos = jsonstr.find(delimiter)) != std::string::npos) {
		std::string token = jsonstr.substr(0, pos);
		float tokenFloat = atof(token.c_str());
		output_vec.push_back(tokenFloat);
		jsonstr.erase(0, pos + delimiter.length());
	}
	output_vec.push_back(atof(jsonstr.c_str()));
	return output_vec;
}

std::vector<float> RobotConntroller::getBaseFlangePose() {
	json json_result, params;
	params["unit_type"] = 0;
	json_result = sendCmd("get_base_flange_pose", params, 1);
	std::string jsonstr = json_result["result"];
	std::vector<float> resultF = stringToVector(jsonstr);

	return resultF;
}

json RobotConntroller::inverseKinematic(std::string jointInformation, int unit_type) {
	json json_result, params;
	std::vector<float> output_vec = RobotConntroller::stringToVector(jointInformation);

	float pose_list[6];
	for (int i = 0; i < 6; i++) {
		pose_list[i] = output_vec[i];
	}
	params["targetPose"] = pose_list, params["unit_type"] = unit_type;
	json_result = sendCmd("inverseKinematic", params, 1);
	return json_result;
}

json RobotConntroller::positiveKinematic(std::string poseInformation) {
	json json_result, params;
	std::vector<float> output_vec = RobotConntroller::stringToVector(poseInformation);

	float pos_list[6];
	for (int i = 0; i < 6; i++) {
		pos_list[i] = output_vec[i];
	}
	params["targetPos"] = pos_list, params["unit_type"] = 0;
	json_result = sendCmd("positiveKinematic", params, 1);
	return json_result;
}