#include "qNDIReceiveThreadObject.h"

qNDIReceiveThreadObject::qNDIReceiveThreadObject()
{
    crcValidator = new SystemCRC();
}

qNDIReceiveThreadObject::~qNDIReceiveThreadObject()
{
    delete crcValidator;
    crcValidator = nullptr;
    if (out) {
        logfile->close();
    }
}


void qNDIReceiveThreadObject::OnReceiveObjectInnerTick() {
    this->track();
    // ToInfoString();
}

QString qNDIReceiveThreadObject::track()
{
    if (isTracking) {
        std::vector<TrackingMark> marksPos = getTrackingMarker();
        QString qstr("");
        for (std::vector<TrackingMark>::iterator iter = marksPos.begin(); iter != marksPos.end(); iter++)
        {
            QString qstr1("");
            //std::cout << (*iter).belongToTool << " : " << (*iter).position.x << "," << (*iter).position.y << "," << (*iter).position.z << std::endl;
            qstr1 = qstr1 + "conf:" + QString::number((*iter).belongToTool, 'f', 1) + " ";
            qstr1 = qstr1 + "x:" + QString::number((*iter).position.x, 'f', 3) + " ";
            qstr1 = qstr1 + "y:" + QString::number((*iter).position.y, 'f', 3) + " ";
            qstr1 = qstr1 + "z:" + QString::number((*iter).position.z, 'f', 3) + " ";
            qstr = qstr + " " + qstr1;
        }
        map_info[MARKER_INFO] = qstr.toStdString();
        return qstr;
    }
    return "";
}

std::string qNDIReceiveThreadObject::intToHexString(int input, int width)
{
    std::stringstream convert;
    convert << std::hex << std::setfill('0');
    convert << std::setw(width) << input;
    return convert.str();
}

int qNDIReceiveThreadObject::sendndiCommand(std::string command, bool showlog)
{
    if (showlog)
    std::cout << "Sending command: " << command << " ..." << std::endl;
    if (out)
    (*out)<< "Sending command: " << QString::fromStdString(command) << Qt::endl;;
    // Add CR character to command and write the command to the socket
    command += CR;
    return send(ndiSocket, command.c_str(), (int)command.length(), 0);
}

ResponseValue  qNDIReceiveThreadObject::WriteAndRead(std::string command,bool showlog) {
    // mutex.lock();
    ResponseValue rv;
    try{
        sendndiCommand(command, showlog);
        std::string response = readResponse(showlog);
        int errorCode = getErrorCodeFromResponse(response);
        rv.response = response;
        rv.errorCode = errorCode;
        if (response == "ERROR: Reply timeout.") {
            rv.errorCode = -1025;
            isConnected = false;
        }
    }
    catch (std::exception& e) {
        // mutex.unlock();
        qDebug() << "Got Exception in NDI:" << e.what();
    }
    if (rv.errorCode == 0)
    {
        // mutex.unlock();
        return rv;
    }
    else
    {
        std::cout << "Error From NDI:" << rv.errorCode << std::endl;
        // mutex.unlock();
        return rv;
    }
}

std::string qNDIReceiveThreadObject::readResponse(bool showlog)
{
    std::string response = std::string("");
    char lastChar = '\0';
    // Read from the device until we encounter a terminating carriage return (CR)
    while (lastChar != CR)
    {
        int numBytes = recv(ndiSocket, &lastChar, 1, MSG_WAITALL);
        if (numBytes <= 0)
        {
            // Timeout!
            std::cerr << "ERROR: Reply timeout." << std::endl;
            return "ERROR: Reply timeout.";
        }
        response += lastChar;
    }

    // Trim trailing CR and verify the CRC16
    response.erase(response.length() - 1); // strip CR (1 char)
    unsigned int replyCRC16 = (unsigned int)stringToInt(response.substr(response.length() - 4, 4));
    response.erase(response.length() - 4, 4); // strip CRC16 (4 chars)
    if (crcValidator->calculateCRC16(response.c_str(), (int)response.length()) != replyCRC16)
    {
        std::cout << "CRC16 failed!" << std::endl;
        return "";
    }
    if(showlog)
    std::cout << "<<" << response << std::endl;
    if (out)
        (*out) << "Get Respone: " << cutString(QString::fromStdString(response)) << Qt::endl;;
    // Return whatever string the device responded with
    return response;
}

QString qNDIReceiveThreadObject::cutString(const QString& originalString) {
    if (originalString.length() > 20) {
        return originalString.left(20);
    }
    else {
        return originalString;
    }
}

TrackingTargetType qNDIReceiveThreadObject::FindMarkByDeviceID(int portHandle)
{
    for (std::vector<TrackingTarget>::iterator iter = trackingTragets.begin(); iter != trackingTragets.end(); iter++)
    {
        if ((*iter).toolID == portHandle)
        {
            return (*iter).toolType;
        }
    }
    return TrackingTargetType::None;
}


int qNDIReceiveThreadObject::getErrorCodeFromResponse(std::string response)
{
    int errorCode = 0;
    if (response.substr(0, 5).compare("ERROR") == 0)
    {
        errorCode = stringToInt(response.substr(5, 2));
    }
    else if (response.substr(0, 7).compare("WARNING") == 0)
    {
        errorCode = stringToInt(response.substr(7, 2)) + 1000;
    }

    return errorCode * -1;
}



std::vector<TrackingMark> qNDIReceiveThreadObject::getTrackingMarker()
{
    if (!isConnected) return std::vector<TrackingMark>();
    // Send the TX command
    std::string command = std::string("TX ").append(intToHexString(0x1008, 4));
    /*sendndiCommand(command);
    std::string reply = readResponse();*/
    auto rv = WriteAndRead(command,false);
    if (rv.response == "") return std::vector<TrackingMark>();
    if (rv.errorCode < 0)
    {
        isConnected = false;
        isTracking = false;
        map_info["connect_status"] = "0";
        return std::vector<TrackingMark>();
    }
    //std::cout << "TrackingDataTX: " << rv.response << std::endl;

    int numPortHandles = stringToInt(rv.response.substr(0, 2));
    int startIndex = 2;
    std::vector<TrackingMark> marksPos;
    for (int i = 0; i < numPortHandles; i++)
    {
        int endIndex = rv.response.find('\n', startIndex);
        int numOfChars = endIndex - startIndex + 1;
        std::string theIDinDevice = rv.response.substr(startIndex, 2);
        TrackingTargetType trackingMarkType = FindMarkByDeviceID(std::stoi(theIDinDevice));

        startIndex += 2;
        int numofMarks = stringToInt(rv.response.substr(startIndex, 2));
        startIndex += 2;
        int replaySize = std::ceil(numofMarks / 4.0);
        int numofOutofVolume = stringToInt(rv.response.substr(startIndex, replaySize));
        int numofMissMark = count_bits_1(numofOutofVolume);
        startIndex += replaySize;

        for (int j = 0; j < numofMarks - numofMissMark; j++)
        {
            double Tx = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            double Ty = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            double Tz = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            Vector3 mark = { Tx ,Ty,Tz };

            TrackingMark trackingMark;
            trackingMark.belongToTool = trackingMarkType;
            trackingMark.position = mark;
            marksPos.push_back(trackingMark);
        }
        startIndex = endIndex + 1;
    }

    int numofMarks = stringToInt(rv.response.substr(startIndex, 2));
    startIndex += 2;
    int replaySize = std::ceil(numofMarks / 4.0);
    int numofOutofVolume = stringToInt(rv.response.substr(startIndex, replaySize));
    int numofMissMark = count_bits_1(numofOutofVolume);
    startIndex += replaySize;

    for (int j = 0; j < numofMarks - numofMissMark; j++)
    {
        double Tx = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
        startIndex += 7;
        double Ty = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
        startIndex += 7;
        double Tz = std::stod(rv.response.substr(startIndex, 7).c_str()) * 0.01;
        startIndex += 7;
        Vector3 mark = { Tx ,Ty,Tz };

        TrackingMark trackingMark;
        trackingMark.belongToTool = TrackingTargetType::None;
        trackingMark.position = mark;
        marksPos.push_back(trackingMark);
    }
    return marksPos;
}

int qNDIReceiveThreadObject::stringToInt(std::string input)
{
    int retVal = 0;
    std::stringstream convert(input);
    convert << std::hex;
    convert >> retVal;
    return retVal;
}

uint8_t qNDIReceiveThreadObject::count_bits_1(uint32_t value)
{
    uint8_t count = 0, i = 0;

    while (value)
    {
        if (value & 0x01)
        {
            count++;
        }
        value >>= 1;
    }
    return count;
}

void qNDIReceiveThreadObject::getTrackingData()
{
    if (!isConnected) return;
    //while (!IsThreadStop)
    {
        // Send the TX command
        std::string command = std::string("TX ").append(intToHexString(0x0001, 4));
        /*sendndiCommand(command);
        std::string trackInfo = readResponse();*/
        auto rv = WriteAndRead(command);
        if (rv.response == "") return;
        RetrieveToolsTransformation(rv.response);
        //ndiSocketSleep(20);
    }
}

TrackingTarget* qNDIReceiveThreadObject::FindTargetByDeviceID(int portHandle)
{
    for (std::vector<TrackingTarget>::iterator iter = trackingTragets.begin(); iter != trackingTragets.end(); iter++)
    {
        if ((*iter).toolID == portHandle)
        {
            return &(*iter);
        }
    }
    return nullptr;
}

void qNDIReceiveThreadObject::RetrieveToolsTransformation(std::string reply)
{
    int numPortHandles = stringToInt(reply.substr(0, 2));
    int startIndex = 2;
    for (int i = 0; i < numPortHandles; i++)
    {
        int endIndex = reply.find('\n', startIndex);
        int numOfChars = endIndex - startIndex + 1;
        std::string theIDinDevice = reply.substr(startIndex, 2);
        TrackingTarget* trackingTraget = FindTargetByDeviceID(std::stoi(theIDinDevice));
        double transform[8] = { 0,0,0,0,0,0,0,0 };

        startIndex += 2;
        if (numOfChars != 70)
        {
            if (reply.substr(startIndex, 1) == "D")
            {
                trackingTraget->toolStatus = TrackingTargetStatus::NDI_DISABLED;
                startIndex = endIndex + 1;
                continue;
            }
            else if (reply.substr(startIndex, 1) == "M")
            {
                trackingTraget->toolStatus = TrackingTargetStatus::NDI_MISSING;
                startIndex = endIndex + 1;
                continue;
            }
        }
        else
        {
            transform[0] = std::stod(reply.substr(startIndex, 6).c_str()) * 0.0001;
            startIndex += 6;
            transform[1] = std::stod(reply.substr(startIndex, 6).c_str()) * 0.0001;
            startIndex += 6;
            transform[2] = std::stod(reply.substr(startIndex, 6).c_str()) * 0.0001;
            startIndex += 6;
            transform[3] = std::stod(reply.substr(startIndex, 6).c_str()) * 0.0001;
            startIndex += 6;

            transform[4] = std::stod(reply.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            transform[5] = std::stod(reply.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            transform[6] = std::stod(reply.substr(startIndex, 7).c_str()) * 0.01;
            startIndex += 7;
            transform[7] = std::stod(reply.substr(startIndex, 6).c_str()) * 0.0001;
            startIndex += 6;
        }
        startIndex = endIndex + 1;

        trackingTraget->toolStatus = TrackingTargetStatus::NDI_OKAY;
        std::copy(transform, transform + 8, trackingTraget->TransformData);
    }
}

bool qNDIReceiveThreadObject::ndiSocketClose()
{
    if (ndiSocket == NULL)
    {
        return false;
    }
    closesocket(ndiSocket);
    WSACleanup();//�ͷų�ʼ��Ws2_32.dll���������Դ��
    return true;
}

