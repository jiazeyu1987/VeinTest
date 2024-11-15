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

#ifndef __qSlicerRequestStatusModuleWidgetqNDIControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqNDIControllThreadObject_h

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

#include "SystemCRC.h"
#include "qNDIReceiveThreadObject.h"
#include "qControlThreadBaseObject.h"
#include "QFile.h"
#include "QTextStream.h"

class qNDIControllThreadObject : public qControlThreadBaseObject
{
    Q_OBJECT
public slots:
    void send_thread_cmd(QString cmd);
    void init(qNDIReceiveThreadObject* in_obj) { obj = in_obj; };
public:
    qNDIReceiveThreadObject* obj = nullptr;
	QString send_synchronize_cmd(QString cmd);
public:
	bool ndiSocketOpen(std::string myIPAddress);
    void loadTools();
    void loadSromToPort(std::string romFilePath, int portHandle);
    void initializeAndEnableTools();
    void SetLaserStatus(bool isOn);
    void SetLaserOn();
    void ndiTransformToMatrix(const double trans[8], double matrix[16]);
    void ndiAnglesFromMatrix(double outRotationAngles[3], const double rotationMatrix[16]);
    void ndiCoordsFromMatrix(double coords[3], const double matrix[16]);
    bool ndiSocketSleep(int milliseconds);
    int portHandleRequest();
    int Init();
    bool IsSetLaserOn = false;
    std::thread* setLaserThread = nullptr;
    
};


#endif