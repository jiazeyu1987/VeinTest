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

#ifndef __qSlicerRequestStatusModuleWidgetqReceiveThreadBaseObject_h
#define __qSlicerRequestStatusModuleWidgetqReceiveThreadBaseObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include "QMutex.h"
class qReceiveThreadBaseObject : public QObject
{
    Q_OBJECT
protected :
    std::string result = "";
    QMutex mutex;
    QElapsedTimer gap_timer;
public:
    int gap_max = 33;
    int gap_index = 0;
    qReceiveThreadBaseObject::qReceiveThreadBaseObject() {}
    qReceiveThreadBaseObject::~qReceiveThreadBaseObject() {}
    std::map<std::string, std::string> map_info;
    virtual std::string fetch_result();
    virtual std::string ToInfoString();
    virtual void ClearData();
signals:
    void tick_finished();
public slots:
    void OnReceiveObjectTick();
    virtual void OnReceiveObjectInnerTick() = 0;
    void OnTimerReceiveObjectInnerTick();
};



#endif