#include "qUSBHidControllThreadObject.h"
#include "qUSBHidReceiveThreadObject.h"

void qUSBHidControllThreadObject::send_thread_cmd(QString cmd) {
	qRegisterMetaType<unsigned char*>("unsigned char*");
	QStringList list1 = cmd.split(", ");
	if (list1.length() < 2) {
		return;
	}
	if (list1[0] != mainKey) {
		return;
	}
	
	if (list1[1] == "Send") {
		if (list1.length() < 5) {
			return;
		}
		if (obj->handle == nullptr) {
			return;
		}
		int gap = list1[2].toInt();
		if (gap > 3000) {
			gap = 3000;
		}
		if (gap < 5) {
			gap = 5;
		}

		unsigned char* data_to_send = get_64bit_cmd(list1[3], list1);
		data_to_send[0] = 0x00;
		obj->add_queued_cmd(list1[3], data_to_send, gap, 10, true);
		obj->loop_write_and_read(obj->handle);
		return;
	}
	else if (list1[1] == "OpenAndShowLog") {
		if ((list1.length()) == 3)
		{
			obj->logfile = new QFile(list1[2]);
			qDebug() << "Create USB Log File" << list1[2];
			if (obj->logfile->exists()) {
				obj->logfile->remove();
			}
			if (obj->logfile->open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text)) {
				obj->out = new QTextStream(obj->logfile);
				return;
			}
			return;
		}
	}
	else if (list1[1] == "SetGapMax") {
		if (list1.length() == 3)
			obj->gap_max = list1[2].toInt();
		return;
	}
	else if (list1[1] == "EraseKey") {
		if (list1.length() == 3)
			obj->map_info.erase(list1[2].toStdString());
		return;
	}
	else if (list1[1] == "Init") {
		if (list1.length() != 4)
			return;
		if (hid_init() != 0) {
			obj->map_info["connect_status"] = "-2";
			//qDebug() << "the harware is lost1";
			return;
		}

		unsigned short vendor_id = list1[2].toUShort();
		unsigned short product_id = list1[3].toUShort();
		obj->devs = hid_enumerate(vendor_id, product_id);
		if (obj->devs) {
			obj->handle = hid_open(obj->devs->vendor_id, obj->devs->product_id, nullptr);
			obj->map_info["connect_status"] = "1";
			obj->status = -1;
			obj->map_info["software_status"] = "-1";
			//qDebug() << "the harware is lost2";
		}
		else {
			obj->map_info["connect_status"] = "-2";
			//qDebug() << "the harware is lost3";
		}
		return;
	}
	else if (list1[1] == "CleanUSBCache") {
		/*for (int i = 0; i < 5; i++) {
			unsigned char data[65];
			obj->read_from_usb(obj->handle, data, 65,100, true);
		}*/
	}
	else if (list1[1] == "Exit") {
		hid_free_enumeration(obj->devs);
		hid_exit();
		return;
	}	
}

unsigned char* qUSBHidControllThreadObject::get_64bit_cmd(QString key, QStringList valuelist) {
	unsigned char* packet = new unsigned char[65];
	for (int i = 0; i < 65; i++) {
		packet[i] = 0x00;
	}
	// ��������ľ�������
	packet[0] = 0xAA;
	packet[1] = 0xAA;  // ֡ͷ
	packet[2] = 0x02;
	packet[3] = 0x01;
	packet[4] = 0x00;  // ���ݰ���Ÿ��ֽ�
	packet[5] = 0x01;  // ���ݰ���ŵ��ֽ�
	// packet[5] �� packet[62] �����ݰ���δָ����Ĭ��Ϊ0x00
	packet[64] = 0xBB; // ֡β
	qDebug() << "Read USB key:" << key;
	if (key == "ReadSoftwareInfo") {
		packet[2] = 0x02;
		packet[3] = valuelist[4].toInt();
	}
	else if (key == "WriteSoftwareInfo") {
		packet[2] = 0x01;
		packet[3] = valuelist[4].toInt();
		QStringList list1 = valuelist[5].split("#");
		for (int i = 0; i < list1.size(); i++) {
			packet[i + 6] = list1[i].toInt();
		}
	}

	else if (key == "SwitchSoftwareStatus") {
		obj->map_info.erase("software_status");
		obj->map_info.erase("heart_beat");
		obj->map_info.erase("connect_status");
		obj->status = -1;
		obj->map_info["software_status"] = "-1";
	}
	else if (key == "ResetMCU") {
		packet[2] = 0x03;
		packet[3] = 0x01;
	}
	else if (key == "ChangeSoftwareStatus") {
		//qDebug() << "ChangeSoftwareStatus test  work state" << key;
		obj->status = 0;
		packet[2] = 0x03;
		packet[3] = 0x02;
		packet[6] = valuelist[4].toInt();
		//QStringList stringList;
		//for (int i = 0; i < 65; ++i) {
		//	// ��ÿ��Ԫ��ת��Ϊ QString ����ӵ� QStringList
		//	QString hexStr = QString("0x%1").arg(QString::number(packet[i], 16).toUpper(), 2, QChar('0'));
		//	stringList.append(hexStr);
		//}
		//qDebug() << "end ChangeSoftwareStatus test  work state " << stringList.join(" ");
	}
	else {
		set_special_cmd(key, packet, valuelist);
	}
	return packet;
}

void qUSBHidControllThreadObject::send_64bit_cmd(QString key, QStringList value, int gap) {
	//if (obj->handle == nullptr) {
	//    return;
	//}
	//unsigned char* data_to_send = get_64bit_cmd(key, value); // �����������
	//QString resultString = obj->write_and_read(obj->handle, data_to_send,65,100, true,gap);
	//obj->map_info[key.toStdString()] = resultString.toStdString();
	//delete[] data_to_send;
}