#ifndef __qSlicerRequestStatusModuleWidgetqUltraImageReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqUltraImageReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include "QMutex.h"
#include <qReceiveThreadBaseObject.h>
#include <UltraSDK/Target/include/UltraSDK.h>
#include <QElapsedTimer>

class qUltraImageReceiveThreadObject : public qReceiveThreadBaseObject
{
	Q_OBJECT
public:
	qUltraImageReceiveThreadObject();
	~qUltraImageReceiveThreadObject();
	void OnReceiveObjectInnerTick();
	void UpdateBModeTick();
	void UpdatePDIModeTick();
	void OnReceiveObjectInnerTick2();
	void SaveToPng();
	void SaveToPng2();
	void SaveToBin();
	void CaculateBModeFPS();
	void CaculateTModeFPS();
	void CaculatePDIModeFPS();
	void init_sdk();
	int frameBModeCount = 0;
	int frameTModeCount = 0;
	int framePDIModeCount = 0;
	QElapsedTimer timer_b;
	QElapsedTimer timer_t;
	QElapsedTimer timer_pdi;
	Q_INVOKABLE  unsigned char* get_ultra_image();
public:
	UltraSDK* gUltraSDK = nullptr;
	bool save_to_bin_flag = false;
	bool caculate_b_mode_flag = false;
	bool caculate_t_mode_flag = false;
	bool caculate_pdi_mode_flag = false;
	static QString m_pData;
	QString debug_mode = "";
};

#endif