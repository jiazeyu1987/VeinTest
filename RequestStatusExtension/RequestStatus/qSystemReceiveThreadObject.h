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

#ifndef __qSlicerRequestStatusModuleWidgetqSystemReceiveThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqSystemReceiveThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
#include <windows.h>
#include <iostream>
#include <tlhelp32.h>
#include <psapi.h>
#include <JQLibrary/jqcpumonitor.h>
class qSystemReceiveThreadObject : public qReceiveThreadBaseObject
{
    Q_OBJECT
public slots:
    void OnReceiveObjectInnerTick();
public:
    qSystemReceiveThreadObject();
    ~qSystemReceiveThreadObject();
private:
    void findProcessUsage(const char* processName);
    void findCPUUsage(const char* processName);
};


#endif