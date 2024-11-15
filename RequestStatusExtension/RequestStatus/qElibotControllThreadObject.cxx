#include "qElibotControllThreadObject.h"
#include "qElibotReceiveThreadObject.h"
void qElibotControllThreadObject::send_thread_cmd(QString cmd) {
    try{
    QStringList list1 = cmd.split(", ");
    if (list1.length() < 2) {
        return;
    }
    if (list1[0] != "Elibot") {
        return;
    }
    if (list1[1] == "SetGapMax") {
        if (list1.length() == 3)
            obj->gap_max = list1[2].toInt();
        return;
    }
    if (list1[1] == "Connect") {
        if(list1.length() == 4)
            connect(list1[2],list1[3]);
        return;
    }
    if (list1[1] == "DisConnect") {
        disconnect();
        return;
    }
    if (list1[1] == "Open") {
        open();
        return;
    }
    if (list1[1] == "MoveByJoint") {
        if (list1.length() == 9){
            QStringList poslist;
            poslist << list1[2] << list1[3] << list1[4] << list1[5] << list1[6] << list1[7];
            QString posstr = poslist.join(", ");
            move_by_joint(posstr, list1[8]);
        }
        return;
    }
    if (list1[1] == "Stop") {
        stop();
        return;
    }
    if (list1[1] == "Rotate") {
        if (list1.length() == 7) {
            rotate(list1[2].toStdString(), list1[3].toInt(), list1[4].toFloat(), list1[5].toFloat(), list1[6].toFloat());
        }
        return;
    }
    if (list1[1] == "SetTool") {
        if (list1.length() == 3) {
            set_tool_number(list1[2].toInt());
        }
        return;
    }
    if (list1[1] == "ClearAlarm") {
        clear_alarm();
        return;
    }
    if (list1[1] == "SetCollapseSensitivity") {
        set_collapse_sensitivity(list1[2].toInt());
        return;
    }
    if (list1[1] == "SetSpeed") {
        set_speed(list1[2].toInt());
        return;
    }
    }
    catch (const std::exception& e) {
        // 处理异常
        qDebug() << "catch exception2" << e.what();
    }
}

void qElibotControllThreadObject::set_speed(int value) {
    qDebug() << "Control Thread " << QThread::currentThreadId() << "set_speed" << value;
    json params, json_result;
    params["value"] = value;
    obj->conntro.sendCmd("setSpeed", params, 1);
}
void qElibotControllThreadObject::set_collapse_sensitivity(int value) {
    qDebug() << "Control Thread " << QThread::currentThreadId() << "setCollisionSensitivity" << value;
    json params, json_result;
    params["value"] = value;
    obj->conntro.sendCmd("setCollisionSensitivity", params, 1);
}

void qElibotControllThreadObject::clear_alarm() {
    qDebug() << "Control Thread " << QThread::currentThreadId() << " clear_alarm";
    json empty;
    //清除警报
    obj->conntro.sendCmd("clearAlarm", empty, 1);
    obj->conntro.sendCmd("resetCollisionState", empty, 1);
}

// 绕当前末端TCP点旋转，可以参考tcp方向或者base方向
std::string qElibotControllThreadObject::tcpRotate_compute(float p[], int toolorbase, float rx, float ry, float rz) {
    // 输入参考笛卡尔空间点，后续旋转rx,ry,rz为deg
    // float pp[6] = {p[0], p[1], p[2], p[3], p[4], p[5]}; 这里有问题，应该也转化为弧度
    float PI = 3.1415926;
    float pp[6] = { p[0], p[1], p[2], p[3] * PI / 180, p[4] * PI / 180, p[5] * PI / 180 };
    float rx_rad = rx * PI / 180;
    float ry_rad = ry * PI / 180;
    float rz_rad = rz * PI / 180;
    float out[6] = { 0, 0, 0, rx_rad, ry_rad, rz_rad };
    float p_tmp[6] = { 0, 0, 0, p[3] * PI / 180, p[4] * PI / 180, p[5] * PI / 180 };

    std::string result;
    std::string result_2;
    json json_result, params;
    if (toolorbase == 0) {
        // 绕当前tcp的方向转
        params["pose1"] = pp;
        params["pose2"] = out;
        json_result = obj->conntro.sendCmd("poseMul", params, 1);
        if (json_result == "" || json_result.dump() == "null") {
            return "";
        }
        for (int i = 0; i < 5; i++)
        {
            result += to_string(json_result["result"][i]);
            result += ',';
        }
        result += to_string(json_result["result"][5]);
        // qDebug() << result[0] <<"\t"<< result[1] <<"\t"<< result[2] <<"\t"<< result[3] <<"\t"<< result[4] <<"\t"<< result[5] <<"\t";
        std::cout << result;
        return result;

    }
    else if (toolorbase == 1) {
        // 绕着当前末端 参考base坐标系
        params["pose1"] = out;
        params["pose2"] = p_tmp;
        json_result = obj->conntro.sendCmd("poseMul", params, 1);
        if (json_result == "" || json_result.dump() == "null") {
            return "";
        }
        result_2 += std::to_string(p[0]);
        result_2 += ",";
        result_2 += std::to_string(p[1]);
        result_2 += ",";
        result_2 += std::to_string(p[2]);
        result_2 += ",";
        result_2 += to_string(json_result["result"][3]);
        result_2 += ",";
        result_2 += to_string(json_result["result"][4]);
        result_2 += ",";
        result_2 += to_string(json_result["result"][5]);
        // qDebug() << result_2[0]<<"\t"<< result_2[1]<<"\t"<< result_2[2]<<"\t"<< result_2[3]<<"\t"<< result_2[4]<<"\t"<< result_2[5]<<"\t";
        std::cout << result_2;
        return result_2;
    }
    else {
        // emit sendrotatemsg("Mistakes occur!");
        std::string result_3 = "";
        return result_3;
    }
}

void qElibotControllThreadObject::movebyLine(std::string targetpos, double speed) {
    // speed_type 值为0为直线速度，取值范围为[1-3000]，值为1时为旋转角速度，取值范围为[1-300]。
    std::vector<float>output_vec = obj->conntro.stringToVector(targetpos);
    double targetposDouble[6];
    // 将vector转为数组
    std::copy(output_vec.begin(), output_vec.end(), targetposDouble);

    json params, json_result;
    params["targetPos"] = targetposDouble;
    params["speed"] = speed;
    params["speed_type"] = 0;
    params["acc"] = 20;
    params["dec"] = 20;
    obj->conntro.sendCmd("moveByLine", params, 1);
}

void qElibotControllThreadObject::set_tool_number(int tool_num) {
    json params, json_result;
    params["tool_num"] = tool_num;
    json_result = obj->conntro.sendCmd("setAutoRunToolNumber", params, 1);
}

void qElibotControllThreadObject::rotate(std::string tcppos, int toolorbase, float rx, float ry, float rz) {
    std::vector<float>output_vec = obj->conntro.stringToVector(tcppos);
    float tcpposFloat[6];
    // 将vector转为数组
    std::copy(output_vec.begin(), output_vec.end(), tcpposFloat);

    std::string newpoint = tcpRotate_compute(tcpposFloat, toolorbase, rx, ry, rz);
    if (newpoint == "") {
        return;
    }
    json json_result, params;
    json_result = obj->conntro.inverseKinematic(newpoint, 1);
    std::string final_pose;
    for (int i = 0; i < 5; i++) {
        final_pose += to_string(json_result["result"][i]);
        final_pose += ",";
    }
    final_pose += to_string(json_result["result"][5]);
    movebyLine(final_pose, 30);
}

void qElibotControllThreadObject::move_by_joint(QString targetpos,QString speed) {
    json json_result;

    std::vector<float>output_vec = obj->conntro.stringToVector(targetpos.toStdString());
    double targetposFloat[6];
    // 将vector转为数组
    std::copy(output_vec.begin(), output_vec.end(), targetposFloat);

    obj->conntro.moveByJoint(targetposFloat, speed.toInt(), 20, 20);
}

void qElibotControllThreadObject::connect(QString ipaddress, QString port) {
    qDebug() << "Control Thread " << QThread::currentThreadId() << " connect";
    obj->conntro.connectEtController(ipaddress.toStdString(), port.toInt());
}

void qElibotControllThreadObject::disconnect() {
    qDebug() << "Control Thread " << QThread::currentThreadId() << " disconnect";
    obj->conntro.disconnectEtController();
}

void qElibotControllThreadObject::stop() {
    qDebug() << "Control Thread " << QThread::currentThreadId() << " stop";
    json json_result, params;
    obj->conntro.sendCmd("stop", params, 1);
}

void qElibotControllThreadObject::open() {
    qDebug() << "Control Thread " << QThread::currentThreadId() << " open";
   
    //获取同步状态
    json params2;
    json jsonStatus = obj->conntro.sendCmd("getMotorStatus", params2, 1);
    if (jsonStatus.dump() == "null") {
        return;
    }
    std::string strStatus = jsonStatus["result"];
    if (atoi(strStatus.c_str()) == 0) {
        //同步伺服编码器数据
        obj->conntro.sendCmd("syncMotorStatus", params2, 1);
        std::cout << "sync MotorStatus Over" << std::endl;
    }

    //#设置伺服使能状态
    json params3;
    params3["status"] = 1;
    obj->conntro.sendCmd("set_servo_status", params3, 1);
    return;
    //获取精确状态
    json rb_calib;
    rb_calib["addr"] = 472;
    int result1;
    int result2;
    nlohmann::json ro = obj->conntro.sendCmd("getVirtualOutput", rb_calib, 1);
    std::string virtualstatus = ro["result"];
    result1 = atoi(virtualstatus.c_str());
    // 0表示未校准 1 表示校准
    std::cout << "Accuracy State: " << result1 << "\n";

    if (result1 == 0) {
        //编码器零位校准
        obj->conntro.sendCmd("calibrate_encoder_zero_position", params2, 1);
        virtualstatus = obj->conntro.sendCmd("getVirtualOutput", rb_calib, 1)["result"];
        result2 = atoi(virtualstatus.c_str());

        std::cout << "Zero Check Finished!" << std::endl;
    }

}