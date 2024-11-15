/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

#ifndef __qSlicerRequestStatusModuleWidgetqURControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqURControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <stack>
#include <cmath>

#include <qControlThreadBaseObject.h>
#include "qURReceiveThreadObject.h"

#include <ur_rtde/rtde_receive_interface.h>
#include <ur_rtde/rtde_control_interface.h>
#include <ur_rtde/rtde_io_interface.h>

const double PI = 3.14159265358979323846;

class qURControllThreadObject : public qControlThreadBaseObject
{
	Q_OBJECT
public slots:
	void send_thread_cmd(QString cmd);
public:
	void init(qURReceiveThreadObject* in_obj) { obj = in_obj; };
	QString send_synchronize_cmd(QString cmd);
	static inline double degToRad(double deg)
	{
		double pi = 3.14159265358979323846;
		return deg * (pi / 180);
	}
public:
	qURReceiveThreadObject* obj = nullptr;
	ur_rtde::RTDEControlInterface* control_handler = nullptr;
	ur_rtde::RTDEIOInterface* io_handler = nullptr;
	std::atomic<bool> keepRunning{ true };
private:
	std::vector<double> stringToVector(std::string s);
	std::string vectorToString(std::vector<double>& v);
	void connect(QString ip, QString port);
	void disconnect();
	void open();
	void stop();
	void clear_alarm();
	void set_collapse_sensitivity(int value);
	void set_speed(int value);
	void moveByJoint(const QString& joints, const bool& async = false);
	void moveByTCP(const QString& tcp_pose, const bool& async = false);
	void moveL(const QString& tcp_pose, const bool& async = false);
	void rotate(std::string tcppos, int toolorbase, float rx, float ry, float rz);
	void set_tool_number(int tool_num);
	std::string tcpRotate_compute(float p[], int toolorbase, float rx, float ry, float rz);
	void movebyLine(std::string targetpos, double speed);
	QString getInverseKinematicsHasSolution(const QString& pose, const bool& standard_units = true);
	QString getInverseKinematics(const QString& pose, const bool& standard_units = true);
	QString isRobotSteady();
	QString getTCPPose();
	QString setInitialPose();
	QString setStepValue(QString);
	QString setStepSdValue(QString);
	QString moveToNextPose();
	QString moveToPrevPose();
	void handlerTranslationalRealtimeMotion(std::vector<double>& tool_wrt_base, std::vector<double>& xd_t, std::vector<double>& t_speed_wrt_base);
	void handlerRotationalRealtimeMotion(std::vector<double>& tool_wrt_base, std::vector<double>& xd_r, std::vector<double>& r_speed_wrt_base);
	void handlerCartesianRealtimeMotion(std::vector<double>& xd_t, std::vector<double>& xd_r, std::vector<double>& speed_wrt_base);
	void executeCartesianRealtimeMotion(std::vector<double>& xd_t, std::vector<double>& xd_r, double acc = 0.5);
	void changeView(QString); // pass "1" for positive direction and "-1" for negative direction
	void rotate_180(QString); // pass "1" for positive direction and "-1" for negative direction
	std::vector<double> getTargetInBaseFrame();
	void startMovePosition(std::string dir);
	void stopMovePosition();
	void startMoveJoint(std::string joint, std::string  dir);
	bool startFreedriveMode();
	bool endFreedriveMode();
	void reuploadScript();
	QString enableRobotAfterEmergency();
	QString enableRobotAfterProtective();
	QString modbusConfigOn(QString);
	QString modbusConfigOff();
	// treatment related variables
	std::vector<double> treatment_initial_pose_;
	int step_counter_ = 0;
	double step_value_ = 0.003; // in m
	double sd_value_ = 3;
	std::stack<std::vector<double>> stack_poses;
	bool change_view_positive = true;
};

#endif