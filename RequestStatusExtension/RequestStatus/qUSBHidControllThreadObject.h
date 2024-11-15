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

#ifndef __qSlicerRequestStatusModuleWidgetqUSBHidControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqUSBHidControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qControlThreadBaseObject.h>
#include "qUSBHidReceiveThreadObject.h"
#include "hidapi.h"
class qUSBHidControllThreadObject : public qControlThreadBaseObject
{
    Q_OBJECT
public slots:
    void send_thread_cmd(QString cmd);
public:
    void init(qUSBHidReceiveThreadObject* in_obj) { obj = in_obj; };
    void send_64bit_cmd(QString key, QStringList value, int gap);
    QString send_synchronize_cmd(QString cmd) { return ""; };
public:
    qUSBHidReceiveThreadObject* obj = nullptr;
    QString mainKey = "empty";
    unsigned char* get_64bit_cmd(QString key, QStringList valuelist);
    virtual void set_special_cmd(QString key,unsigned char* packet, QStringList valuelist) = 0;
};


#endif