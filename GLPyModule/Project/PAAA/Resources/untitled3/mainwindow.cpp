#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QMovie.h>
MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    this->setWindowFlags(Qt::FramelessWindowHint);
    showFullScreen();
    auto path = "D:/S521/GLPyModule/Project/PAAA/Resources/Icons/loading60.gif";
    movie = new QMovie(path);
    ui->lblIcon->setMovie(movie);
    start();
}

void MainWindow::start()
{
    movie->start();
}

void MainWindow::stop()
{
    movie->stop();
}

MainWindow::~MainWindow()
{
    delete ui;
}

