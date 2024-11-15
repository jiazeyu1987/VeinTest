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

#ifndef __qSlicerRequestStatusModuleWidgetqUSBHidReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqUSBHidReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
#include <QMutex>
#include "hidapi.h"
#include "QFile.h"
class PackageData {
public :
    QString key;
    unsigned char* data;
    int gap;
    int timeout;
    bool show_log;
    int length = 65;
    PackageData::PackageData(QString key1, unsigned char* data1, int gap1,int timeout1,bool show_log1) {
        key = key1;
        data = data1;
        gap = gap1;
        timeout = timeout1;
        show_log = show_log1;
    }
};

class qUSBHidReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
    void add_queued_cmd(QString key, unsigned char* data, int gap, int timeout, bool showlog);
public:
    qUSBHidReceiveThreadObject();
    ~qUSBHidReceiveThreadObject();
public:
    hid_device* handle = nullptr;
    hid_device_info* devs = nullptr;
    int read_timeout = 50;
    QList<PackageData*> packagelist;
    void HID_API_EXPORT HID_API_CALL loop_write_and_read(hid_device* dev);

protected:
    void GetHidData();
    void GetSoftwareStatus();
    void GetHeartBeat();
private:
    int  HID_API_EXPORT HID_API_CALL write_to_usb(hid_device* dev, const unsigned char* data, size_t length, bool show_log);
    QString HID_API_EXPORT HID_API_CALL read_from_usb(hid_device* dev, unsigned char* data, size_t length, int milliseconds, bool show_log);
    QString HID_API_EXPORT HID_API_CALL write_and_read(hid_device* dev, unsigned char* data, size_t length, int milliseconds, bool show_log, int gap = 10);
    void HID_API_EXPORT HID_API_CALL read_empty(hid_device* dev);
    void analyse_result(PackageData* pd, QString  res);
public:
    int status = 0;
    QFile* logfile = nullptr;
    QTextStream* out = nullptr;

};


#endif