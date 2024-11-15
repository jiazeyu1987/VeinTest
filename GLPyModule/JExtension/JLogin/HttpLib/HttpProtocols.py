

#from PyQt5.QtWidgets import *
import slicer.util as util
import requests,zipfile,json,os

def Str2QByteArray(s):
    from PyQt5.QtCore import QByteArray
    byte_array = QByteArray()
    byte_array.append(s.encode())
    return byte_array

class HttpNetwork():
    m_token = None
    def __init__(self,host):
        self.host=host
        self.m_token=None

    def Login2Server(self, account, pwd):
        from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager,QNetworkReply
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo
        """
        login to server
        """
        # print(self.host)
        # print(account)
        # print(pwd)
        req=QNetworkRequest(QUrl(self.host+"/login"))
        # print(self.host+"/login")
        # reply=QtNetwork.QNetworkReply()
        manager=QNetworkAccessManager()
        headerName=Str2QByteArray("Content-Type")
        value=Str2QByteArray("application/json;charset=UTF-8")
        req.setRawHeader(headerName, value)
        data=QByteArray()
        sendJson=QJsonDocument(data).object()
        sendJson["username"] = account
        sendJson["password"] = pwd

        doc=QJsonDocument(sendJson)
        reply=manager.post(req,doc.toJson(QJsonDocument.JsonFormat.Indented))
        eventloop=QEventLoop()
        reply.finished.connect(eventloop.quit)
        QTimer.singleShot(2000,eventloop.quit)
        eventloop.exec()
        # connect(reply, SIGNAL(finished()), & eventloop, SLOT(quit()))
        if reply.error() == QNetworkReply.NoError :
            responseByte = reply.readAll()
            jsonError=QJsonParseError()
            jsonDoc=QJsonDocument.fromJson(responseByte,jsonError)

            # print(jsonError.errorString())
            if jsonError.error == QJsonParseError.ParseError.NoError:
                print(3)
                responseObj=jsonDoc.object()
                print(4)
                if responseObj["code"].toInt() == 200 :

                    self.m_token = responseObj["token"].toString()
                    error = responseObj["msg"].toString()
                    return True,1

                else:
                    error = responseObj["msg"].toString()
                    return False,error
            else:
                return False,jsonError.errorString()
        else:
            return False,"网络连接失败"

    def ReconTaskUpload(self, zip_path, reconJson):
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo,QFile
        from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager,QNetworkReply
        if self.m_token == None:
            return "Please Login to the server first"

        req = QNetworkRequest(QUrl(self.host + "/reconstruct/http"))
        manager = QNetworkAccessManager()

        eventloop=QEventLoop()
        content=QByteArray()


        headerName = Str2QByteArray("Accept")
        value = Str2QByteArray("*/*")
        req.setRawHeader(headerName, value)
        authName=Str2QByteArray("Authorization")
        req.setRawHeader(authName, self.m_token.encode("utf-8"))

        zipfile=QFile(zip_path)
        readFile = QByteArray()
        if zipfile.open(QIODevice.ReadOnly) is True:
            readFile=zipfile.readAll()
        else:
            return "File open failed"

        fileInfo=QFileInfo(zipfile)
        fileName=fileInfo.fileName()
        zipfile.close()

        # content填充
        boundary = "--------------------------864753390260194048816082"
        startBoundary = "--" + boundary
        endBoundary = "\r\n--" + boundary + "--\r\n"
        m_ContentType = "multipart/form-data; boundary=" + boundary
        tempStr = startBoundary
        tempStr += "\r\nContent-Disposition: form-data; name=\"recon\"\r\n"
        tempStr += "Content-Type: application/json \r\n\r\n"

        reconDoc=QJsonDocument(reconJson)
        reconJsonStr=reconDoc.toJson(QJsonDocument.JsonFormat.Indented)
        # print(reconJsonStr)

        content.append(tempStr.encode("latin1"))
        content.append(reconJsonStr)
        content.append("\r\n")

        tempStr = startBoundary
        tempStr += "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + fileName + "\"\r\n"
        tempStr += "Content-Type: application/zip \r\n\r\n"
        content.append(tempStr.encode("latin1"))
        content.append(readFile)
        content.append(endBoundary)

        req.setHeader(QNetworkRequest.ContentTypeHeader, Str2QByteArray(m_ContentType))
        req.setHeader(QNetworkRequest.ContentLengthHeader, content.length())
        print("start post")
        reply = manager.post(req, content)
        print("connect")
        reply.finished.connect(eventloop.quit)
        print("time")
        QTimer.singleShot(10000000, eventloop.quit)
        print("start exec")
        eventloop.exec()
        print("reply")
        if reply.error() == QNetworkReply.NoError:
            responseByte = reply.readAll()
            print(responseByte)
            jsonError = QJsonParseError()
            jsonDoc = QJsonDocument.fromJson(responseByte, jsonError)

            # print(jsonError.errorString())
            if jsonError.error == QJsonParseError.ParseError.NoError:

                responseObj = jsonDoc.object()
                if responseObj["code"].toInt() == 200:
                    error = "successful"
                else:
                    error = responseObj["msg"].toString()

                return error, responseObj
            else:
                return jsonError.errorString(), None
        else:
            return "Failed:"+reply.errorString(), None
    
    
    def QueryPatienId(self, patientId, pageNum, pageSize, beginTime, endTime):
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo,QFile
        from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager
        print(f"\nCurrent token before QueryPatienId: {self.m_token}")
        print(f"self.host:{self.host}")
        # 构建URL，使用字符串格式化替换参数
        url_query = f"{self.host}/reconstruct/query/patient?patientId={patientId}&pageNum={pageNum}&pageSize={pageSize}&beginTime={beginTime}&endTime={endTime}"
        # 设置请求头，动态填充 Authorization 头
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Authorization': f'Bearer {self.m_token}'  # 在这里将 token 加入到 Authorization 头
        }
        try:
            # 发送GET请求，并获取回复
            response = requests.get(url_query, headers=headers)
            # 检查网络回复是否无错误
            response.raise_for_status()
            # 解析JSON数据
            response_json = response.json()
            # 如果从服务器返回的 JSON 数据中存在一个名为 'code' 的字段，并且该字段的值等于 200，则条件为真。
            # 这通常用于检查 HTTP 请求是否成功，因为通常 HTTP 状态码 200 表示请求成功。
            if response_json.get('code') == 200:
                # 输出响应文本
                print(f"Server Response: {response.text}")
                print("QueryPatienId successful")
                print(f"Page Num:{pageNum}")

                # 提取 "rows"
                rows = response_json.get("rows", [])
                # 提取 "total"
                total = response_json.get("total")

                return "QueryPatienId successful", response_json.get('msg'),rows,total
            else:
                # 提取 "rows"
                rows = response_json.get("rows", [])
                # 提取 "total"
                total = response_json.get("total")
                print(f"Server Response: {response.text}")
                print("QueryPatienId Failed")
                return "QueryPatienId Failed", response_json.get('msg'),rows,total
        except requests.exceptions.RequestException as e:
            # 返回查询失败
            print(f"HTTP请求错误: {e}")
            

    def Download_data(self,target_path_file, save_path_file,rows,row):
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo,QFile
        from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager
        print(f"\nCurrent token before Download_data: {self.m_token}")
        # 构建下载文件的URL
        url_download = f"{self.host}/reconstruct/download?filePath={target_path_file}"
        # 设置请求头，包含授权信息
        headers = {
            "Authorization": f'{self.m_token}'
        }
        print(f"target_path_file:{target_path_file}")
        print(f"save_path_file:{save_path_file}")
        try:
            # 发送GET请求
            response = requests.get(url_download, headers=headers, timeout=15)
            response.raise_for_status()  # 对于错误的响应状态，抛出HTTPError异常
            # 输出服务器响应文本
            print("Server Response:", response.text)
            # 检查响应是否包含JSON数据
            try:
                # 尝试解析JSON数据
                response_json = response.json()
                # 如果解析成功，说明下载失败，因为服务器返回了JSON数据
                # 处理JSON数据
                print("Download_data Failed")
                return -1,  response.text
            except json.JSONDecodeError:
                # 提取类型信息
                row_type = rows[row].get("type", "")
                sequenceId_value = rows[row].get("sequenceId", "")

                # 根据提取的 type、sequenceId 和 save_path_file 构建保存文件夹路径（二级目录type/sequenceId 的层次结构）
                folder_path = os.path.join(os.path.dirname(save_path_file), row_type, str(sequenceId_value))
                # 创建文件夹，如果存在则不报错
                os.makedirs(folder_path, exist_ok=True)
                # 构建新的文件名
                new_filename = os.path.join(folder_path, f"{sequenceId_value}.zip")

                # 检查文件是否已存在，如果存在，直接替换(避免重复下载)
                if os.path.exists(new_filename):
                    print(f"Replacing file: {new_filename}")
                    os.remove(new_filename)

                # 将响应的内容写入指定的 new_file
                with open(new_filename, 'wb') as new_file:
                    new_file.write(response.content)

                print(f"Finaly file to: {new_filename}")

                # 解压缩文件
                # 创建一个 ZipFile 对象
                with zipfile.ZipFile(new_filename, 'r') as zip_ref:
                    # 解压缩到指定目录
                    print("zip file")
                    #zip_ref.extractall(folder_path)

                print("Download_data successful")

                # 返回下载成功的标志和空的结果（因为没有JSON数据）
                return 1, folder_path

        except requests.exceptions.RequestException as err:
            print("失败")
            # 请求异常，返回下载失败的标志和错误信息
            return -1, str(err)
    
    def delete_zip_files_in_direct_subfolders(self,folder_path):
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo,QFile
        # 获取子文件夹中的所有文件
        files_in_subfolder = os.listdir(folder_path)

        # 遍历每个文件，如果是 ZIP 文件则删除
        for file_name in files_in_subfolder:
            if file_name.endswith('.zip'):
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
            
    def DownloadData(self, targetPathFile, savePathFile):
        from PyQt5.QtNetwork import QNetworkRequest,QNetworkAccessManager,QNetworkReply
        from PyQt5.QtCore import QByteArray,QUrl,QJsonDocument, QJsonParseError,QEventLoop,QTimer,QIODevice,QFileInfo,QFile
        if self.m_token == None:
            return "Please Login to the server first"

        req = QNetworkRequest(QUrl(self.host + "/reconstruct/download?filePath="+targetPathFile))
        manager = QNetworkAccessManager()

        eventloop = QEventLoop()
        content = QByteArray()
        authName = Str2QByteArray("Authorization")
        req.setRawHeader(authName, self.m_token.encode("utf-8"))
        reply = manager.get(req)
        reply.finished.connect(eventloop.quit)
        QTimer.singleShot(5000, eventloop.quit)
        eventloop.exec()
        if reply.error() == QNetworkReply.NoError:
            responseByte = reply.readAll()
            jsonError = QJsonParseError()
            jsonDoc = QJsonDocument.fromJson(responseByte, jsonError)

            # print(jsonError.errorString())
            if jsonError.error == QJsonParseError.ParseError.NoError:

                responseObj = jsonDoc.object()
                saveFile=QFile(savePathFile)
                if saveFile.open(QIODevice.ReadWrite):
                    saveFile.write(responseByte)
                    error="successful"
                else:
                    error="Save File Failed"
                return error
            else:
                return jsonError.errorString()
        else:
            return reply.errorString()



