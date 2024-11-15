#include "qRegisterReceiveThreadObject.h"

qRegisterReceiveThreadObject::qRegisterReceiveThreadObject() {
    m_npoints = 0;
    
}
qRegisterReceiveThreadObject::~qRegisterReceiveThreadObject() {
}

void qRegisterReceiveThreadObject::OnReceiveObjectInnerTick() {
    registrationImp();
    ToInfoString();
}


QString qRegisterReceiveThreadObject::registrationImp() {
    updateMarkers();
    //qDebug() << "registrationImp"; 
    if (m_points_reg->GetNumberOfPoints() == 0 || m_points_ct->GetNumberOfPoints() == 0
        || m_points_reg->GetNumberOfPoints() != m_points_ct->GetNumberOfPoints()) {
        map_info[MARKER_INFO] = -1;
        return "";
    }
    vtkNew<vtkLandmarkTransform> ltrans;
    ltrans->SetMode(VTK_LANDMARK_RIGIDBODY);
    ltrans->SetSourceLandmarks(m_points_reg);
    ltrans->SetTargetLandmarks(m_points_ct);
    // for (int i = 0; i < 4; i++)
    // {
    //   double* point = m_points_ct->GetPoint(i);
    //   std::cout << "from point : " << point[0] << ", " << point[1] << ", " << point[2] << "\n";
    // }
    // for (int i = 0; i < 4; i++)
    // {
    //   double* point = m_points_reg->GetPoint(i);
    //   std::cout << "to point : " << point[0] << ", " << point[1] << ", " << point[2] << "\n";
    // }
    ltrans->Update();

    auto trams_mat = ltrans->GetMatrix();
    auto det = trams_mat->Determinant();
    auto mat_ptr = trams_mat->GetData();

    if (det * det < 1e-12 || det < 0 || ((det - 1.0) * (det - 1.0) > 1e-12)) {
        map_info[MARKER_INFO] = -1;
        return "";
    }

    vtkSmartPointer<vtkPoints> m_points_out = vtkSmartPointer<vtkPoints>::New();
    ltrans->TransformPoints(m_points_reg, m_points_out);
    //ltrans->Update();
    QVector<double> err_and_matrix;
    double dsum = 0.0;
    double error = 0;
    for (int i = 0; i < m_npoints; i++)
    {

        double d = vtkMath::Distance2BetweenPoints(m_points_ct->GetPoint(i), m_points_out->GetPoint(i));
        error = d;
        dsum += d;
        error = 0;
    }

    error = sqrt(dsum / m_npoints);
    err_and_matrix.append(error);
    QString reg_matrix;
    for (int32_t i = 0; i < 4; i++) {
        err_and_matrix.append(mat_ptr[i * 4 + 0]);
        err_and_matrix.append(mat_ptr[i * 4 + 1]);
        err_and_matrix.append(mat_ptr[i * 4 + 2]);
        err_and_matrix.append(mat_ptr[i * 4 + 3]);

        reg_matrix.append(QString::number(err_and_matrix[1 + i * 4 + 0]));
        reg_matrix.append(",");
        reg_matrix.append(QString::number(err_and_matrix[1 + i * 4 + 1]));
        reg_matrix.append(",");
        reg_matrix.append(QString::number(err_and_matrix[1 + i * 4 + 2]));
        reg_matrix.append(",");
        reg_matrix.append(QString::number(err_and_matrix[1 + i * 4 + 3]));
        reg_matrix.append(",");
    }
    reg_matrix.chop(1);
    map_info["matrix"] = reg_matrix.toStdString(); // this is the reg matrix
    // qDebug() << "reg matrix is : " << reg_matrix;
    map_info[MARKER_INFO] = QString::number(error).toStdString(); // this is the reg error
    QString err_matrix_str = QString::number(error);
    err_matrix_str.append(",");
    err_matrix_str.append(reg_matrix);
    return err_matrix_str;
}
void qRegisterReceiveThreadObject::updateMarkers() {
    for (size_t idx = 0; idx < qRegisterReceiveThreadObject::m_npoints; idx++) {
        qRegisterReceiveThreadObject::m_points_reg->SetPoint(idx, qRegisterReceiveThreadObject::m_points_input->GetPoint(idx));
    }
}