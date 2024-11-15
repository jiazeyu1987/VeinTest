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

#ifndef __qSlicerRequestStatusModuleWidgetqIMEReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqIMEReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>

#include "AimPositionAPI.h"
#include "AimPositionDef.h"

#include <Windows.h>
#include "qSlicerRequestStatusModule.h"

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

typedef struct s_MarkerOutput {
    double coordinates[3];//x y z
    int32_t id = -1;//tracking id
    int32_t last_id = -1;// last frame's tracking id
    float confidence = 0.0f;// confidence of marker's coordinates
    double dis_sum = 0.0f;// distance sum to other markers
    double last_dis_sum = -1.0f; // last frame's distance sum to other markers
}MarkerOutput;

class qIMEReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick() override;
public:
    AimHandle m_aimHandle;
    std::string m_hardware_verion;
    T_AIMPOS_DATAPARA m_PosDataPara;
    QString track();
private:
    int m_last_marker_num = -1;
private:
    std::string EXCEPTION_TRACK = "track_exception";
    std::string EXCEPTION_TRACK_NUMBER = "track_number_exception";
    std::string CONNECT_STATUS = "connect_status";
    std::string MARKER_INFO = "marker_info";
};


#endif