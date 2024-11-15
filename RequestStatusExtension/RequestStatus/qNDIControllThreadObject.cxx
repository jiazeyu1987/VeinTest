#include "qNDIControllThreadObject.h"

QString qNDIControllThreadObject::send_synchronize_cmd(QString cmd) {
  QString res;
  QStringList list1 = cmd.split(", ");
  if (list1[1] == "GetMarkerInfo") {
    return obj->track();
  }
  return res;
}

void qNDIControllThreadObject::send_thread_cmd(QString cmd) {
    QStringList list1 = cmd.split(", ");
    if (list1.length() < 2) {
        return;
    }
    if (list1[0] != "NDI") {
        return;
    }
    if (list1[1] == "SetGapMax") {
        return;
    }
    if (list1[1] == "Stop") {
        std::string command = std::string("TSTOP ");
        /*obj->sendndiCommand(command);
        obj->getErrorCodeFromResponse(obj->readResponse());*/
        obj->WriteAndRead(command);
        obj->ndiSocketClose();
        return;
    }
    if (list1[1] == "SetLaserStatus") {
        if ((list1.length()) == 3)
        {
            bool on = list1[2].toInt() == 1;
            SetLaserStatus(on);
            return;
        }
    }
    if (list1[1] == "Sleep") {
        if ((list1.length()) == 3)
        {
            int second = list1[2].toInt();
            ndiSocketSleep(second);
            return;
        }
    }
    if (list1[1] == "SETPATH") {
        if ((list1.length()) == 3)
        {
            obj->base_path = list1[2];
            return;
        }
    }
    if (list1[1] == "OpenAndShowLog") {
        if ((list1.length()) == 3)
        {
            obj->logfile = new QFile(list1[2]);
            qDebug() << "Create Log File" << obj->logfile;
            if (obj->logfile->exists()) {
                obj->logfile->remove();
            }
            if (obj->logfile->open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text)) {
                obj->out = new QTextStream(obj->logfile);
                return;
            }
            return;
        }
    }
    if (list1[1] == "Connect") {
        if((list1.length()) == 3)
        {
            std::string ip = list1[2].toStdString();
            if (ndiSocketOpen(ip) != true)
            {
                std::cout << "Connection Failed!" << std::endl;
                return;
            }
            std::cout << "Connected!" << std::endl;
            Init();
            loadTools(); 
            initializeAndEnableTools();
            auto rv = obj->WriteAndRead(std::string("TSTART "));
            if (rv.errorCode > -1) {
                obj->isTracking = true;
                obj->map_info["connect_status"] = "1";
            }
            qDebug() << "Do ConnectNDI";
        }
    }
}



void qNDIControllThreadObject::SetLaserStatus(bool isOn)
{
    if (IsSetLaserOn == isOn) return;
    if (!obj->isConnected) return;
    IsSetLaserOn = isOn;
    if (IsSetLaserOn == true)
    {
        if (setLaserThread == nullptr)
        {
            setLaserThread = new std::thread(&qNDIControllThreadObject::SetLaserOn, this);
        }
    }
    return;
}

void qNDIControllThreadObject::ndiTransformToMatrix(const double trans[8], double matrix[16])
{
    double ww, xx, yy, zz, wx, wy, wz, xy, xz, yz, ss, rr, f;

    /* Determine some calculations done more than once. */
    ww = trans[0] * trans[0];
    xx = trans[1] * trans[1];
    yy = trans[2] * trans[2];
    zz = trans[3] * trans[3];
    wx = trans[0] * trans[1];
    wy = trans[0] * trans[2];
    wz = trans[0] * trans[3];
    xy = trans[1] * trans[2];
    xz = trans[1] * trans[3];
    yz = trans[2] * trans[3];

    rr = xx + yy + zz;
    ss = (ww - rr) * 0.5;
    /* Normalization factor */
    f = 2.0 / (ww + rr);

    /* Fill in the matrix. */
    matrix[0] = (ss + xx) * f;
    matrix[1] = (wz + xy) * f;
    matrix[2] = (-wy + xz) * f;
    matrix[3] = 0;
    matrix[4] = (-wz + xy) * f;
    matrix[5] = (ss + yy) * f;
    matrix[6] = (wx + yz) * f;
    matrix[7] = 0;
    matrix[8] = (wy + xz) * f;
    matrix[9] = (-wx + yz) * f;
    matrix[10] = (ss + zz) * f;
    matrix[11] = 0;
    matrix[12] = trans[4];
    matrix[13] = trans[5];
    matrix[14] = trans[6];
    matrix[15] = 1;
}

void qNDIControllThreadObject::ndiAnglesFromMatrix(double outRotationAngles[3], const double rotationMatrix[16])
{
    double yaw, cosYaw, sinYaw;

    yaw = atan2(rotationMatrix[1], rotationMatrix[0]);
    cosYaw = cos(yaw);
    sinYaw = sin(yaw);

    outRotationAngles[2] = yaw;
    outRotationAngles[1] = atan2(-rotationMatrix[2], (cosYaw * rotationMatrix[0]) + (sinYaw * rotationMatrix[1]));
    outRotationAngles[0] = atan2((sinYaw * rotationMatrix[8]) - (cosYaw * rotationMatrix[9]), (-sinYaw * rotationMatrix[4]) + (cosYaw * rotationMatrix[5]));
}

void qNDIControllThreadObject::ndiCoordsFromMatrix(double coords[3], const double matrix[16])
{
    coords[0] = matrix[12];
    coords[1] = matrix[13];
    coords[2] = matrix[14];
}

bool qNDIControllThreadObject::ndiSocketSleep(int milliseconds)
{
    Sleep(milliseconds);
    return true;
}

void qNDIControllThreadObject::SetLaserOn()
{
    while (true)
    {
        if (IsSetLaserOn == false)
        {
            /*obj->sendndiCommand("SET Param.Laser.Laser Status=" + std::to_string(0));
            std::string response = obj->readResponse();
            int errorCode = obj->getErrorCodeFromResponse(response);*/
            obj->WriteAndRead("SET Param.Laser.Laser Status=" + std::to_string(0));
            break;
        }
        /*obj->sendndiCommand("SET Param.Laser.Laser Status=" + std::to_string(1));
        std::string response = obj->readResponse();
        int errorCode = obj->getErrorCodeFromResponse(response);*/
        obj->WriteAndRead("SET Param.Laser.Laser Status=" + std::to_string(1));
        Sleep(30000);
    }
}

int qNDIControllThreadObject::Init()
{
    // Send the INIT command
    std::string command = std::string("INIT ");
    auto rv = obj->WriteAndRead(command);
    /*obj->sendndiCommand(command);
    return obj->getErrorCodeFromResponse(obj->readResponse());*/
    return rv.errorCode;
}


bool qNDIControllThreadObject::ndiSocketOpen(std::string myIPAddress)
{
    WSADATA wsaData;
    // Initialize Winsock
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != NO_ERROR)
    {
        return false;
    }

    addrinfo addressInfo;
    memset(&addressInfo, 0, sizeof(addressInfo));
    addressInfo.ai_family = AF_INET;
    addressInfo.ai_socktype = SOCK_STREAM;
    addressInfo.ai_protocol = IPPROTO_TCP;

    // Setup a TCP socket using the given hostname and port
    addrinfo* aiPointer = NULL, * pai;
    int addrinforesult = getaddrinfo(myIPAddress.c_str(), "8765", &addressInfo, &aiPointer);
    if (addrinforesult != 0)
    {
        std::cerr << "getaddrinfo Error code " << addrinforesult << " (" << gai_strerror(addrinforesult) << ")" << std::endl;
        return false;
    }

    for (pai = aiPointer; pai != NULL; pai = pai->ai_next)
    {
        //Initialize socket
        obj->ndiSocket = socket(pai->ai_family, pai->ai_socktype, pai->ai_protocol);
        if (obj->ndiSocket == INVALID_SOCKET)
        {
            continue;
        }
        //Initialize connection
        obj->isConnected = ::connect(obj->ndiSocket, pai->ai_addr, (socklen_t)pai->ai_addrlen) >= 0;
        if (obj->isConnected)
        {
            break;
        }
        obj->ndiSocketClose();
        obj->ndiSocket = INVALID_SOCKET;
    }

    if (!obj->isConnected)
    {
#pragma warning( disable : 4996)
#pragma warning( push )
        std::cerr << "::connect Error code " << errno << " (" << std::strerror(errno) << ")" << std::endl;
#pragma warning( pop )
    }
    freeaddrinfo(aiPointer);
    return obj->isConnected;
}



void qNDIControllThreadObject::loadTools()
{
    obj->trackingTragets.clear();
    TrackingTarget T339;
    T339.toolType = TrackingTargetType::T339;
    T339.ROMPath = obj->base_path.toStdString()+"/NDIRoms/8700339.rom";
    obj->trackingTragets.push_back(T339);
    TrackingTarget T340;
    T340.toolType = TrackingTargetType::T340;
    T340.ROMPath = obj->base_path.toStdString() + "/NDIRoms/8700340.rom";
    obj->trackingTragets.push_back(T340);
    TrackingTarget T449;
    T449.toolType = TrackingTargetType::T449;
    T449.ROMPath = obj->base_path.toStdString() + "/NDIRoms/8700449.rom";
    obj->trackingTragets.push_back(T449);

    if (obj->trackingTragets.size() > 0)
    {
        std::cout << "Loading Tool Definitions (.rom files) ..." << std::endl;
        for (int f = 0; f < obj->trackingTragets.size(); f++)
        {
            if (_access(obj->trackingTragets[f].ROMPath.c_str(), 0) != 0)
            {
                std::cout << "rom files: " << obj->trackingTragets[f].ROMPath << "is not exist" << std::endl;
                return;
            }
            std::cout << "Loading: " << obj->trackingTragets[f].ROMPath << std::endl;
            // Request a port handle to load a passive tool into
            int portHandle = portHandleRequest();
            obj->trackingTragets[f].toolID = portHandle;
            // Load the .rom file using the previously obtained port handle
            loadSromToPort(obj->trackingTragets[f].ROMPath.c_str(), portHandle);
        }
    }
}

int qNDIControllThreadObject::portHandleRequest()
{
    // Send the PHRQ command
    std::string command = "PHRQ *********100**";
    auto rv = obj->WriteAndRead(command);
    //obj->sendndiCommand(command);
    //// Return the requested port handle or an error code
    //std::string response = obj->readResponse();
    //int errorCode = obj->getErrorCodeFromResponse(response);
    if (rv.errorCode == 0)
    {
        return obj->stringToInt(rv.response);
    }
    else
    {
        return rv.errorCode;
    }
}

void qNDIControllThreadObject::loadSromToPort(std::string romFilePath, int portHandle)
{
    // If the port handle is invalid, print an error message and return
    if (portHandle < 0)
    {
        std::cout << "Invalid port handle: " << portHandle << std::endl;
        return;
    }

    // If the .rom file cannot be opened, print an error message and return
    std::ifstream inputFileStream(romFilePath.c_str(), std::ios_base::binary);
    if (!inputFileStream.is_open())
    {
        std::cout << "Cannot open file: " + romFilePath << std::endl;
        return;
    }

    // Read the entire file and convert it to ASCII hex characters
    std::stringstream romStream;
    romStream << std::setfill('0') << std::hex;
    while (!inputFileStream.eof())
    {
        romStream << std::setw(2) << inputFileStream.get();
    }
    inputFileStream.close();

    // Tool data is sent in chunks of 128 hex characters (64-bytes).
    // It must be an integer number of chunks, padded with zeroes at the end.
    const int messageSizeChars = 128;
    const int messageSizeBytes = 64;
    std::string toolDefinition = romStream.str();
    int remainder = toolDefinition.size() % messageSizeChars;
    toolDefinition.append((messageSizeChars - remainder), '0');
    const int totalIterations = (int)toolDefinition.size() / messageSizeChars;
    std::string command = "";
    int errorCode = 0;
    std::stringstream startAddressStream;
    startAddressStream << std::setfill('0') << std::hex;
    for (int i = 0; i < totalIterations; i++)
    {
        // Pass the startAddress as a fixed width four characters of hex padded with zeroes
        startAddressStream << std::setw(4) << i * messageSizeBytes;

        // Send the PVWR command
        command = std::string("PVWR ").append(obj->intToHexString(portHandle, 2));
        command += startAddressStream.str();
        command += toolDefinition.substr(i * messageSizeChars, messageSizeChars);
        //obj->sendndiCommand(command);

        //// If we run into an error, print something before exiting
        //errorCode = obj->getErrorCodeFromResponse(obj->readResponse());
        auto rv = obj->WriteAndRead(command);
        if (rv.errorCode != 0)
        {
            std::cout << "PVWR returned error: " << rv.errorCode << std::endl;
            return;
        }

        // Reset the stringstream used to print fixed width address sizes
        startAddressStream.str("");
    }
}

void qNDIControllThreadObject::initializeAndEnableTools()
{
    std::cout << std::endl << "Initializing and enabling tools..." << std::endl;
    // Send the PHSR command
    std::stringstream stream;
    stream << "PHSR " << std::setw(2) << std::setfill('0') << 2;
    std::string command = stream.str();
    //obj->sendndiCommand(command);

    //// If an error occurred, return an empty vector
    //std::string response = obj->readResponse();
    //int errorCode = obj->getErrorCodeFromResponse(response);
    auto rv = obj->WriteAndRead(command);
    std::vector<std::string> portHandles;
    if (rv.errorCode != 0)
    {
        return;
    }

    int numPortHandles = obj->stringToInt(rv.response.substr(0, 2));
    for (int i = 0; i < numPortHandles; i++)
    {
        portHandles.push_back(rv.response.substr(i * 5 + 2, 2));
    }

    for (int i = 0; i < portHandles.size(); i++)
    {
        // Send the PINIT command
        std::string commandPINIT = std::string("PINIT ").append(portHandles[i]);
        /*obj->sendndiCommand(commandPINIT);
        obj->getErrorCodeFromResponse(obj->readResponse());*/
        obj->WriteAndRead(commandPINIT);
        // Send the PENA command
        std::string commandPENA = std::string("PENA ").append(portHandles[i]);
        commandPENA += (char)'D';
        /*obj->sendndiCommand(commandPENA);
        obj->getErrorCodeFromResponse(obj->readResponse());*/
        obj->WriteAndRead(commandPENA);
    }
}