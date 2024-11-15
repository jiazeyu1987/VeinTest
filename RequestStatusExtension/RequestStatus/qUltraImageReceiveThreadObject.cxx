#include "qUltraImageReceiveThreadObject.h"
#include <iostream>

#include "vtkMRMLCoreTestingMacros.h"
#include "vtkMRMLScene.h"
#include "qSlicerApplication.h"
#include "vtkMRMLStreamingVolumeNode.h"
#include <QRandomGenerator>
#include <qSlicerLayoutManager.h>
#include <vtkCollection.h>
#include <vtkMRMLSliceLogic.h>
#include <qMRMLSliceWidget.h>
#include <vtkMRMLSliceNode.h>
#include <vtkMRMLSliceCompositeNode.h>
#include <vtkSlicerVolumeRenderingLogic.h>
#include <vtkMRMLVolumeRenderingDisplayNode.h>
#include <QDir>
#include <QDate>
#include <vector>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <fstream>
#include <memory>

const int BModeLen = 921600;
const int PDIModeLen = 1228800;
const int TempLen = 518144;
unsigned char pDST[BModeLen];
unsigned char pPDI[PDIModeLen];
unsigned char pTemp[TempLen];
int frameCountBMode = 0;
int frameCountPDIMode = 0;
int frameCountTMode = 0;
int saveToBinFlag = 0;
int saveToPngFlag = 0;
QElapsedTimer timer2;
int flag = 0;
bool flag_bmode = false;
bool flag_tmode = false;
bool flag_pdimode = false;
int a = 0;

constexpr size_t T_MODE_DATA_SIZE = TempLen; // T模式数据文件的固定大小

std::queue<std::map<QString, std::shared_ptr<std::vector<unsigned char>>>> tModeQueue;
std::mutex queueMutex;
std::condition_variable dataCondition;
bool stopSaving = false;
QString tModeDateFolder;
const QString tModeRootDirectory = "D:/ultrasound_data/T_data";
QString bModeDateFolder;
const QString bModeRootDirectory = "D:/ultrasound_data/B_data";
QString pDIModeDateFolder;
const QString pDIModeRootDirectory = "D:/ultrasound_data/PDI_data";

void MonitorISR(const int& MsgType, unsigned char* pData, const unsigned int nLength);
void FrameISR2(const int& eMode, unsigned char* pData, const unsigned int nLength);
void asyncSaveData();

QString qUltraImageReceiveThreadObject::m_pData = "";

qUltraImageReceiveThreadObject::qUltraImageReceiveThreadObject() {
	std::thread(asyncSaveData).detach();
}

qUltraImageReceiveThreadObject::~qUltraImageReceiveThreadObject() {
	{
		std::lock_guard<std::mutex> lock(queueMutex);
		stopSaving = true;
	}
	dataCondition.notify_all();
}

unsigned char* qUltraImageReceiveThreadObject::get_ultra_image() {
	return pDST;
}

void qUltraImageReceiveThreadObject::OnReceiveObjectInnerTick2() {
	int randomValue = QRandomGenerator::global()->bounded(1000);
	unsigned char* ptr = pDST;
	int randVal = randomValue;
	for (ptr = pDST; ptr != pDST + BModeLen; ptr++)
	{
		*ptr = randVal++ % 255;
	}
	//for (int i = 0; i < BModeLen; i++) {
	//	pDST[i] = (randomValue + i) % 255;
	//}
	auto nodename = "ultrasound_volue";
	auto node = qSlicerApplication::application()->mrmlScene()->GetFirstNodeByName(nodename);
	if (node == nullptr) {
		node = qSlicerApplication::application()->mrmlScene()->AddNewNodeByClass("vtkMRMLVectorVolumeNode");
		node->SetName(nodename);
	}

	vtkMRMLVectorVolumeNode* mvnode = dynamic_cast<vtkMRMLVectorVolumeNode*>(node);
	vtkImageData* newVolumeData = mvnode->GetImageData();

	/*vtkNew<vtkSlicerVolumeRenderingLogic> vrLogic;
	vrLogic->SetMRMLScene(qSlicerApplication::application()->mrmlScene());
	vrLogic->CreateDefaultVolumeRenderingNodes(mvnode);
	vtkMRMLVolumeRenderingDisplayNode* vrDisplayNode = vrLogic->GetFirstVolumeRenderingDisplayNode(mvnode);
	vrDisplayNode->SetVisibility(false);*/

	if (newVolumeData == nullptr) {
		vtkNew<vtkImageData> imageData;
		imageData->SetDimensions(640, 480, 1); // ʹ��2Dͼ��ĳߴ�
		imageData->AllocateScalars(VTK_UNSIGNED_CHAR, 3); // ��������ֻʹ��һ����ɫͨ��

		//size_t byte_count = 640 * 480 * 3 * sizeof(unsigned char);
		//if (pDST != nullptr) {
		//	memcpy(imageData->GetScalarPointer(), pDST, byte_count);	//reverse order
		//}
		//imageData->Modified();

		unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
		unsigned char* ptrDST = pDST + BModeLen - 1; //pointer of pDST in reverse order
		for (; ptrDST >= pDST; pixel++, ptrDST--) {
			*pixel = *ptrDST;
		}

		//unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
		//for (size_t i = 0; i < BModeLen; i++) {
		//	pixel[i] = pDST[BModeLen - 1 - i];
		//}
		mvnode->SetAndObserveImageData(imageData);

		/*auto displaynode = mvnode->GetDisplayNode();
		if (displaynode == nullptr) {
			mvnode->CreateDefaultDisplayNodes();
			displaynode = mvnode->GetDisplayNode();
		}*/
		/*std::vector<std::string> viewids;
		viewids.push_back("vtkMRMLSliceNodeRed+");
		displaynode->RemoveAllViewNodeIDs();
		displaynode->SetViewNodeIDs(viewids);*/

		/*qSlicerLayoutManager* layoutManager = qSlicerApplication::application()->layoutManager();
		vtkCollection* sliceLogics = layoutManager->mrmlSliceLogics();

		if (!sliceLogics)
		{
			return;
		}
		vtkObject* object = nullptr;
		vtkCollectionSimpleIterator it;
		for (sliceLogics->InitTraversal(it); (object = sliceLogics->GetNextItemAsObject(it));)
		{
			vtkMRMLSliceLogic* sliceLogic = vtkMRMLSliceLogic::SafeDownCast(object);
			sliceLogic->FitSliceToAll(true);
		}*/
	}
	else {
		unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
		unsigned char* ptrDST = pDST + BModeLen - 1;		//pointer of pDST in reverse order
		for (; ptrDST >= pDST; pixel++, ptrDST--) {
			*pixel = *ptrDST;
		}
		//unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
		//for (size_t i = 0; i < BModeLen; i++) {
		//	pixel[i] = pDST[BModeLen - 1 - i];
		//}
		auto displaynode = mvnode->GetDisplayNode();
		if (displaynode == nullptr) {
			mvnode->CreateDefaultDisplayNodes();
			displaynode = mvnode->GetDisplayNode();
		}
		/*std::vector<std::string> viewids;
		viewids.push_back("vtkMRMLSliceNodeRed+");
		displaynode->RemoveAllViewNodeIDs();
		displaynode->SetViewNodeIDs(viewids);*/
	}

	return;
}

void qUltraImageReceiveThreadObject::CaculateBModeFPS()
{
	if (timer_b.elapsed() >= 1000) {  // ÿ��1000���루1�룩����һ��֡��
		int fps = frameCountBMode;
		//qDebug() << "fps_b:" << fps;
		frameCountBMode = 0;
		timer_b.restart();
	}
}

void qUltraImageReceiveThreadObject::CaculateTModeFPS()
{
	if (timer_t.elapsed() >= 1000) {  // ÿ��1000���루1�룩����һ��֡��
		int fps = frameCountTMode;
		//qDebug() << "fps_t:" << fps;
		frameCountTMode = 0;
		timer_t.restart();
	}
}

void qUltraImageReceiveThreadObject::CaculatePDIModeFPS()
{
	if (timer_pdi.elapsed() >= 1000) {  // ÿ��1000���루1�룩����һ��֡��
		int fps = frameCountPDIMode;
		//qDebug() << "fps_pdi:" << fps;
		frameCountPDIMode = 0;
		timer_pdi.restart();
	}
}

void qUltraImageReceiveThreadObject::SaveToPng()
{
	QDateTime now = QDateTime::currentDateTime();
	QString timeString = now.toString("yyyyMMdd_HHmmss_zzz");
	QString dateFolderName = QDate::currentDate().toString("yyyy-MM-dd");
	bModeDateFolder = QString("%1/%2").arg(bModeRootDirectory).arg(dateFolderName);
	QDir dir;
	if (!dir.exists(bModeDateFolder)) {
		dir.mkpath(bModeDateFolder);
	}
	//qDebug() << "save to b mode in";
	if (flag_bmode) {
		unsigned char* pDST2 = new unsigned char[BModeLen / 3];
		for (int i = 0; i < BModeLen / 3; i++) {
			pDST2[i] = pDST[i * 3];
		}
		//std::vector<unsigned char> pDST2(pDST, pDST + BModeLen / 3);
		//qDebug() << "data is to trasfer";
		QImage image(pDST2, 640, 480, QImage::Format_Grayscale8);
		QString path = QString("%1/%2.png").arg(bModeDateFolder).arg(timeString);
		image.save(path);
		//qDebug() << "data is saved";
	}
	//flag_bmode = false;
}

void qUltraImageReceiveThreadObject::SaveToPng2()
{
	//qDebug() << "save to PDI mode in";
	if (flag_pdimode) {
		QImage image(pPDI, 640, 480, QImage::Format_RGBA8888);
		QString path = QString("D:/2/tmp/%1.png").arg(frameCountPDIMode);
		image.save(path);
	}
	//flag_bmode = false;
}

//void qUltraImageReceiveThreadObject::SaveToBin()
//{
//	//qDebug() << "save to T mode in" << saveToBinFlag;
//	if (flag_tmode) {
//		QString path = QString("D:/ultrasound_data/T_data/%1.bin").arg(saveToBinFlag);
//		std::ofstream outFile(path.toStdString(), std::ios::binary);
//		if (!outFile) {
//			std::cerr << "Error opening file for writing." << std::endl;
//			return;  // �ļ���ʧ�ܣ����ش������
//		}
//		outFile.write(reinterpret_cast<const char*>(pTemp), TempLen);
//
//		// ����Ƿ�ɹ�д��
//		if (!outFile) {
//			std::cerr << "Error writing to file." << std::endl;
//			return;  // д��ʧ�ܣ����ش������
//		}
//
//		// �ر��ļ�
//		outFile.close();
//	}
//	//flag_tmode = false;
//}

void qUltraImageReceiveThreadObject::UpdateBModeTick() {
	auto nodename = "ultrasound_volue";
	auto node = qSlicerApplication::application()->mrmlScene()->GetFirstNodeByName(nodename);
	if (node == nullptr) {
		node = qSlicerApplication::application()->mrmlScene()->AddNewNodeByClass("vtkMRMLVectorVolumeNode");
		node->SetName(nodename);
	}

	vtkMRMLVectorVolumeNode* mvnode = dynamic_cast<vtkMRMLVectorVolumeNode*>(node);
	vtkImageData* newVolumeData = mvnode->GetImageData();

	if (newVolumeData == nullptr) {
		vtkNew<vtkImageData> imageData;
		imageData->SetDimensions(640, 480, 1); // ʹ��2Dͼ��ĳߴ�
		imageData->AllocateScalars(VTK_UNSIGNED_CHAR, 3); // ��������ֻʹ��һ����ɫͨ��
		unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
		unsigned char* ptrDST = pDST + BModeLen - 1;		//pointer of pDST in reverse order
		for (; ptrDST >= pDST; pixel++, ptrDST--) {
			*pixel = *ptrDST;
		}

		//unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
		//for (size_t i = 0; i < BModeLen; i++) {
		//	pixel[i] = pDST[BModeLen - 1 - i];
		//}
		mvnode->SetAndObserveImageData(imageData);
	}
	else {
		unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
		unsigned char* ptrDST = pDST + BModeLen - 1;		//pointer of pDST in reverse order
		for (; ptrDST >= pDST; pixel++, ptrDST--) {
			*pixel = *ptrDST;
		}

		//unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
		//for (size_t i = 0; i < BModeLen; i++) {
		//	pixel[i] = pDST[BModeLen - 1 - i];
		//}
	}
}

void qUltraImageReceiveThreadObject::UpdatePDIModeTick() {
	if (!flag_pdimode) {
		return;
	}
	auto nodename = "ultrasound_pdi";
	auto node = qSlicerApplication::application()->mrmlScene()->GetFirstNodeByName(nodename);
	if (node == nullptr) {
		node = qSlicerApplication::application()->mrmlScene()->AddNewNodeByClass("vtkMRMLVectorVolumeNode");
		node->SetName(nodename);
	}

	vtkMRMLVectorVolumeNode* mvnode = dynamic_cast<vtkMRMLVectorVolumeNode*>(node);
	vtkImageData* newVolumeData = mvnode->GetImageData();
	const size_t numPixels = BModeLen;
	const size_t numComponents = 3;
	unsigned char tmp[numPixels];

	//pointers for tmp, step size 3
	unsigned char* pTmp = tmp;
	//pointer for PDI, step size 4
	unsigned char* ptrPDI = pPDI;
	for (size_t i = 0; i < numPixels / numComponents; ++i, pTmp += 3, ptrPDI += 4) {
		if ((ptrPDI[3]) == 0) {
			std::fill_n(pTmp, numComponents, 0);
		}
		else {
			std::copy_n(ptrPDI, numComponents, pTmp);
		}
	}

	/*
	for (size_t i = 0; i < numPixels / numComponents; ++i) {
		if ((pPDI[i * 4 + 3]) == 0) {
			std::fill_n(tmp + i * numComponents, numComponents, 0);
		}
		else {
			std::copy_n(pPDI + i * 4, numComponents, tmp + i * numComponents);
		}
	}*/

	if (newVolumeData == nullptr) {
		vtkNew<vtkImageData> imageData;
		imageData->SetDimensions(640, 480, 1); // ʹ��2Dͼ��ĳߴ�
		imageData->AllocateScalars(VTK_UNSIGNED_CHAR, 3); // ��������ֻʹ��һ����ɫͨ��
		unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
		std::reverse_copy(tmp, tmp + numPixels, pixel);

		mvnode->SetAndObserveImageData(imageData);
	}
	else {
		unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
		std::reverse_copy(tmp, tmp + numPixels, pixel);
		//for (size_t i = 0; i < BModeLen; i++) {
		//	pixel[i] = tmp[BModeLen - 1 - i];
		//}
	}
	qDebug() << "save to PDI mode flag" << flag_pdimode;
	SaveToPng2();
	//flag_pdimode = false;
}

void qUltraImageReceiveThreadObject::OnReceiveObjectInnerTick() {
	//qDebug() << "save to T mode flag" << saveToBinFlag;
	try {
		if (save_to_bin_flag) {
			//SaveToPng2();
			SaveToPng();
			//SaveToBin();
		}
		if (caculate_b_mode_flag) {
			CaculateBModeFPS();
		}
		if (caculate_t_mode_flag) {
			CaculateTModeFPS();
		}
		if (caculate_pdi_mode_flag) {
			CaculatePDIModeFPS();
		}
		auto nodename = "ultrasound_volue";
		auto node = qSlicerApplication::application()->mrmlScene()->GetFirstNodeByName(nodename);
		if (node == nullptr) {
			node = qSlicerApplication::application()->mrmlScene()->AddNewNodeByClass("vtkMRMLVectorVolumeNode");
			node->SetName(nodename);
		}

		vtkMRMLVectorVolumeNode* mvnode = dynamic_cast<vtkMRMLVectorVolumeNode*>(node);
		vtkImageData* newVolumeData = mvnode->GetImageData();

		if (newVolumeData == nullptr) {
			vtkNew<vtkImageData> imageData;
			imageData->SetDimensions(640, 480, 1); // ʹ��2Dͼ��ĳߴ�
			imageData->AllocateScalars(VTK_UNSIGNED_CHAR, 3); // ��������ֻʹ��һ����ɫͨ��
			//unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
			//unsigned char* ptrDST = pDST + BModeLen - 1;		//pointer of pDST in reverse order
			//for (; ptrDST >= pDST; pixel++, ptrDST--) {
			//	*pixel = *ptrDST;
			//}
			unsigned char* pixel = static_cast<unsigned char*>(imageData->GetScalarPointer(0, 0, 0));
			for (size_t i = 0; i < BModeLen; i++) {
				pixel[i] = pDST[BModeLen - 1 - i];
			}
			mvnode->SetAndObserveImageData(imageData);
		}
		else {
			//unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
			//unsigned char* ptrDST = pDST + BModeLen - 1;		//pointer of pDST in reverse order
			//for (; ptrDST >= pDST; pixel++, ptrDST--) {
			//	*pixel = *ptrDST;
			//}
			unsigned char* pixel = static_cast<unsigned char*>(newVolumeData->GetScalarPointer(0, 0, 0));
			for (size_t i = 0; i < BModeLen; i++) {
				pixel[i] = pDST[BModeLen - 1 - i];
			}
		}
		//a++;
		//qDebug() << "BMode Data update :";

		if (flag_pdimode)
			UpdatePDIModeTick();
	}
	catch (const std::exception& e) {
		qDebug() << "ultra image update an exception occurred: " << e.what();
	}
}

void qUltraImageReceiveThreadObject::init_sdk() {
	try
	{
		gUltraSDK = new UltraSDK();
		gUltraSDK->initializeSDK(FrameISR2);
		gUltraSDK->setMonitorMgrCallback(MonitorISR);
	}
	catch (const std::exception& e) {
		qDebug() << "ultra SDK initialized an exception occurred: " << e.what();
	}
}

qUltraImageReceiveThreadObject test_q = qUltraImageReceiveThreadObject();

void MonitorISR(const int& MsgType, unsigned char* pData, const unsigned int nLength)
{
	//qDebug() << "On MonitorISR:" << MsgType << "," << pData << "," << nLength;
	QString m_pData = reinterpret_cast<char*>(pData);
	switch (MsgType)
	{
	case 1:  //Probe connect
		//qDebug() << "On MonitorISR Probe:" << MsgType << "," << pData << "," << nLength;
		qUltraImageReceiveThreadObject::m_pData = m_pData;
		//qDebug() << "On MonitorISR Probe value:" << MsgType << "," << qUltraImageReceiveThreadObject::m_pData << "," << nLength;
		break;
	case 2:  //Voltage monitor
		//qDebug() << "On MonitorISR Voltage:" << MsgType << "," << m_pData << "," << nLength;
		break;
	case 3:  //Temperature monitor
		//qDebug() << "On MonitorISR Temperature:" << MsgType << "," << m_pData << "," << nLength;
		break;
	default:
		//qDebug() << "On MonitorISR default:" << MsgType << "," << m_pData << "," << nLength;
		break;
	}
}

void FrameISR2(const int& eMode, unsigned char* pData, const unsigned int nLength)
{
	try {
		switch (eMode)
		{
		case 1:  //B mode
			//qDebug() << "BMode Data:" << nLength << " :::::::::::::::::::::::::::::::::::";
			if (nLength > BModeLen)
				qDebug() << "BMode Data overflow :" << nLength << " :::::::::::::::::::::::::::::::::::>" << BModeLen;
			else
			{
				memcpy(pDST, pData, nLength);
				frameCountBMode++;
				flag_bmode = true;
				flag_pdimode = false;
				flag_tmode = false;
				saveToPngFlag++;
				//qDebug() << "saveToPngFlag is:" << saveToBinFlag;
				//qDebug() << "BMode Data:" << frameCountBMode << "::::::::::::::::::::::::::::::";
			}
			break;
		case 2:  //PDI mode
			//qDebug() << "PDIMode Data:" << nLength << "," << frameCountPDIMode << " :::::::::::::::::::::::::::::::::::";
			if (nLength > PDIModeLen)
				qDebug() << "PDIMode Data overflow :" << nLength << " :::::::::::::::::::::::::::::::::::>" << PDIModeLen;
			else
			{
				memcpy(pPDI, pData, nLength);
				frameCountPDIMode++;
				flag_bmode = false;
				flag_pdimode = true;
				flag_tmode = false;
			}
			break;
		case 3:  //Temperature mode
			//qDebug() << "TMode Data:" << nLength << " :::::::::::::::::::::::::::::::::::";
			if (nLength > TempLen)
				qDebug() << "TMode Data overflow :" << nLength << " :::::::::::::::::::::::::::::::::::>" << TempLen;
			else
			{
				frameCountTMode++;
				saveToBinFlag++;
				memcpy(pTemp, pData, nLength);
				//qDebug() << "saveToBinFlag is:" << saveToBinFlag;
				flag_bmode = false;
				flag_pdimode = false;
				flag_tmode = true;
				test_q.SaveToBin();
			}
			break;
		default:
			break;
		}
	}
	catch (const std::exception& e) {
		qDebug() << "ultra update data an exception occurred: " << e.what();
	}
}

void qUltraImageReceiveThreadObject::SaveToBin() {
	qDebug() << "save to bin T mode" << flag_tmode;
	if (flag_tmode) {
		auto data = std::make_shared<std::vector<unsigned char>>(pTemp, pTemp + T_MODE_DATA_SIZE);

		// 获取当前时间字符串，精确到毫秒
		QDateTime now = QDateTime::currentDateTime();
		QString timeString = now.toString("yyyyMMdd_HHmmss_zzz");

		std::map<QString, std::shared_ptr<std::vector<unsigned char>>> dataMap;
		dataMap[timeString] = data;

		{
			std::lock_guard<std::mutex> lock(queueMutex);
			tModeQueue.push(dataMap);
			//qDebug() << "queue size is " << tModeQueue.size();
		}
		dataCondition.notify_one();
	}
}

void asyncSaveData() {
	QString dateFolderName = QDate::currentDate().toString("yyyy-MM-dd");
	tModeDateFolder = QString("%1/%2").arg(tModeRootDirectory).arg(dateFolderName);
	QDir dir;
	if (!dir.exists(tModeDateFolder)) {
		dir.mkpath(tModeDateFolder);
	}

	while (!stopSaving) {
		std::unique_lock<std::mutex> lock(queueMutex);
		dataCondition.wait(lock, [] { return !tModeQueue.empty() || stopSaving; });

		while (!tModeQueue.empty()) {
			auto dataMap = tModeQueue.front();
			tModeQueue.pop();
			lock.unlock();

			const auto& timeString = dataMap.begin()->first;
			const auto& data = dataMap.begin()->second;

			QString path = QString("%1/%2.bin").arg(tModeDateFolder).arg(timeString);
			std::ofstream outFile(path.toStdString(), std::ios::binary);
			if (!outFile) {
				std::cerr << "Error opening file for writing." << std::endl;
				return;
			}
			outFile.write(reinterpret_cast<const char*>(data->data()), data->size());
			if (!outFile) {
				std::cerr << "Error writing to file." << std::endl;
				return;
			}
			outFile.close();
			lock.lock();
		}
	}
}