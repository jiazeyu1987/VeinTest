#include "qReceiveThreadBaseObject.h"
#include "QDateTime.h"
void qReceiveThreadBaseObject::OnTimerReceiveObjectInnerTick() {
    QElapsedTimer timer;
    timer.start();
    map_info["time_gap_elapsed"] = QString::number(gap_timer.elapsed()).toStdString() + " ms";
    try{
        OnReceiveObjectInnerTick();
    }
    catch (const std::exception& e) {
        map_info["exception"] = e.what();
        qDebug() << "std::exception ====================================" << e.what() << "===============================";
    }
    map_info["time_function_elapsed"] = QString::number(timer.nsecsElapsed()).toStdString() + " ns";
    map_info["timestamp"] = QString::number(QDateTime::currentDateTime().toSecsSinceEpoch()).toStdString();
    ToInfoString();
    //qDebug() << metaObject()->className() << " finished " ;
}
 
void qReceiveThreadBaseObject::OnReceiveObjectTick() {
    mutex.lock();
    try {
        gap_index += 1;
        if (result != "") {
            mutex.unlock();
            return;
        }
        if (gap_index > gap_max - 1)
        {
            gap_index = 0;
            OnTimerReceiveObjectInnerTick();
            emit tick_finished();
            //qDebug() << metaObject()->className()<<" finished "<< gap_max;
        }
    }
    catch (const std::exception& e) {
        // �����쳣
        qDebug() << "catch exception3:" << e.what();
    }
    mutex.unlock();
}

std::string qReceiveThreadBaseObject::ToInfoString() {
    result = "";
    for (const auto& pair : map_info) {
        if (!result.empty()) {
            result += "*V* ";
        }
        result += pair.first + "*U* " + pair.second;
    }
    return result;
}

std::string qReceiveThreadBaseObject::fetch_result() {
    auto tmp = result;
    result = "";
    return tmp;
};

void qReceiveThreadBaseObject::ClearData() {
    map_info.clear();
}