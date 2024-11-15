#include "qRegisterControllThreadObject.h"
#include "qRegisterReceiveThreadObject.h"

QString qRegisterControllThreadObject::send_synchronize_cmd(QString cmd) {
  QString res;
  QStringList list1 = cmd.split(", ");
  if (list1[1] == "GetRegistrationErrMatrix") {
    return obj->registrationImp();
  }
  return res;
} 

void qRegisterControllThreadObject::send_thread_cmd(QString cmd) {
    QStringList list1 = cmd.split(", ");
    if (list1.length() < 2) {
        return;
    }
    if (list1[0] != "Register") {
        return;
    }
    if (list1[1] == "SetGapMax") {
        if (list1.length() == 3)
        {
            obj->gap_max = list1[2].toInt();
        }
        return;
    }
    if (list1[1] == "Init") {
        if ((list1.length()) == 3)
        {
            init(list1[2].toInt());
        }
        qDebug() << "Register Init" << list1.length();
    }
    if (list1[1] == "SetCtMarkers") {
        if ((list1.length()) == 3)
        {
            QList valuelist = list1[2].split("&");
            if (valuelist.length() % 3 != 0) {
                qDebug() << "error valuelist length" << valuelist.length();
                return;
            }
            if (valuelist.length() == 0) {
                qDebug() << "error valuelist length2" << valuelist.length();
                return;
            }
            int num = valuelist.length() / 3;
            std::vector<std::array<double, 3>> points_all;
            for (int i = 0; i < num; i++) {
                std::array<double, 3> myArray = { valuelist[i * 3].toDouble() , valuelist[i * 3 + 1].toDouble() , valuelist[i * 3 + 2].toDouble() };
                points_all.push_back(myArray);
            }
            setCtMarkers(points_all);
        }
        qDebug() << "Register Init" << list1.length();
    }
    if (list1[1] == "SetInputMarkers") {
        if ((list1.length()) == 3)
        {
            QList valuelist = list1[2].split("&");
            if (valuelist.length() % 3 != 0) {
                qDebug() << "error valuelist length" << valuelist.length();
                return;
            }
            if (valuelist.length() == 0) {
                qDebug() << "error valuelist length2" << valuelist.length();
                return;
            }
            int num = valuelist.length() / 3;
            std::vector<std::array<double, 3>> points_all;
            for (int i = 0; i < num; i++) {
                std::array<double, 3> myArray = { valuelist[i * 3].toDouble() , valuelist[i * 3 + 1].toDouble() , valuelist[i * 3 + 2].toDouble() };
                points_all.push_back(myArray);
            }
            setInputMarkers(points_all);
        }
        // qDebug() << "Register Init" << list1.length();
    }
    // qDebug() << "qRegisterControllThreadObject::send_thread_cmd";
}

void qRegisterControllThreadObject::init(size_t marker_num){
    obj->m_npoints = marker_num;
    obj->m_points_ct->SetNumberOfPoints(obj->m_npoints);
    obj->m_points_input->SetNumberOfPoints(obj->m_npoints);
    obj->m_points_reg->SetNumberOfPoints(obj->m_npoints);
}

int32_t qRegisterControllThreadObject::setCtMarkers(const std::vector<std::array<double, 3>>& points) {
    if (points.size() != obj->m_npoints) {
        qDebug() << "CT marker error" << obj->m_npoints << " " << points.size();
        return -1;
    }
    for (size_t idx = 0; idx < obj->m_npoints; idx++) {
        obj->m_points_ct->SetPoint(idx, points[idx].data());
    }
    qDebug() << "setCtMarkers Done";
    return 0;
}

int32_t qRegisterControllThreadObject::setInputMarkers(const std::vector<std::array<double, 3>>& points) {
    if (points.size() != obj->m_npoints) {
        qDebug() << "input marker error" << obj->m_npoints << " " << points.size();
        return -1;
    }
    for (size_t idx = 0; idx < obj->m_npoints; idx++) {
        obj->m_points_input->SetPoint(idx, points[idx].data());
    }
    // qDebug() << "setInputMarkers Done";
    return 0;
}



