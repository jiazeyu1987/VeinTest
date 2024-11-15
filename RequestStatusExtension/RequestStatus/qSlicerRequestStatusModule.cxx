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

// RequestStatus Logic includes
#include <vtkSlicerRequestStatusLogic.h>

// RequestStatus includes
#include "qSlicerRequestStatusModule.h"
#include "qSlicerRequestStatusModuleWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerRequestStatusModulePrivate
{
public:
  qSlicerRequestStatusModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerRequestStatusModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerRequestStatusModulePrivate::qSlicerRequestStatusModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerRequestStatusModule methods

//-----------------------------------------------------------------------------
qSlicerRequestStatusModule::qSlicerRequestStatusModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerRequestStatusModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerRequestStatusModule::~qSlicerRequestStatusModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerRequestStatusModule::helpText() const
{
  return "This is a loadable module that can be bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerRequestStatusModule::acknowledgementText() const
{
  return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
}

//-----------------------------------------------------------------------------
QStringList qSlicerRequestStatusModule::contributors() const
{
  QStringList moduleContributors;
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerRequestStatusModule::icon() const
{
  return QIcon(":/Icons/RequestStatus.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerRequestStatusModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerRequestStatusModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerRequestStatusModule::setup()
{
	this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation* qSlicerRequestStatusModule
::createWidgetRepresentation()
{
  return new qSlicerRequestStatusModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerRequestStatusModule::createLogic()
{
  return vtkSlicerRequestStatusLogic::New();
}
