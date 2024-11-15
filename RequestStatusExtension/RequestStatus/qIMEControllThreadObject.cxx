#include "qIMEControllThreadObject.h"

QString qIMEControllThreadObject::send_synchronize_cmd(QString cmd) {
  QString res;
  QStringList list1 = cmd.split(", ");
  if (list1[1] == "GetMarkerInfo") {
    return obj->track();
  }
  return res;
} 

void qIMEControllThreadObject::send_thread_cmd(QString cmd) {
    // qDebug() << "Receive Command IME:" << cmd;
    QStringList list1 = cmd.split(", ");
    if (list1.length() < 2) {
        return;
    }
    if (list1[0] != "IME") {
        return;
    }
    if (list1[1] == "SetGapMax") {
        if (list1.length() == 3) {
            obj->gap_max = list1[2].toInt();
            qDebug() << "Set gap max ime:" << obj->gap_max;
        }
            
        return;
    }
    else if (list1[1] == "Connect") {
        qDebug() << "Do ConnectNDI:"<< list1.length();
        if((list1.length()) == 3)
        {
            vInitalCamera();
            vConnectCamera(list1[2]);
            
        }
    }
    else {
        qDebug() << "Unsupport key:" << list1[1];
    }
}

void qIMEControllThreadObject::vInitalCamera()
{
    E_ReturnValue rlt = Aim_API_Initial(obj->m_aimHandle);
    if (rlt != AIMOOE_OK)
    {
        qDebug() << "Aimooe API init failed.";
    }
    else
    {   
        qDebug() << "Aimooe API init successfully.";
    }

    return;
}

void qIMEControllThreadObject::vConnectCamera(QString ip)
{
    auto ipintlist = ip.split('.');
    if(ipintlist.length()==4){
        qDebug() << "Connect IME With IP:" << ip;
        Aim_SetEthernetConnectIP(obj->m_aimHandle, ipintlist[0].toInt(), ipintlist[1].toInt(), ipintlist[2].toInt(), ipintlist[3].toInt());
        E_ReturnValue rlt = Aim_ConnectDevice(obj->m_aimHandle, E_Interface::I_ETHERNET, obj->m_PosDataPara);
        obj->m_hardware_verion = QString(obj->m_PosDataPara.hardwareinfo).toStdString();
        Aim_SetAcquireData(obj->m_aimHandle, E_Interface::I_ETHERNET, E_DataType::DT_NONE);
    }
    return;
}
