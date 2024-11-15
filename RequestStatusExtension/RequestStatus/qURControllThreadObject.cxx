#include "qURControllThreadObject.h"
#include "qURReceiveThreadObject.h"
#include <QTimer>

QString qURControllThreadObject::send_synchronize_cmd(QString cmd) {
	std::cout << "send_synchronize : " << cmd.toStdString() << "\n";
	QString res;
	QStringList list1 = cmd.split(", ");
	if (list1[1] == "GetInverseKinematicsHasSolution") {
		std::cout << list1.length() << "\n";
		QString posstr = list1[2];
		std::cout << "posstr : " << posstr.toStdString() << "\n";
		bool standard_units = list1[3] == "True" ? true : false;
		std::cout << "units : " << standard_units << "\n";
		return getInverseKinematicsHasSolution(posstr, standard_units);
	}
	if (list1[1] == "GetInverseKinematics") {
		QString posstr = list1[2];
		// std::cout << "posstr : " <<  posstr.toStdString() << "\n";
		bool standard_units = list1[3] == "True" ? true : false;
		// std::cout << "units : " << standard_units << "\n";
		return getInverseKinematics(posstr, standard_units);
	}
	if (list1[1] == "IsRobotSteady") {
		// std::cout << "Received steady cmd\n";
		return isRobotSteady();
	}
	if (list1[1] == "GetTCPPose")
		return getTCPPose();
	if (list1[1] == "SetInitialPose")
		return setInitialPose();
	if (list1[1] == "SetStepValue") {
		QString stepval = list1[2];
		return setStepValue(stepval);
	}
	if (list1[1] == "SetStepSdValue") {
		QString stepval = list1[2];
		return setStepSdValue(stepval);
	}
	if (list1[1] == "MoveToNextPose")
		return moveToNextPose();
	if (list1[1] == "MoveToPrevPose")
		return moveToPrevPose();
	if (list1[1] == "EnableRobotAfterEmergency") {
		return enableRobotAfterEmergency();
	}
	if (list1[1] == "EnableRobotAfterProtective") {
		return enableRobotAfterProtective();
	}
	if (list1[1] == "ModbusConfigOn") {
		QString margin = list1[2];
		return modbusConfigOn(margin);
	}
	if (list1[1] == "ModbusConfigOff") {
		return modbusConfigOff();
	}
	return res;
}

void qURControllThreadObject::send_thread_cmd(QString cmd) {
	std::cout << "cmd : " << cmd.toStdString() << "\n";
	try {
		QStringList list1 = cmd.split(", ");
		if (list1.length() < 2) {
			return;
		}
		if (list1[0] != "UR") {
			return;
		}
		if (list1[1] == "SetGapMax") {
			if (list1.length() == 3)
				obj->gap_max = list1[2].toInt();
			return;
		}
		if (list1[1] == "Connect") {
			connect(list1[2], list1[3]);
			return;
		}
		if (list1[1] == "DisConnect") {
			disconnect();
			return;
		}
		if (list1[1] == "Open") {
			open();
			return;
		}
		if (list1[1] == "MoveByTCP") {
			// std::cout << "move tcp command received\n";
			QStringList poslist;
			poslist << list1[2] << list1[3] << list1[4] << list1[5] << list1[6] << list1[7];
			QString posstr = poslist.join(", ");
			bool async = list1[8] == "True" ? true : false;
			qDebug() << posstr;
			std::cout << async << "\n";
			moveByTCP(posstr, async);
			return;
		}
		if (list1[1] == "MoveByJoint") {
			QStringList poslist;
			poslist << list1[2] << list1[3] << list1[4] << list1[5] << list1[6] << list1[7];
			QString posstr = poslist.join(", ");
			// QString joint_pos = list1[2];
			bool async = list1[8] == "True" ? true : false;
			moveByJoint(posstr, async);
			return;
		}
		if (list1[1] == "RemoveKey") {
			auto key = list1[2].toStdString();
			obj->map_info.erase(key);
			return;
		}
		if (list1[1] == "RemoveKey") {
			auto key = list1[2].toStdString();
			obj->map_info.erase(key);
			return;
		}
		if (list1[1] == "Stop") {
			return;
		}
		if (list1[1] == "Rotate") {
			return;
		}
		if (list1[1] == "SetTool") {
			return;
		}
		if (list1[1] == "ClearAlarm") {
			return;
		}
		if (list1[1] == "SetCollapseSensitivity") {
			return;
		}
		if (list1[1] == "SetSpeed") {
			return;
		}
		if (list1[1] == "StartMoveUp") {
			std::string dir = "up";
			keepRunning = true;
			std::cout << "Caling move up\n";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartMoveDown") {
			std::string dir = "down";
			keepRunning = true;
			std::cout << "Caling move down\n";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartMoveRight") {
			std::string dir = "right";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartMoveLeft") {
			std::string dir = "left";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartMoveBack") {
			std::string dir = "back";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartMoveFront") {
			std::string dir = "front";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StopMove") {
			keepRunning = false;
			std::cout << "Caling stop\n";
			stopMovePosition();
			return;
		}
		if (list1[1] == "StartRotateXPositive") {
			std::string dir = "rotateXPositive";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartRotateXNegative") {
			std::string dir = "rotateXNegative";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartRotateYPositive") {
			std::string dir = "rotateYPositive";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartRotateYNegative") {
			std::string dir = "rotateYNegative";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartRotateZPositive") {
			std::string dir = "rotateZPositive";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "StartRotateZNegative") {
			std::string dir = "rotateZNegative";
			startMovePosition(dir);
			return;
		}
		if (list1[1] == "RotateDegree") {
			QString dir = list1[2];
			rotate_180(dir);
			return;
		}
		if (list1[1] == "ChangeView") {
			QString dir = list1[2];
			changeView(dir);
			return;
		}
		if (list1[1] == "StartMoveJoint") {
			std::cout << "Caling start move joint\n";
			std::string joint = list1[2].toStdString();
			std::string dir = list1[3].toStdString();
			startMoveJoint(joint, dir);
			return;
		}
		if (list1[1] == "ToolModbusRead") {
			std::cout << "Caling tool modbus read\n";
			// int val = control_handler->getToolModbusRead();
			std::string spt = list1[2].toStdString();
			std::cout << "spt : \n";
			std::cout << spt << "\n";
			bool val = false;
			val = control_handler->sendCustomScript(spt);
			std::cout << "val is " << val << "\n";
			return;
		}
		if (list1[1] == "StartFreedriveMode") {
			if (!obj->IS_FREEDRIVE_STATE)
			{
				std::cout << "starting fd mode\n";
				bool res = startFreedriveMode();
				if (res == false)
				{
					std::cout << "[Error] : fd mode cannot be started\n";
					return;
				}
				obj->IS_FREEDRIVE_STATE = true;
			}
			else
			{
				std::cout << "already started fd mode\n";
			}
			return;
		}
		if (list1[1] == "EndFreedriveMode") {
			if (obj->IS_FREEDRIVE_STATE)
			{
				std::cout << "ending fd mode\n";
				bool res = endFreedriveMode();
				if (res == false)
				{
					std::cout << "[Error] : fd mode cannot be ended\n";
					return;
				}
				obj->IS_FREEDRIVE_STATE = false;
			}
			else
			{
				std::cout << "already ended fd mode\n";
			}
			return;
		}
		if (list1[1] == "ReuploadScript") {
			reuploadScript();
			return;
		}
	}
	catch (const std::exception& e) {
		// �����쳣
		qDebug() << "catch exception2" << e.what();
	}
}

void qURControllThreadObject::set_speed(int value) {
}
void qURControllThreadObject::set_collapse_sensitivity(int value) {
}

void qURControllThreadObject::clear_alarm() {
}

// �Ƶ�ǰĩ��TCP����ת�����Բο�tcp�������base����
std::string qURControllThreadObject::tcpRotate_compute(float p[], int toolorbase, float rx, float ry, float rz) {
	return "";
}

void qURControllThreadObject::movebyLine(std::string targetpos, double speed) {
}

void qURControllThreadObject::set_tool_number(int tool_num) {
}

void qURControllThreadObject::rotate(std::string tcppos, int toolorbase, float rx, float ry, float rz) {
}

std::vector<double> qURControllThreadObject::stringToVector(std::string s)
{
	std::vector<double> res;
	std::string delimiter = ",";

	size_t pos = 0;
	while ((pos = s.find(delimiter)) != std::string::npos)
	{
		std::string temp = s.substr(0, pos);
		double temp_d = std::stod(temp.c_str());
		res.push_back(temp_d);
		s.erase(0, pos + delimiter.length());
	}
	res.push_back(std::stod(s.c_str()));
	return res;
}

std::string qURControllThreadObject::vectorToString(std::vector<double>& v)
{
	std::string res;
	size_t sz = v.size();
	if (sz < 1)
		return "";
	for (size_t i = 0; i < sz; i++)
	{
		res += std::to_string(v[i]);
		res += ", ";
	}
	res.pop_back();
	res.pop_back();
	return res;
}

std::vector<double> qURControllThreadObject::getTargetInBaseFrame()
{
	std::vector<double> target_in_tool_frame(6, 0);
	std::cout << "Moving with step value : " << step_value_ << "\n";
	// target_in_tool_frame[0] = step_value_ * step_counter_;
	// std::vector<double> target_in_base_frame = control_handler->poseTrans(treatment_initial_pose_,target_in_tool_frame);
	target_in_tool_frame[0] = step_value_;
	std::vector<double> prev_pose = stack_poses.top();
	std::vector<double> target_in_base_frame = control_handler->poseTrans(prev_pose, target_in_tool_frame);
	std::cout << "before moveToNext: " << prev_pose[0] << ", " << prev_pose[1] << ", " << prev_pose[2] << ", " << prev_pose[3] << ", " << prev_pose[4] << ", " << prev_pose[5] << "\n";

	return target_in_base_frame;
}

void qURControllThreadObject::moveByTCP(const QString& tcp_pose, const bool& async) {
	if (control_handler) {
		std::vector<double> pose_ = stringToVector(tcp_pose.toStdString());
		std::cout << "move (by tcp) to:\n";
		for (int i = 0; i < pose_.size(); i++)
			std::cout << pose_[i] << " ";
		std::cout << "\n";
		control_handler->moveJ_IK(pose_, 0.25, 0.5, async);
	}
}

void qURControllThreadObject::moveByJoint(const QString& joints, const bool& async) {
	if (control_handler) {
		std::vector<double> joints_ = stringToVector(joints.toStdString());
		std::cout << "move (by joint) to :\n";
		for (int i = 0; i < joints_.size(); i++)
			std::cout << joints_[i] << " ";
		std::cout << "\n";
		control_handler->moveJ(joints_, 0.15, 0.25, async);
	}
}

void qURControllThreadObject::moveL(const QString& tcp_pose, const bool& async) {
	if (control_handler) {
		std::vector<double> pose_ = stringToVector(tcp_pose.toStdString());
		std::cout << "move (by L) to :\n";
		for (int i = 0; i < pose_.size(); i++)
			std::cout << pose_[i] << std::endl;
		std::cout << "\n";
		control_handler->moveL(pose_, 0.15, 0.5, async);
	}
}

void qURControllThreadObject::connect(QString ipaddress, QString port) {
	qDebug() << "connect with ip:" << ipaddress;
	obj->handler = new ur_rtde::RTDEReceiveInterface(ipaddress.toStdString(), -1.0, {}, false,
		false, RT_PRIORITY_UNDEFINED);
	control_handler = new ur_rtde::RTDEControlInterface(ipaddress.toStdString(), -1.0);
	io_handler = new ur_rtde::RTDEIOInterface(ipaddress.toStdString());
	//bool rnull = obj->handler == NULL;
	//qDebug() << "receive handler : " << (obj->handler == NULL);
	//qDebug() << "control_handler : " << (control_handler == NULL);
	//qDebug() << "io_handler : " << (io_handler == NULL);
}

void qURControllThreadObject::disconnect() {
	qDebug() << "dis connect";
	if (obj->handler) {
		obj->handler->disconnect();
	}
	if (control_handler) {
		control_handler->disconnect();
	}
}

void qURControllThreadObject::stop() {
}

void qURControllThreadObject::open() {
	if (control_handler) {
		control_handler->startContactDetection();
	}
}

QString qURControllThreadObject::getInverseKinematicsHasSolution(const QString& pose, const bool& standard_units)
{
	QString ret = "0";
	bool res = false;
	// std::cout << "11111111111111111111111" << std::endl;
	if (control_handler)
	{
		// std::cout << "11111111111111111111112" << std::endl;
		std::vector<double> pose_ = stringToVector(pose.toStdString());
		// std::cout << "11111111111111111111113" << std::endl;
		if (!standard_units) // convert from mm, deg to m, rad
		{
			for (int i = 0; i < 3; i++)
			{
				pose_[i] /= 1000.0;
				pose_[i + 3] = degToRad(pose_[i + 3]);
			}
		}
		// std::cout << "11111111111111111111114" << std::endl;
		res = control_handler->getInverseKinematicsHasSolution(pose_);
		// std::cout << "11111111111111111111115" << std::endl;
	}
	if (res)
		ret = "1";
	// obj->map_info["getInverseKinematicsHasSolution"] = "1"; // set the value in C++ map
  // else
  //     obj->map_info["getInverseKinematicsHasSolution"] = "0";
	std::cout << "Has solution res is : " << res << "\n";
	return ret;
}

QString qURControllThreadObject::getInverseKinematics(const QString& pose, const bool& standard_units)
{
	QString ret;
	std::vector<double> res;
	if (control_handler)
	{
		std::vector<double> pose_ = stringToVector(pose.toStdString());
		if (!standard_units) // convert from mm, deg to m, rad
		{
			for (int i = 0; i < 3; i++)
			{
				pose_[i] /= 1000.0;
				pose_[i + 3] = degToRad(pose_[i + 3]);
			}
		}
		res = control_handler->getInverseKinematics(pose_);
	}
	std::string tmp = vectorToString(res);
	// obj->map_info["getInverseKinematics"] = res; // set the value in C++ map
	std::cout << " IK res is : " << tmp << "\n";
	ret = QString::fromStdString(tmp);
	return ret;
}

QString qURControllThreadObject::isRobotSteady()
{
	QString ret = "False";
	bool res = false;
	if (control_handler)
	{
		res = control_handler->isSteady();
	}
	if (res)
		ret = "True";
	// std::cout << "Is steady res is : " << res << "\n";
	return ret;
}

QString qURControllThreadObject::getTCPPose()
{
	QString ret;
	if (control_handler)
	{
		std::vector<double> pose = obj->handler->getActualTCPPose();
		std::string pose_str = vectorToString(pose);
		ret = QString::fromStdString(pose_str);
	}
	return ret;
}

QString qURControllThreadObject::setInitialPose()
{
	QString ret = "False";
	if (control_handler)
	{
		treatment_initial_pose_ = obj->handler->getActualTCPPose();

		while (!stack_poses.empty())
			stack_poses.pop();
		stack_poses.push(treatment_initial_pose_);

		step_counter_ = 0;

		std::cout << "Setting initial pose to : \n";
		for (auto i : treatment_initial_pose_)
			std::cout << i << " ";
		std::cout << "\n";
		ret = "True";
		return ret;
	}
	return ret;
}

QString qURControllThreadObject::setStepValue(QString step_value)
{
	QString ret = "False";
	bool ok;
	if (control_handler)
	{
		double value = step_value.toDouble(&ok);

		if (!ok) {
			std::cout << "Step value conversion failed:\n";
			return ret;
		}

		step_value_ = value / 1000; // mm to m
		std::cout << "Setting step value to :" << step_value_ << "\n";
		ret = "True";
		return ret;
	}
	return ret;
}

QString qURControllThreadObject::setStepSdValue(QString step_value)
{
	QString ret = "False";
	bool ok;
	// if (control_handler)
	// {
	//   double value = step_value.toDouble(&ok);

	//   if (!ok) {
	//     std::cout << "Step value conversion failed:\n";
	//     return ret;
	//   }

	//   sd_value_ = value;
	//   std::cout << "Setting sd value to :" << sd_value_ << "\n";
	//   ret = "True";
	//   return ret;
	// }

	// use this to adjust speed scaling
	if (io_handler)
	{
		double value = step_value.toDouble(&ok);

		if (!ok) {
			std::cout << "Step value conversion failed:\n";
			return ret;
		}

		io_handler->setSpeedSlider(value);
		std::cout << "Setting speed slider value to :" << value << "\n";
		ret = "True";
		return ret;
	}
	return ret;
}

QString qURControllThreadObject::moveToNextPose()
{
	//either the pose is THE current pose or pose after additional movement,
	//it should be first move into current pose, then move to next pose
	QString ret = "False";
	std::cout << "----cpp entry----\n";
	if (control_handler && !treatment_initial_pose_.empty())
	{
		step_counter_++;
		std::cout << "step number : " << step_counter_ << "\n";
		std::vector<double> target_in_base_frame = getTargetInBaseFrame();

		stack_poses.push(target_in_base_frame);

		std::string pose_str = vectorToString(target_in_base_frame);
		QString pose_qstr = QString::fromStdString(pose_str);
		moveL(pose_qstr, false);
		std::cout << "after moveToNextPose " << pose_qstr.toStdString().c_str() << "\n";
		std::cout << "stack_poses size after move_next " << stack_poses.size() << "\n";
		ret = "True";
		return ret;
	}
	std::cout << "----cpp exit----\n";
	return ret;
}

QString qURControllThreadObject::moveToPrevPose()
{
	QString ret = "False";
	std::cout << "----cpp entry----\n";
	if (control_handler && !treatment_initial_pose_.empty())
	{
		if (stack_poses.size() > 1)
		{
			if (step_counter_ > 0)
				step_counter_--;
			std::cout << "step number : " << step_counter_ << "\n";
			stack_poses.pop();
			std::cout << "stack_poses size after move_prev" << stack_poses.size() << "\n";
		}
		std::vector<double> target_in_base_frame = stack_poses.top();
		std::string pose_str = vectorToString(target_in_base_frame);
		QString pose_qstr = QString::fromStdString(pose_str);
		moveL(pose_qstr, false);
		ret = "True";
		std::cout << "after moveToPrevPose " << pose_qstr.toStdString().c_str() << "\n";
		std::cout << "----cpp exit----\n";
		return ret;
	}
	std::cout << "----cpp exit----\n";
	return ret;
}

void qURControllThreadObject::rotate_180(QString dir)
{
	std::cout << "----cpp entry change view----\n";
	if (control_handler)
	{
		std::vector<double> cur_joint_pos = obj->handler->getActualQ();
		int direction = 0;
		// if (dir == "1")
		//   direction = 1;
		// else if (dir == "-1")
		//   direction = -1;
		// else
		// {
		//   std::cout << "Invalid direction provided\n";
		//   return;
		// }
		if (dir == "1")
		{
			direction = 1;
		}
		else
		{
			direction = -1;
		}
		cur_joint_pos[5] = cur_joint_pos[5] + direction * PI;
		std::string joint_str = vectorToString(cur_joint_pos);
		QString joint_qstr = QString::fromStdString(joint_str);
		double ss_old = obj->handler->getSpeedScaling();
		double ss_new = 1.0;
		if (io_handler)
			io_handler->setSpeedSlider(ss_new);
		moveByJoint(joint_qstr, true);
		if (io_handler)
			io_handler->setSpeedSlider(ss_old);
	}
	std::cout << "----cpp exit----\n";
}

void qURControllThreadObject::changeView(QString dir)
{
	std::cout << "----cpp entry change view----\n";
	if (control_handler)
	{
		std::vector<double> cur_joint_pos = obj->handler->getActualQ();
		int direction = 0;
		// if (dir == "1")
		//   direction = 1;
		// else if (dir == "-1")
		//   direction = -1;
		// else
		// {
		//   std::cout << "Invalid direction provided\n";
		//   return;
		// }
		if (change_view_positive)
		{
			direction = 1;
			change_view_positive = false;
			std::cout << "pos dir\n";
		}
		else
		{
			direction = -1;
			change_view_positive = true;
			std::cout << "neg dir\n";
		}
		cur_joint_pos[5] = cur_joint_pos[5] + direction * PI / 2;
		std::string joint_str = vectorToString(cur_joint_pos);
		QString joint_qstr = QString::fromStdString(joint_str);
		double ss_old = obj->handler->getSpeedScaling();
		double ss_new = 1.0;
		if (io_handler)
			io_handler->setSpeedSlider(ss_new);
		moveByJoint(joint_qstr, true);
		if (io_handler)
			io_handler->setSpeedSlider(ss_old);
	}
	std::cout << "----cpp exit----\n";
}

void qURControllThreadObject::handlerTranslationalRealtimeMotion(std::vector<double>& tool_wrt_base, std::vector<double>& xd_t, std::vector<double>& t_speed_wrt_base)
{
	std::vector<double> t_speed_wrt_base_raw = control_handler->poseTrans(tool_wrt_base, xd_t);
	for (int i = 0; i < 3; i++)
		t_speed_wrt_base[i] = t_speed_wrt_base_raw[i] - tool_wrt_base[i];
}

void qURControllThreadObject::handlerRotationalRealtimeMotion(std::vector<double>& tool_wrt_base, std::vector<double>& xd_r, std::vector<double>& r_speed_wrt_base)
{
	std::vector<double> r_speed_wrt_base_raw = control_handler->poseTrans(tool_wrt_base, xd_r);
	for (int i = 0; i < 3; i++)
		r_speed_wrt_base[i] = r_speed_wrt_base_raw[i] - tool_wrt_base[i];
}

void qURControllThreadObject::handlerCartesianRealtimeMotion(std::vector<double>& xd_t, std::vector<double>& xd_r, std::vector<double>& speed_wrt_base)
{
	std::vector<double> tool_wrt_base = obj->handler->getActualTCPPose();
	std::vector<double> t_speed_wrt_base(6, 0);
	std::vector<double> r_speed_wrt_base(6, 0);

	handlerTranslationalRealtimeMotion(tool_wrt_base, xd_t, t_speed_wrt_base);
	handlerRotationalRealtimeMotion(tool_wrt_base, xd_r, r_speed_wrt_base);

	for (int i = 0; i < 3; i++)
		r_speed_wrt_base[i] *= sd_value_;
	speed_wrt_base = { t_speed_wrt_base[0], t_speed_wrt_base[1], t_speed_wrt_base[2], r_speed_wrt_base[0], r_speed_wrt_base[1], r_speed_wrt_base[2] };
	double ss = obj->handler->getSpeedScaling();
	std::cout << "ss : " << ss << "\n";
	std::cout << "speed_wrt_base";
	for (auto i : speed_wrt_base)
		std::cout << i << "\t";
	std::cout << "\n";
}

void qURControllThreadObject::executeCartesianRealtimeMotion(std::vector<double>& xd_t, std::vector<double>& xd_r, double acc)
{
	std::cout << "before executeCartesianRealtimeMotion " << "\n";
	std::vector<double> speed_wrt_base(6, 0);
	handlerCartesianRealtimeMotion(xd_t, xd_r, speed_wrt_base);
	control_handler->speedL(speed_wrt_base, acc, 0.2);
	std::cout << "after executeCartesianRealtimeMotion " << "\n";
}

void qURControllThreadObject::startMovePosition(std::string dir)
{
	std::cout << "Move called ; " << std::this_thread::get_id() << "\n";
	if (control_handler)
	{
		std::chrono::time_point t_start = control_handler->initPeriod();
		double acc = 0.5;
		std::vector<double> xd_t(6, 0.0), xd_r(6, 0.0);
		if (dir == "up")
			xd_t[2] = -0.1;
		else if (dir == "down")
			xd_t[2] = 0.1;
		else if (dir == "right")
			xd_t[0] = -0.1;
		else if (dir == "left")
			xd_t[0] = 0.1;
		else if (dir == "back")
			xd_t[1] = 0.1;
		else if (dir == "front")
			xd_t[1] = -0.1;
		else if (dir == "rotateXPositive")
			xd_r[0] = 0.1;
		else if (dir == "rotateXNegative")
			xd_r[0] = -0.1;
		else if (dir == "rotateYPositive")
			xd_r[1] = 0.1;
		else if (dir == "rotateYNegative")
			xd_r[1] = -0.1;
		else if (dir == "rotateZPositive")
			xd_r[2] = 0.1;
		else if (dir == "rotateZNegative")
			xd_r[2] = -0.1;

		executeCartesianRealtimeMotion(xd_t, xd_r, acc);
	}
}

void qURControllThreadObject::stopMovePosition()
{
	std::cout << "Stop called ; " << std::this_thread::get_id() << "\n";
	if (control_handler)
	{
		control_handler->speedStop(2);
	}
	std::cout << "Stop returned\n";
}

void qURControllThreadObject::startMoveJoint(std::string joint, std::string  dir)
{
	double val = 0.2;
	double acc = 0.5;
	int jointNum = stoi(joint);

	if (jointNum > 6 || jointNum < 1)
	{
		std::cout << "Invalid joint number provided\n";
		return;
	}

	if (dir == "negative")
		val = -val;

	std::vector<double> qd(6, 0);
	qd[jointNum - 1] = val;
	std::cout << "qd : ";
	for (auto i : qd)
		std::cout << i << ",";
	std::cout << "\n";
	if (control_handler)
	{
		control_handler->speedJ(qd, acc, 0.4);
		std::cout << "Function returned\n";
	}
}

bool qURControllThreadObject::startFreedriveMode()
{
	bool res = false;
	if (control_handler) {
		res = control_handler->freedriveMode();
	}
	return res;
}

bool qURControllThreadObject::endFreedriveMode()
{
	bool res = true;
	if (control_handler) {
		res = control_handler->endFreedriveMode();
	}
	return res;
}

void qURControllThreadObject::reuploadScript()
{
	std::cout << "reuploadScript called [cpp]\n";
	if (control_handler)
	{
		control_handler->reuploadScript();
	}
	std::cout << "reuploadScript returned [cpp]\n";
}

QString qURControllThreadObject::enableRobotAfterEmergency()
{
	QString ret = "False";
	std::cout << "----cpp entry----\n";
	if (control_handler) {
		control_handler->closeSafetyPopup();
		control_handler->powerOn();
		control_handler->brakeRelease();
		ret = "True";
	}
	std::cout << "----cpp exit----\n";
	return ret;
}

QString qURControllThreadObject::enableRobotAfterProtective()
{
	QString ret = "False";
	std::cout << "unlockProtectiveStop called [cpp]\n";
	if (control_handler)
	{
		control_handler->unlockProtectiveStop();
		ret = "True";
	}
	std::cout << "unlockProtectiveStop returned [cpp]\n";
	return ret;
}

QString qURControllThreadObject::modbusConfigOn(QString margin)
{
	QString ret = "False";
	std::cout << "modbus config on called [cpp]\n";
	if (io_handler)
	{
		bool ok;
		double value = margin.toDouble(&ok);
		if (!ok) {
			std::cout << "margin conversion failed:\n";
			return ret;
		}
		bool reg_set = io_handler->setInputDoubleRegister(20, value);
		if (!reg_set) {
			std::cout << "double register setting failed\n";
			return ret;
		}
		bool to_set = io_handler->setToolDigitalOut(1, true);
		ret = to_set ? "True" : "False";
	}
	std::cout << "modbus config on returned [cpp]\n";
	return ret;
}

QString qURControllThreadObject::modbusConfigOff()
{
	QString ret = "False";
	std::cout << "modbus config off called [cpp]\n";
	if (io_handler)
	{
		bool to_set = io_handler->setToolDigitalOut(1, false);
		ret = to_set ? "True" : "False";
	}
	std::cout << "modbus config off returned [cpp]\n";
	return ret;
}