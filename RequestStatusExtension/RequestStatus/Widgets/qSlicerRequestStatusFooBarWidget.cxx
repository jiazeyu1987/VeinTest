/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerRequestStatusFooBarWidget.h"
#include "ui_qSlicerRequestStatusFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_RequestStatus
class qSlicerRequestStatusFooBarWidgetPrivate
  : public Ui_qSlicerRequestStatusFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerRequestStatusFooBarWidget);
protected:
  qSlicerRequestStatusFooBarWidget* const q_ptr;

public:
  qSlicerRequestStatusFooBarWidgetPrivate(
    qSlicerRequestStatusFooBarWidget& object);
  virtual void setupUi(qSlicerRequestStatusFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerRequestStatusFooBarWidgetPrivate
::qSlicerRequestStatusFooBarWidgetPrivate(
  qSlicerRequestStatusFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerRequestStatusFooBarWidgetPrivate
::setupUi(qSlicerRequestStatusFooBarWidget* widget)
{
  this->Ui_qSlicerRequestStatusFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerRequestStatusFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerRequestStatusFooBarWidget
::qSlicerRequestStatusFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerRequestStatusFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerRequestStatusFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerRequestStatusFooBarWidget
::~qSlicerRequestStatusFooBarWidget()
{
}
