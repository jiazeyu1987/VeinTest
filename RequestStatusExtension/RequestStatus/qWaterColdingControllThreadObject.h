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

#ifndef __qSlicerRequestStatusModuleWidgetqWaterColdingControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqWaterColdingControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qUSBHidControllThreadObject.h>


class qWaterColdingControllThreadObject : public qUSBHidControllThreadObject
{
    Q_OBJECT
public:
    qWaterColdingControllThreadObject::qWaterColdingControllThreadObject() {
        mainKey = "WaterControl";
    }
public:

    void set_special_cmd(QString key, unsigned char* packet, QStringList valuelist);
};


#endif