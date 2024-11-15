#include "qUSBHidReceiveThreadObject.h"

qUSBHidReceiveThreadObject::qUSBHidReceiveThreadObject() {
}
qUSBHidReceiveThreadObject::~qUSBHidReceiveThreadObject() {}

void qUSBHidReceiveThreadObject::OnReceiveObjectInnerTick() {
	GetHidData();
}

void qUSBHidReceiveThreadObject::GetHidData() {
	if (handle == nullptr) {
		if (map_info["connect_status"] != "-2") {
			map_info["connect_status"] = "-1";
		}
		return;
	}
	map_info["connect_status"] = "1";
	if (status == 0)
	{
		GetSoftwareStatus();
	}
	else if (status == 1)
	{
		GetHeartBeat();
	}
	else {
	}
}

void qUSBHidReceiveThreadObject::GetSoftwareStatus() {
	unsigned char* packet = new unsigned char[65];
	for (int i = 0; i < 65; i++) {
		packet[i] = 0x00;
	}
	packet[0] = 0x00;
	packet[1] = 0xAA;
	packet[2] = 0x02;
	packet[3] = 0x02;
	packet[4] = 0x00;
	packet[5] = 0x01;
	packet[64] = 0xBB;
	add_queued_cmd("software_status", packet, 65, read_timeout, false);
	loop_write_and_read(handle);
}

void qUSBHidReceiveThreadObject::GetHeartBeat() {
	unsigned char* packet = new unsigned char[65];
	for (int i = 0; i < 65; i++) {
		packet[i] = 0x00;
	}
	packet[0] = 0x00;  // ֡ͷ
	// ��������ľ�������
	packet[1] = 0xAA;  // ֡ͷ
	packet[2] = 0x02;
	packet[3] = 0x01;
	packet[4] = 0x00;  // ���ݰ���Ÿ��ֽ�
	packet[5] = 0x01;  // ���ݰ���ŵ��ֽ�
	// packet[5] �� packet[62] �����ݰ���δָ����Ĭ��Ϊ0x00
	packet[64] = 0xBB; // ֡β
	add_queued_cmd("heart_beat", packet, 65, read_timeout, false);
	loop_write_and_read(handle);
}

void qUSBHidReceiveThreadObject::add_queued_cmd(QString key, unsigned char* data, int gap, int timeout, bool showlog) {
	packagelist.append(new PackageData(key, data, gap, timeout, showlog));
}

void qUSBHidReceiveThreadObject::analyse_result(PackageData* pd, QString  res) {
	if (pd->key == "software_status" && pd->data[5] == 1) {
		status = 1;
	}
	if (pd->key == "heart_beat" ||
		pd->key == "connect_status" ||
		pd->key == "ReadSoftwareInfo" ||
		pd->key == "software_status") {
		map_info[pd->key.toStdString()] = res.toStdString();
	}
	if (pd->key == "heart_beat") {
		if (pd->data[6] == 0x72 && pd->data[7] == 0x72 && pd->data[9] == 0x72) {
			status = 0;
		}
	}
}

void HID_API_EXPORT HID_API_CALL qUSBHidReceiveThreadObject::loop_write_and_read(hid_device* dev) {
	while (packagelist.length() > 0) {
		PackageData* pd = packagelist[0];
		packagelist.pop_front();
		if (pd->key == "heart_beat" ||
			pd->key == "connect_status" ||
			pd->key == "ReadSoftwareInfo" ||
			pd->key == "WriteSoftwareInfo" ||
			pd->key == "2" ||
			pd->key == "software_status") 
		{
			read_empty(dev);
			QString res = write_and_read(dev, pd->data, pd->length, pd->timeout, pd->show_log, pd->gap);
			analyse_result(pd, res);
		}
		else {
			write_to_usb(dev, pd->data, pd->length, pd->show_log);
		}
		QThread::msleep(20);

		delete pd->data;
		delete pd;
	}
}

QString HID_API_EXPORT HID_API_CALL qUSBHidReceiveThreadObject::write_and_read(hid_device* dev, unsigned char* data, size_t length, int milliseconds, bool show_log, int gap) {
	write_to_usb(dev, data, length, show_log);
	QThread::msleep(gap);
	for (int i = 0; i < length; i++) {
		data[i] = 0;
	}
	QString res = read_from_usb(dev, data, length, milliseconds, show_log);
	return res;
}

int  HID_API_EXPORT HID_API_CALL qUSBHidReceiveThreadObject::write_to_usb(hid_device* dev, const unsigned char* data, size_t length, bool show_log) {
	QStringList stringList;
	for (int i = 0; i < length; ++i) {
		// ��ÿ��Ԫ��ת��Ϊ QString ����ӵ� QStringList
		QString hexStr = QString("0x%1").arg(QString::number(data[i], 16).toUpper(), 2, QChar('0'));
		stringList.append(hexStr);
	}

	if (show_log)
	{
		qDebug() << "Send To USB:" << stringList.join(" ");;
	}
	if (out)
		(*out) << "Send To USB: " << stringList.join(" ") << Qt::endl;;
	int res = hid_write(dev, data, length);
	return res;
}

void HID_API_EXPORT HID_API_CALL qUSBHidReceiveThreadObject::read_empty(hid_device* dev) {
	unsigned char packet[65];
	hid_read_timeout(dev, packet, 65, 100);
}

QString HID_API_EXPORT HID_API_CALL qUSBHidReceiveThreadObject::read_from_usb(hid_device* dev, unsigned char* data, size_t length, int milliseconds, bool show_log) {
	int result = hid_read_timeout(dev, data, length, milliseconds);
	if (result == -1) {
		return "-1";
	}
	else if (data[0] == 0 && data[1] == 0 && data[2] == 0) {
		return "-2";
	}
	else {
		QStringList stringList;
		for (int i = 0; i < length; ++i) {
			QString hexStr = QString("0x%1").arg(QString::number(data[i], 16).toUpper(), 2, QChar('0'));
			// ��ÿ��Ԫ��ת��Ϊ QString ����ӵ� QStringList
			stringList.append(hexStr);
		}
		// ʹ�ÿո��ַ����б���������
		QString resultString = stringList.join(" ");
		if (show_log)
		{
			qDebug() << "Get From USB:" << resultString;
		}
		if (out)
			(*out) << "Get From USB: " << resultString << Qt::endl;;
		return resultString;
	}
}