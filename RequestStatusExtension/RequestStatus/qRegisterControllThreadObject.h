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

#ifndef __qSlicerRequestStatusModuleWidgetqRegisterControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqRegisterControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qControlThreadBaseObject.h>
#include "qRegisterReceiveThreadObject.h"
#include "vtkLandmarkTransform.h"
#include "vtkMath.h"
#include "vtkMatrix4x4.h"
#include "vtkNew.h"
#include "vtkPoints.h"
#include "vtkTransform.h"
class vtkPoints;
class qRegisterControllThreadObject : public qControlThreadBaseObject
{
    Q_OBJECT
public slots:
    void send_thread_cmd(QString cmd);
public:
    void init(qRegisterReceiveThreadObject* in_obj) { obj = in_obj; };
    QString send_synchronize_cmd(QString cmd);
public:
    qRegisterReceiveThreadObject* obj = nullptr;
private:
    void init(size_t marker_num);
    int32_t setCtMarkers(const std::vector<std::array<double, 3>>& points);
    int32_t setInputMarkers(const std::vector<std::array<double, 3>>& points);
    void updateMarkers();
    void registrationImp();
};


#endif