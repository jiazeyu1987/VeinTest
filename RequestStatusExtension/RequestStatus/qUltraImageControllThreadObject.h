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

#ifndef __qSlicerRequestStatusModuleWidgetqUltraImageControllThreadObject_h
#define __qSlicerRequestStatusModuleWidgetqUltraImageControllThreadObject_h

// Slicer includes
#include <QObject>
#include <QDebug>
#include <QThread>

#include <qControlThreadBaseObject.h>
#include "qUltraImageReceiveThreadObject.h"
#include <UltraSDK/Target/include/UltraSDK.h>
class qUltraImageControllThreadObject : public qControlThreadBaseObject
{
	Q_OBJECT
public slots:
	void send_thread_cmd(QString cmd);
public:
	void init(qUltraImageReceiveThreadObject* in_obj) { obj = in_obj; };

public:
	qUltraImageReceiveThreadObject* obj = nullptr;
	QString send_synchronize_cmd(QString cmd);
private:
};

#endif