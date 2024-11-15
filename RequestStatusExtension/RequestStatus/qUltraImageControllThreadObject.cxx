#include "qUltraImageControllThreadObject.h"
#include "qUltraImageReceiveThreadObject.h"
void qUltraImageControllThreadObject::send_thread_cmd(QString cmd) {
	try
	{
		// qDebug() << "qUltraImageControllThreadObject::send_thread_cmd(QString {" << cmd << "})";
		QStringList list1 = cmd.split(", ");
		if (list1.length() < 2) {
			return;
		}
		if (list1[0] != "UltraImage") {
			return;
		}
		if (list1[1] == "SetGapMax") {
			if (list1.length() == 3)
				obj->gap_max = list1[2].toInt();
			return;
		}
		else if (list1[1] == "Init") {
			//qDebug() << "init_sdk before is ------ " << obj->gUltraSDK;
			obj->init_sdk();
			qDebug() << "UltraSDK inititilized ------ ";
			return;
		}
		else if (list1[1] == "SetPreset") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString preset = list1[2];
			
			if (!obj->gUltraSDK->setPreset(preset.toStdString()))
				qDebug() << "setPreset has Failed!!!!!!!!!!!!!!!!!! ";

			return;
		}
		else if (list1[1] == "SetDepth") {
			//qDebug() << "depth is ------ " << obj->gUltraSDK;
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString depth = list1[2];
			double doudepth = depth.toDouble();
			if (obj->gUltraSDK) {
				if (!obj->gUltraSDK->setDepthValue(doudepth))
					qDebug() << "setDepthValue to " << doudepth <<" has Failed!!!!!!!!!!!!!!!!!!";
			}
		}
		else if (list1[1] == "setFreeze") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString fr = list1[2];
			int fr1 = fr.toInt();
			bool bFreeze = fr1 == 1;
			if (!obj->gUltraSDK->setFreeze(bFreeze))
				qDebug() << "setFreeze to " << fr1 << " has Failed!!!!!!!!!!!!!!!!!!";
			//if (fr1 == 1)
			//	obj->gUltraSDK->setFreeze(true);
			//else
			//	obj->gUltraSDK->setFreeze(false);
		}
		else if (list1[1] == "SetLiveGain") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString gain = list1[2];
			int intgain = gain.toInt();
			//qDebug() << "intgain    " << intgain;
			if (!obj->gUltraSDK->setLiveGain(intgain))
				qDebug() << "setLiveGain to " << intgain << " has Failed!!!!!!!!!!!!!!!!!!";
			return;
		}
		else if (list1[1] == "switchToBMode") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			if (!obj->gUltraSDK->switchToBMode())
				qDebug() << "switchToBMode has Failed!!!!!!!!!!!!!!!!!! ";
		}
		else if (list1[1] == "switchToPDIMode") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			if (!obj->gUltraSDK->switchToPDIMode())
				qDebug() << "SwitchToPDIMode has Failed!!!!!!!!!!!!!!!!!! ";
			return;
		}
		else if (list1[1] == "switchToTMode") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			//qDebug() << "Before switchToTMode. ";
			if (!obj->gUltraSDK->switchToTMode())
				qDebug() << "SwitchToTMode has Failed!!!!!!!!!!!!!!!!!! ";
			return;
		}
		else if (list1[1] == "SetActivateProbe") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString Probe = list1[2];
			if (!obj->gUltraSDK->setActivateProbe(Probe.toStdString()))
				qDebug() << "setActivateProbe to " << Probe.toStdString().c_str() << " has Failed!!!!!!!!!!!!!!!!!!";
			return;
		}
		else if (list1[1] == "setTissueFocus") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString VA = list1[2];
			int douVA = VA.toInt();
			obj->gUltraSDK->setTissueFocus(douVA);
			return;
		}
		else if (list1[1] == "setColorFocus") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString VA = list1[2];
			int douVA = VA.toInt();
			obj->gUltraSDK->setColorFocus(douVA);
			return;
		}
		else if (list1[1] == "setCFrequency") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString VA = list1[2];
			double douVA = VA.toDouble();
			//obj->gUltraSDK->setCFrequency(douVA);
			return;
		}
		else if (list1[1] == "resetTGC") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->gUltraSDK->resetTGC();
			return;
		}
		else if (list1[1] == "setTGC1") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC1(val);
			return;
		}
		else if (list1[1] == "setTGC2") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC2(val);
			return;
		}
		else if (list1[1] == "setTGC3") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC3(val);
			return;
		}
		else if (list1[1] == "setDebugMode") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->debug_mode = list1[2];
			return;
		}
		else if (list1[1] == "setTGC4") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC4(val);
			return;
		}
		else if (list1[1] == "setTGC5") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC5(val);
			return;
		}
		else if (list1[1] == "setTGC6") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC6(val);
			return;
		}
		else if (list1[1] == "setTGC7") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC7(val);
			return;
		}
		else if (list1[1] == "setTGC8") {
			QString VA = list1[2];
			int val = VA.toInt();
			obj->gUltraSDK->setTGC8(val);
			return;
		}
		else if (list1[1] == "setCROI") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString VA1 = list1[2];
			QString VA2 = list1[3];
			QString VA3 = list1[4];
			QString VA4 = list1[5];
			double val1 = VA1.toDouble();
			double val2 = VA2.toDouble();
			double val3 = VA3.toDouble();
			double val4 = VA4.toDouble();
			if (!obj->gUltraSDK->setCROI(val1, val2, val3, val4))
				qDebug() << "setCROI has Failed!!!!!!!!!!!!!!!!!! ";
			return;
		}
		else if (list1[1] == "Finalize") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			if (!obj->gUltraSDK->finalizeSDK())
				qDebug() << "finalizeSDK has Failed!!!!!!!!!!!!!!!!!! ";
			return;
		}
		else if (list1[1] == "SaveToBinFlag") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->save_to_bin_flag = true;
			//qDebug() << "SaveToBinFlag called. ";
			return;
		}
		else if (list1[1] == "CaculateBModeFPS") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->caculate_b_mode_flag = true;
			obj->timer_b.start();
			return;
		}
		else if (list1[1] == "CaculateTModeFPS") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->caculate_t_mode_flag = true;
			obj->timer_t.start();
			qDebug() << "CaculateTModeFPS called. ";
			return;
		}
		else if (list1[1] == "CaculatePDIModeFPS") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			obj->caculate_pdi_mode_flag = true;
			obj->timer_pdi.start();
			return;
		}
		else if (list1[1] == "SetPower") {
			if (!obj->gUltraSDK->targetPresent())
			{
				return;
			}
			QString power = list1[2];
			int intPower = power.toInt();
			if (obj->gUltraSDK) {
				obj->gUltraSDK->setPower(intPower);
			}
		}
	}
	catch (const std::exception& e) {
		qDebug() << "ultra SDK send cmd an exception occurred: " << e.what();
	}
}

QString qUltraImageControllThreadObject::send_synchronize_cmd(QString cmd) {
	QString res;
	QStringList list1 = cmd.split(", ");
	QStringList tmp;

	if (list1.size() > 1)
		qDebug() << "send_synchronize_cmd " << list1[1].toStdString().c_str();

	if (list1[1] == "GetInfo") {
		tmp << "Info: ";
		int id = obj->gUltraSDK->getProbeID();
		tmp << "\nProbeID: " + id;
		int type = obj->gUltraSDK->getProbeType();
		tmp << "\nProbeType: " + type;
		std::string name = obj->gUltraSDK->getProbeName();
		tmp << "\nProbeName: " + QString::fromStdString(name);

		double mi = obj->gUltraSDK->getMIValue();
		tmp << "\nMI: " + QString::number(mi);
		double ti = obj->gUltraSDK->getTIValue();
		tmp << "\nTI: " + QString::number(ti);

		std::string version = obj->gUltraSDK->getHWRevision();
		tmp << "\nHWRevision: " + QString::fromStdString(version);
		double depth = obj->gUltraSDK->getDepthValue();
		tmp << "\nDepth: " + QString::number(depth);
		int gain = obj->gUltraSDK->getLiveGain();
		tmp << "\nLiveGain: " + QString::number(gain);
		bool isHarmonic = obj->gUltraSDK->isHarmonic();
		tmp << "\nisHarmonic: " + isHarmonic;
		bool isModeLive = obj->gUltraSDK->isModeLive();
		tmp << "\n isModeLive: " + isModeLive;
		res = tmp.join(", ");
		qDebug() << "send_synchronize_cmd Get_info(): " << res.toStdString().c_str();
	}
	else if (list1[1] == "GetDepth") {
		if (!obj->gUltraSDK->targetPresent())
		{
			//qDebug() << "i am not a targetPresent";
			return "0";
		}
		double depth = obj->gUltraSDK->getDepthValue();
		//qDebug() << "c++ depth is :" << depth;
		res = QString::number(depth);
	}
	else if (list1[1] == "GetMITI") {
		if (!obj->gUltraSDK->targetPresent())
		{
			return "0";
		}
		double mi = obj->gUltraSDK->getMIValue();
		tmp << "\nMI:" + QString::number(mi);
		double ti = obj->gUltraSDK->getTIValue();
		tmp << "\nTI:" + QString::number(ti);
		res = tmp.join(", ");
	}
	else if (list1[1] == "GetProbe") {
		if (!obj->gUltraSDK->targetPresent())
		{
			return "0";
		}
		std::string name = obj->gUltraSDK->getProbeName();
		res = QString::fromStdString(name);
	}
	else if (list1[1] == "GetInitProbe") {
		res = obj->m_pData;
		qDebug() << "init Probe value:" << res;
	}
	return res;
}