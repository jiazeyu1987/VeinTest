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

#ifndef __qSlicerRequestStatusModuleWidgetqIMEControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqIMEControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qIMEReceiveThreadObject.h>
#include <qControlThreadBaseObject.h>

#include "AimPositionAPI.h"
#include "AimPositionDef.h"

#include <Windows.h>
#include "qIMEReceiveThreadObject.h"
#ifdef _DEBUG
#ifdef _WIN64
#pragma comment(lib,"AimPosition2.3.3d.lib")
#else
#pragma comment(lib,"AimPosition2.3.3dX86.lib")
#endif
#else
#ifdef _WIN64
#pragma comment(lib,"AimPosition2.3.3.lib")
#else
#pragma comment(lib,"AimPosition2.3.3X86.lib")
#endif

#endif // _DEBUG

class qIMEControllThreadObject : public qControlThreadBaseObject
{
    Q_OBJECT
public slots:
    void send_thread_cmd(QString cmd);
    void init(qIMEReceiveThreadObject* in_obj) { obj = in_obj; };
public:
    qIMEReceiveThreadObject* obj = nullptr;
    QString send_synchronize_cmd(QString cmd);
private:
    void vInitalCamera();

    void vConnectCamera(QString ip);
};


#endif