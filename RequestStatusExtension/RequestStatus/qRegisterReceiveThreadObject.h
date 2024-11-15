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

#ifndef __qSlicerRequestStatusModuleWidgetqRegisterReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqRegisterReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
#include "vtkNew.h"
#include <vector>
#include <array>
#include "vtkLandmarkTransform.h"
#include "vtkMath.h"
#include "vtkMatrix4x4.h"
#include "vtkPoints.h"
#include "vtkTransform.h"
#include "QMutex.h"
#include <deque>
#include "vtkPoints.h"
#include "QMutex.h"
class qRegisterReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
public:
    qRegisterReceiveThreadObject();
    ~qRegisterReceiveThreadObject();
public:
    //For Register Statics
    vtkNew<vtkPoints> m_points_ct, m_points_input, m_points_reg;
    size_t m_npoints;
    QString registrationImp();
private:
    void updateMarkers();
    std::string MARKER_INFO = "marker_info";
};


#endif