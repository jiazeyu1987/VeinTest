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

#ifndef __qSlicerRequestStatusModuleWidgetqControlThreadBaseObject_h
#define __qSlicerRequestStatusModuleWidgetqControlThreadBaseObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>
#include <qReceiveThreadBaseObject.h>
class qControlThreadBaseObject : public QObject
{
    Q_OBJECT
public slots:
    virtual QString send_synchronize_cmd(QString cmd) = 0;
    virtual void send_thread_cmd(QString cmd) = 0;
public:
};


#endif