#include "qIMEReceiveThreadObject.h"



void qIMEReceiveThreadObject::OnReceiveObjectInnerTick() {
    this->track();
    
}




QString qIMEReceiveThreadObject::track() {
    T_MarkerInfo m_markerSt;
    T_AimPosStatusInfo m_statusSt;
    E_ReturnValue rlt;
    try
    {
        rlt = Aim_GetMarkerAndStatusFromHardware(m_aimHandle, E_Interface::I_ETHERNET, m_markerSt, m_statusSt);
        if (rlt == AIMOOE_OK)
        {
            int markerNum = m_markerSt.MarkerNumber;
            if (m_markerSt.PhantomMarkerGroupNumber > 0)//���ڻ�Ӱ��
            {
                //���ݻ�Ӱ����ܷ�������ʼ��ÿ���Ӱ��Ĵ�ſռ�
                std::vector<int>* PantomMarkerID = new  std::vector<int>[m_markerSt.PhantomMarkerGroupNumber];
                for (int j = 0; j < m_markerSt.PhantomMarkerGroupNumber; j++)
                {
                    PantomMarkerID[j].reserve(50);//ÿ��Ԥ��50���㣬�������ֵΪ200�������������ܴﵽ��
                }
                //������Ӱ�㾯ʾ���飬�ѻ�Ӱ����ൽ��Ӧ������
                for (int j = 0; j < markerNum; j++)
                {
                    int WarningValue = m_markerSt.PhantomMarkerWarning[j];
                    if (WarningValue > 0)//��ʾ��j����Ϊ��Ӱ��
                    {
                        PantomMarkerID[WarningValue - 1].push_back(j);//�Ѹõ���ൽ��Ӧ�Ļ�Ӱ�����
                    }
                }
                delete[] PantomMarkerID;
            }
            map_info[CONNECT_STATUS] = "1";
        }
        else
        {
            map_info[CONNECT_STATUS] = "-1";
        }
    }
    catch (std::exception& e) {
        map_info[EXCEPTION_TRACK] = "1";
    }

    //GetMarkerCoodinates
    int m_marker_num = m_markerSt.MarkerNumber;
    MarkerOutput data[200];

    for (int i = 0; i < m_marker_num; i++)
    {
        data[i].coordinates[0] = m_markerSt.MarkerCoordinate[i * 3];
        data[i].coordinates[1] = m_markerSt.MarkerCoordinate[i * 3 + 1];
        data[i].coordinates[2] = m_markerSt.MarkerCoordinate[i * 3 + 2];
        data[i].confidence = (float)((m_markerSt.MarkerBGLightStatus) == E_BackgroundLightStatus::BG_LIGHT_OK);
    }
    if (m_marker_num < 3)
    {
        map_info[EXCEPTION_TRACK_NUMBER] = "1";
        return "";
    }


    bool id_error = false;
    int id_err_cnt = 0;
    for (int i = 0; i < m_marker_num; i++)// id is unique or not
    {
        for (int j = 0; j < m_marker_num; j++)
        {
            if (j != i && data[i].id == data[j].id)
                id_err_cnt++;
        }

        if (id_err_cnt > 0)
        {
            id_error = true;
            break;
        }
    }
    if ((m_marker_num != m_last_marker_num) || id_error)//numbers not match || id not unique
    {
        for (int i = 0; i < m_marker_num; i++)
        {
            data[i].last_id = -1;
            data[i].confidence = 0.0f;
        }
    }
    // qDebug() << "id_error: " << id_error;
    for (int i = 0; i < m_marker_num; i++)
    {
        if (data[i].last_id < 0)//tracking id init
        {
            data[i].id = i + 1;
        }

        double sumi = 0.0f;
        for (int j = 0; j < m_marker_num; j++)
        {
            if (j != i)
            {
                sumi += sqrt((data[i].coordinates[0] - data[j].coordinates[0]) * (data[i].coordinates[0] - data[j].coordinates[0]) +
                    (data[i].coordinates[1] - data[j].coordinates[1]) * (data[i].coordinates[1] - data[j].coordinates[1]) +
                    (data[i].coordinates[2] - data[j].coordinates[2]) * (data[i].coordinates[2] - data[j].coordinates[2]));
            }
        }

        data[i].dis_sum = sumi;
        sumi = 100000000000.0f;
        int tindex = -1;
        bool dis_error = false; // distance error
        if (data[i].last_id > 0)// tracking process
        {
            for (int j = 0; j < m_marker_num; j++)
            {
                double tempj = abs(data[i].dis_sum - data[j].last_dis_sum);
                if (tempj < sumi && tempj < 7)//(mm) when pos error from aimooe is larger than 1mm, two points 's dis error may larger than 3.5mm (sqrt[2^2+2^2+2^2]), so the dis diff error may larger than 7mm
                {
                    sumi = tempj;
                    tindex = j;
                    data[i].id = data[j].last_id;
                }
            }

        }

    }
    m_last_marker_num = m_marker_num;

    QString qstr("");
    for (int i = 0; i < m_marker_num; i++)
    {
        QString qstr1("");
        QString qstr2("");
        qstr1 = qstr1 + "conf:" + QString::number(data[i].confidence, 'f', 1) + " ";
        qstr1 = qstr1 + "x:" + QString::number(data[i].coordinates[0], 'f', 3) + " ";
        qstr1 = qstr1 + "y:" + QString::number(data[i].coordinates[1], 'f', 3) + " ";
        qstr1 = qstr1 + "z:" + QString::number(data[i].coordinates[2], 'f', 3) + " ";
        qstr2 = qstr2 + " " + QString::number(data[i].coordinates[0], 'f', 3);
        qstr2 = qstr2 + ", " + QString::number(data[i].coordinates[1], 'f', 3);
        qstr2 = qstr2 + ", " + QString::number(data[i].coordinates[2], 'f', 3) + ", ";
        qstr = qstr + " " + qstr1;
        data[i].last_dis_sum = data[i].dis_sum;
        data[i].last_id = data[i].id;
    }
    map_info[MARKER_INFO] = qstr.toStdString();
    return qstr;
}

