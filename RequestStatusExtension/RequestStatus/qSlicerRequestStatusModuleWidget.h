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

#ifndef __qSlicerRequestStatusModuleWidget_h
#define __qSlicerRequestStatusModuleWidget_h

// Slicer includes
#include "qSlicerAbstractModuleWidget.h"
#include <qtimer.h>
#include "qSlicerRequestStatusModuleExport.h"
#include <vtkMRMLScene.h>
#include <vtkCallbackCommand.h>
#include <QDebug>
#include <QThread>
#include "qReceiveThreadBaseObject.h"
#include "qControlThreadBaseObject.h"
#include "qElibotReceiveThreadObject.h"
#include "qURReceiveThreadObject.h"
#include "qURControllThreadObject.h"
#include "qIMEControllThreadObject.h"
#include "qIMEReceiveThreadObject.h"
#include "qNDIControllThreadObject.h"
#include "qNDIReceiveThreadObject.h"
#include "qElibotControllThreadObject.h"
#include "qElibotReceiveThreadObject.h"
#include "qUSBHidControllThreadObject.h"
#include "qUSBHidReceiveThreadObject.h"
#include "qRegisterControllThreadObject.h"
#include "qRegisterReceiveThreadObject.h"
#include "qSystemReceiveThreadObject.h"
#include "qPowerControllThreadObject.h"
#include "qPowerReceiveThreadObject.h"
#include "qUltrasoundGeneratorControllThreadObject.h"
#include "qUltrasoundGeneratorReceiveThreadObject.h"
#include "qWaterColdingControllThreadObject.h"
#include "qWaterColdingReceiveThreadObject.h"
#include "qUltraImageControllThreadObject.h"
#include "qUltraImageReceiveThreadObject.h"
#include "qDeviceControllThreadObject.h"
#include "qDeviceReceiveThreadObject.h"
#include "qUltraImageControllThreadObject.h"
#include "qUltraImageReceiveThreadObject.h"
#include <UltraSDK/Target/include/UltraSDK.h>
#include "QMutex.h"
class qSlicerRequestStatusModuleWidgetPrivate;
class vtkMRMLNode;


/// \ingroup Slicer_QtModules_ExtensionTemplate
class Q_SLICER_QTMODULES_REQUESTSTATUS_EXPORT qSlicerRequestStatusModuleWidget :
  public qSlicerAbstractModuleWidget
{
  Q_OBJECT

public:
    //For Elirobot Statics
    

    
public:
    UltraSDK* gUltraSDK = nullptr;
    static void ReceiveTickCallback(vtkObject* caller, unsigned long eid, void* clientData, void* callData);
    void connect_subthread_to_main(std::string key, bool tobind);
    void connect_subthread_to_subthread(std::string main_key, std::string sub_key,bool tobind);
    Q_INVOKABLE void start_thread(float gap);
    Q_INVOKABLE void pause_thread();
  typedef qSlicerAbstractModuleWidget Superclass;
  qSlicerRequestStatusModuleWidget(QWidget *parent=0);
  virtual ~qSlicerRequestStatusModuleWidget();
  Q_INVOKABLE void add_handler(QString key);
  Q_INVOKABLE void send_cmd(QString cmd);
  Q_INVOKABLE QString send_synchronize_cmd(QString cmd);
  Q_INVOKABLE std::string get_info();
  Q_INVOKABLE int bind_subthreads(QStringList namelist, bool to_bind);
  QTimer* timer = nullptr;
  Q_INVOKABLE unsigned char* get_ultra_image();
signals:
    void on_tick();
    void on_tick_python(QString);
    void send_signal_cmd(QString);
public slots:
    void on_main_thread_tick();
    void shutdown();
public:
  QScopedPointer<qSlicerRequestStatusModuleWidgetPrivate> d_ptr;
  QMap<std::string, vtkSmartPointer<vtkCallbackCommand>> map_vtkCallbackCommand;
  QMap<std::string, unsigned long > map_ReceiveCallbackTag;
  QMap<std::string, qReceiveThreadBaseObject* >  map_ReceiveObject;
  QMap<std::string, QThread* >  map_ReceiveThread;
  QMap<std::string, qControlThreadBaseObject* >  map_ControlObject;
  QMap<std::string, QThread* >  map_ControlThread;
  QMap<std::string, std::string > map_AllInfo;
  QMap<std::string, std::vector<std::string> > bind_map;
  void setup() override;
  QMutex mutex;
  
private:
  Q_DECLARE_PRIVATE(qSlicerRequestStatusModuleWidget);
  Q_DISABLE_COPY(qSlicerRequestStatusModuleWidget);
};

#endif
