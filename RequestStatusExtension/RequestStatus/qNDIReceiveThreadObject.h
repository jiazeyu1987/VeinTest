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

#ifndef __qSlicerRequestStatusModuleWidgetqNDIReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqNDIReceiveThreadObject_h

#include "qReceiveThreadBaseObject.h"
#pragma comment(lib, "Ws2_32.lib")
#include <winsock2.h> // for Windows Socket API (WSA)
#include <ws2tcpip.h> // for getaddrinfo() etc...
#include <stdint.h>
#include <string>
#include <vector>
#include <iostream>
#include <thread>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <io.h>

#include "QTextStream.h"
#include "SystemCRC.h"
#include "QMutex.h"
#include "QFile.h"
//1. ����ɨ��
//2. �ر�ɨ��
//3. ����˫Ŀ���
//4. ���������������������ϵ�ȣ�
//5. ��ȡ���з����򹤾ߵ�λ����Ϣ�Ϳɼ���Ϣ
//6. ����˫Ŀ�����IP��ַ�Ͷ˿ںš�


enum TrackingTargetStatus { NDI_OKAY, NDI_MISSING, NDI_DISABLED };

enum TrackingTargetType
{
    None,
    T339,
    T340,
    T449
};

struct TrackingTarget
{
    int toolID;
    TrackingTargetType  toolType;
    TrackingTargetStatus toolStatus;
    std::string ROMPath;
    double TransformData[8];
};


struct Vector3
{
    double x;
    double y;
    double z;
};

struct TrackingMark
{
    TrackingTargetType belongToTool;
    Vector3 position;
};

struct ResponseValue
{
    std::string response;
    int errorCode;
};

class qNDIReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
private:
    std::string EXCEPTION_TRACK = "track_exception";
    std::string EXCEPTION_TRACK_NUMBER = "track_number_exception";
    std::string CONNECT_STATUS = "connect_status";
    std::string MARKER_INFO = "marker_info";

public:
    qNDIReceiveThreadObject();
    ~qNDIReceiveThreadObject();
private:
    int sendndiCommand(std::string command,bool showlog);
    TrackingTargetType FindMarkByDeviceID(int portHandle);
    int getErrorCodeFromResponse(std::string response);
    void RetrieveToolsTransformation(std::string reply);
    std::string readResponse(bool showlog);
    uint8_t count_bits_1(uint32_t value);
    void getTrackingData();
    SystemCRC* crcValidator = nullptr;
    static const char CR = '\r';
    TrackingTarget* FindTargetByDeviceID(int portHandle);
public:
    std::vector<TrackingMark> qNDIReceiveThreadObject::getTrackingMarker();
    int stringToInt(std::string input);
    std::string intToHexString(int input, int width);
    SOCKET ndiSocket = NULL;
    bool isConnected = false;
    bool isTracking = false;
    QString base_path;
    std::vector<TrackingTarget> trackingTragets;
    QFile* logfile = nullptr;
    QTextStream* out = nullptr;
    ResponseValue  WriteAndRead(std::string command,bool showlog=true);
    bool ndiSocketClose();
    QString cutString(const QString& originalString);
    QString track();
};


#endif