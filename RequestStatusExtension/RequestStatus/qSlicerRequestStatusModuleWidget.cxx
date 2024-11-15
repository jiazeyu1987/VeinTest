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

// Slicer includes
#include "qSlicerRequestStatusModuleWidget.h"
#include "ui_qSlicerRequestStatusModuleWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerRequestStatusModuleWidgetPrivate : public Ui_qSlicerRequestStatusModuleWidget
{
public:
	qSlicerRequestStatusModuleWidgetPrivate();
};

//-----------------------------------------------------------------------------
// qSlicerRequestStatusModuleWidgetPrivate methods

//-----------------------------------------------------------------------------
qSlicerRequestStatusModuleWidgetPrivate::qSlicerRequestStatusModuleWidgetPrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerRequestStatusModuleWidget methods

//-----------------------------------------------------------------------------
qSlicerRequestStatusModuleWidget::qSlicerRequestStatusModuleWidget(QWidget* _parent)
	: Superclass(_parent)
	, d_ptr(new qSlicerRequestStatusModuleWidgetPrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerRequestStatusModuleWidget::~qSlicerRequestStatusModuleWidget()
{
}

//-----------------------------------------------------------------------------
void qSlicerRequestStatusModuleWidget::setup()
{
	Q_D(qSlicerRequestStatusModuleWidget);
	d->setupUi(this);
	this->Superclass::setup();
	//qDebug() << "Setup Thread ID:" << QThread::currentThreadId();
	timer = new QTimer(this);
	timer->setInterval(10);

	// ����ʱ���� timeout() �ź����ӵ��ۺ���
	connect(timer, &QTimer::timeout, this, &qSlicerRequestStatusModuleWidget::on_main_thread_tick);

	// �����ʱ��
	timer->start();
}

void qSlicerRequestStatusModuleWidget::shutdown() {
	timer->stop();
}

int  qSlicerRequestStatusModuleWidget::bind_subthreads(QStringList namelist, bool to_bind) {
	qDebug() << "bind_subthreads " << namelist << "," << to_bind;
	for (int i = 0; i < namelist.size(); i++) {
		std::string name = namelist.at(i).toStdString();
		if (!map_ReceiveThread.contains(name)) {
			qDebug() << "bind_subthreads error code 1" << name.c_str();
			return -1;
		}
	}

	if (namelist.size() < 2) {
		qDebug() << "bind_subthreads error code 2" << namelist.size();
		return -2;
	}

	std::string main_key = namelist[0].toStdString();
	if (to_bind) {
		std::vector<std::string> sub_keys;
		for (int i = 1; i < namelist.size(); i++) {
			std::string sub_key = namelist.at(i).toStdString();
			sub_keys.push_back(sub_key);
			connect_subthread_to_main(sub_key, false);
			connect_subthread_to_subthread(main_key, sub_key, true);
		}
		bind_map[main_key] = sub_keys;
	}
	else {
		bind_map.remove(main_key);
		for (int i = 1; i < namelist.size(); i++) {
			std::string sub_key = namelist.at(i).toStdString();
			connect_subthread_to_main(sub_key, true);
			connect_subthread_to_subthread(main_key, sub_key, false);
		}
	}

	return 1;
}

void qSlicerRequestStatusModuleWidget::connect_subthread_to_subthread(std::string mainkey, std::string subkey, bool tobind) {
	qReceiveThreadBaseObject* main_thread = map_ReceiveObject[mainkey];
	qReceiveThreadBaseObject* sub_thread = map_ReceiveObject[subkey];
	auto ime_receive_object_cast = dynamic_cast<const qIMEReceiveThreadObject*>(sub_thread);
	if (tobind) {
		connect(main_thread, &qReceiveThreadBaseObject::tick_finished, sub_thread, &qReceiveThreadBaseObject::OnTimerReceiveObjectInnerTick, Qt::BlockingQueuedConnection);
	}
	else {
		disconnect(main_thread, &qReceiveThreadBaseObject::tick_finished, sub_thread, &qReceiveThreadBaseObject::OnTimerReceiveObjectInnerTick);
	}
}

void qSlicerRequestStatusModuleWidget::connect_subthread_to_main(std::string key, bool tobind) {
	auto ime_receive_object = map_ReceiveObject[key];
	if (tobind) {
		connect(this, &qSlicerRequestStatusModuleWidget::on_tick, ime_receive_object, &qReceiveThreadBaseObject::OnReceiveObjectTick);
	}
	else {
		disconnect(this, &qSlicerRequestStatusModuleWidget::on_tick, ime_receive_object, &qReceiveThreadBaseObject::OnReceiveObjectTick);
	}
}

void qSlicerRequestStatusModuleWidget::on_main_thread_tick() {
	mutex.lock();
	//for sub thread to update map_info
	emit on_tick();

	//concat map  into data
	std::string result = "";
	QMap<std::string, std::string>::iterator i;
	QStringList temp;
	for (auto it = map_ReceiveObject.begin(); it != map_ReceiveObject.end(); ++it) {
		std::string key = it.key();
		qReceiveThreadBaseObject* obj = it.value();
		if (obj) {
			auto result = obj->fetch_result();
			//qDebug() << key.c_str() << "::::" << result.c_str();
			if (result == "") {
				continue;
			}
			temp << QString::fromStdString(key + "*Y*, " + result);
		}
	}
	//auto res = get_info();
	QString pystring = temp.join("&H&, ");
	mutex.unlock();

	//send data to python
	emit on_tick_python(pystring);
}

void qSlicerRequestStatusModuleWidget::add_handler(QString qkey) {
	auto key = qkey.toStdString();
	map_vtkCallbackCommand[key] = vtkSmartPointer<vtkCallbackCommand>::New();
	map_vtkCallbackCommand[key]->SetClientData(reinterpret_cast<void*>(this));
	map_vtkCallbackCommand[key]->SetCallback(qSlicerRequestStatusModuleWidget::ReceiveTickCallback);
	map_ReceiveCallbackTag[key] = mrmlScene()->AddObserver(19870830, map_vtkCallbackCommand[key]);
	map_ReceiveThread[key] = new QThread();
	map_ControlThread[key] = new QThread();
	if (key == "IME")
	{
		auto ime_receive_object = new qIMEReceiveThreadObject();
		map_ReceiveObject[key] = ime_receive_object;
		auto ime_control_object = new qIMEControllThreadObject();
		map_ControlObject[key] = ime_control_object;
		ime_control_object->init(ime_receive_object);
	}
	else if (key == "NDI")
	{
		auto ime_receive_object = new qNDIReceiveThreadObject();
		map_ReceiveObject[key] = ime_receive_object;
		auto ime_control_object = new qNDIControllThreadObject();
		map_ControlObject[key] = ime_control_object;
		ime_control_object->init(ime_receive_object);
	}
	else if (key == "Elibot")
	{
		auto elibot_receive_object = new qElibotReceiveThreadObject();
		map_ReceiveObject[key] = elibot_receive_object;
		auto elibot_control_object = new qElibotControllThreadObject();
		map_ControlObject[key] = elibot_control_object;
		elibot_control_object->init(elibot_receive_object);
	}
	else if (key == "UR")
	{
		auto ur_receive_object = new qURReceiveThreadObject();
		map_ReceiveObject[key] = ur_receive_object;
		auto ur_control_object = new qURControllThreadObject();
		map_ControlObject[key] = ur_control_object;
		ur_control_object->init(ur_receive_object);
	}
	else if (key == "Register")
	{
		auto receive_object = new qRegisterReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qRegisterControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "Power")
	{
		auto receive_object = new qPowerReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qPowerControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "UltrasoundGenerator")
	{
		auto receive_object = new qUltrasoundGeneratorReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qUltrasoundGeneratorControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "Device")
	{
		auto receive_object = new qDeviceReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qDeviceControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "WaterControl")
	{
		auto receive_object = new qWaterColdingReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qWaterColdingControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "UltraImage")
	{
		auto receive_object = new qUltraImageReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
		auto control_object = new qUltraImageControllThreadObject();
		map_ControlObject[key] = control_object;
		control_object->init(receive_object);
	}
	else if (key == "System")
	{
		auto receive_object = new qSystemReceiveThreadObject();
		map_ReceiveObject[key] = receive_object;
	}
	else {
		std::cout << "Empty key " << key << std::endl;
	}
	connect_subthread_to_main(key, true);
	map_ReceiveObject[key]->moveToThread(map_ReceiveThread[key]);
	map_ReceiveThread[key]->start();

	if (key != "System")
	{
		connect(this, &qSlicerRequestStatusModuleWidget::send_signal_cmd, map_ControlObject[key], &qControlThreadBaseObject::send_thread_cmd, Qt::QueuedConnection);
		map_ControlObject[key]->moveToThread(map_ControlThread[key]);
		map_ControlThread[key]->start();
	}
}

unsigned char* qSlicerRequestStatusModuleWidget::get_ultra_image() {
	if (map_ReceiveThread.contains("UltraImage")) {
		qUltraImageReceiveThreadObject* receive = dynamic_cast<qUltraImageReceiveThreadObject*>(map_ReceiveThread["UltraImage"]);
		return receive->get_ultra_image();
	}
	return nullptr;
}

QString qSlicerRequestStatusModuleWidget::send_synchronize_cmd(QString cmd) {
	QStringList list1 = cmd.split(", ");
	if (list1.length() < 2) {
		return "error format";
	}
	auto key = list1[0];
	if (map_ControlObject.contains(key.toStdString())) {
		return map_ControlObject[key.toStdString()]->send_synchronize_cmd(cmd);
	}
	return "empty";
}

void qSlicerRequestStatusModuleWidget::send_cmd(QString cmd) {
	emit(send_signal_cmd(cmd));
}

std::string qSlicerRequestStatusModuleWidget::get_info() {
	std::string result = "";
	QMap<std::string, std::string>::iterator i;
	for (i = map_AllInfo.begin(); i != map_AllInfo.end(); ++i) {
		if (!result.empty()) {
			result = result + "&H&, "; // ��Ӽ�ֵ��֮��ķָ��
		}
		std::string   row = i.key() + "*Y*, " + i.value(); // ƴ�Ӽ���ֵ
		std::cout << "FFFFFFF:" << i.key() << "------->" << i.value() << std::endl;
		std::cout << "FFFFFFF2:" << row << std::endl;
		std::cout << "FFFFFFF3:" << result << std::endl;
		result = result + row;
		std::cout << "FFFFFFF4:" << result << std::endl;
	}
	return result;
}

void qSlicerRequestStatusModuleWidget::ReceiveTickCallback(vtkObject* caller, unsigned long vtkNotUsed(eid), void* clientData, void* vtkNotUsed(callData))
{
}

void qSlicerRequestStatusModuleWidget::start_thread(float gap) {
}

void qSlicerRequestStatusModuleWidget::pause_thread() {
}