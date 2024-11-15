#include "qElibotReceiveThreadObject.h"


void qElibotReceiveThreadObject::OnReceiveObjectInnerTick() {
    GetRobotStatus();
    GetCollapseSensitivity();
    GetCollapseState();
    GetToolNumber();
    GetVirtualOutput();
    GetFlangePos();
    GetTcpPos();
    GetSpeed();
}



void qElibotReceiveThreadObject::GetSpeed() {
    json params, json_result;
    json_result = conntro.sendCmd("getSpeed", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    std::string virstate = json_result["result"];
    map_info[SPEED] = virstate;
}

void qElibotReceiveThreadObject::GetCollapseSensitivity() {
    json params, json_result;
    json_result = conntro.sendCmd("getCollisionSensitivity", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    std::string virstate = json_result["result"];
    map_info[COLLAPSE_SENSITIVITY] = virstate;
} 

void qElibotReceiveThreadObject::GetCollapseState() {
    json params, json_result;
    json_result = conntro.sendCmd("getCollisionState", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    std::string virstate = json_result["result"];
    map_info[COLLAPSE_STATE] = virstate;
}

void qElibotReceiveThreadObject::GetToolNumber() {
    json params, json_result;
    json_result = conntro.sendCmd("getToolNumber", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    std::string virstate = json_result["result"];
    map_info[TOOL_NUMBER] = virstate;
}

void qElibotReceiveThreadObject::GetTcpPos() {
    json params, json_result;
    params["coordinate_num"] = -1;
    params["tool_num"] = -1;
    params["unit_type"] = 0;
    json_result = conntro.sendCmd("get_tcp_pose", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    //此处返回的是Pose xyz下的 类型是一个array[6]
    std::string msg = "";
    std::string temploc;
    for (int j = 0; j < 5; j++) {
        temploc = to_string(json_result["result"][j]);
        std::cout << temploc << "\t";
        msg = msg + temploc;
        msg = msg + ",";
    }
    msg += to_string(json_result["result"][5]);
    map_info[TCP_POS] = msg;
}

void qElibotReceiveThreadObject::GetVirtualOutput() {
    json params;
    params["addr"] = 473;
    json json_state = conntro.sendCmd("getVirtualOutput", params, 1);
    if(json_state == "" || json_state.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }

    std::string virstate = json_state["result"];
    int rb_state = atoi(virstate.c_str());
    map_info[VIRTUAL_OUTPUT] = rb_state;
}

void qElibotReceiveThreadObject::GetRobotStatus() {
    json params;
    json result;
    std::string cmd = "getRobotState";

    result = conntro.sendCmd(cmd, params, 1);

    if (result == "" || result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    std::string a = result["result"];
    //停止状态 0，暂停状态 1，急停状态 2，运行状态 3，报警状态 4，碰撞状态 5
    map_info[CONNECT_STATUS] =a;
}

void qElibotReceiveThreadObject::GetFlangePos() {
    json json_result, params;
    params["unit_type"] = 0;   //此处默认函数返回的类型为角度 弧度则需改为1
    json_result = conntro.sendCmd("get_base_flange_pose", params, 1);
    if (json_result == "" || json_result.dump() == "null") {
        map_info[CONNECT_STATUS] = "-1";
        return;
    }
    //此处返回的是Pose xyz下的 类型是一个array[6]
    std::string msg = "";
    std::string temploc;
    for (int j = 0; j < 5; j++) {
        temploc = to_string(json_result["result"][j]);
        msg = msg + temploc;
        if (j == 5)
            break;
        msg = msg + ",";
    }
    msg += to_string(json_result["result"][5]);
    map_info[FLANGE_POS] = msg;
}
