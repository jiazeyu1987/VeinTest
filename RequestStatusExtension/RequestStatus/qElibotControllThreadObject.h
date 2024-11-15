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

#ifndef __qSlicerRequestStatusModuleWidgetqElibotControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqElibotControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>

#include <qControlThreadBaseObject.h>
#include "qElibotReceiveThreadObject.h"

class qElibotControllThreadObject : public qControlThreadBaseObject
{
    Q_OBJECT
public slots:
    void send_thread_cmd(QString cmd);
public:
    void init(qElibotReceiveThreadObject* in_obj) { obj = in_obj; };
public:
    qElibotReceiveThreadObject* obj = nullptr;
    QString send_synchronize_cmd(QString cmd) { return ""; };
private:
    void connect(QString ip,QString port);
    void disconnect();
    void open();
    void stop();
    void clear_alarm();
    void set_collapse_sensitivity(int value);
    void set_speed(int value);
    void move_by_joint(QString targetpos, QString speed);
    void rotate(std::string tcppos, int toolorbase, float rx, float ry, float rz);
    void set_tool_number(int tool_num);
    std::string tcpRotate_compute(float p[], int toolorbase, float rx, float ry, float rz);
    void movebyLine(std::string targetpos, double speed);
};


#endif