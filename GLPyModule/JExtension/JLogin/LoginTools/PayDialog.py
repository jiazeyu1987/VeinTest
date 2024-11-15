import slicer
import slicer.util as util
import os
import qt
from datetime import datetime
import requests


# 嵌入ui已有widget
class PayDialog:
    def __init__(self):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的上一层目录
        parent_directory = os.path.dirname(os.path.dirname(current_file_path))
        # 其他插件也会用到这个弹窗，所以不能通过parent加载ui文件
        self.uiWidget = slicer.util.loadUI(parent_directory + '/Resources/UI/PayDialog.ui')
        self.ui = util.childWidgetVariables(self.uiWidget)
        self._init_ui()

    def _init_ui(self):
        self.uiWidget.setWindowFlags(qt.Qt.FramelessWindowHint)
        self.ui.btn_pay.clicked.connect(self.submit_payment)
        self.ui.label_order_no.setText("TD" + datetime.now().strftime("%Y%m%d%H%M%S"))
        self.amount_group = qt.QButtonGroup()
        self.amount_group.addButton(self.ui.amount_1, 1)
        self.amount_group.addButton(self.ui.amount_2, 2)
        self.amount_group.addButton(self.ui.amount_3, 3)

        # 支付方式
        self.payment_group = qt.QButtonGroup()
        self.payment_group.addButton(self.ui.alipay, 1)
        self.payment_group.addButton(self.ui.wechat, 2)

    def submit_payment(self):
        order_no = self.ui.label_order_no.text
        amount_id = self.amount_group.checkedId()
        payment_id = self.payment_group.checkedId()

        if amount_id == -1 or payment_id == -1 or not order_no:
            qt.QMessageBox.warning(self.uiWidget, "警告", "请填写所有字段并选择金额和支付方式")
            return

        amount = {1: "0.1 元", 2: "0.2 元", 3: "0.3 元"}[amount_id]
        payment = {1: "alipay.direct.pc", 2: "wxpaynative"}[payment_id]

        # 发送POST请求到服务器
        try:
            response = requests.post('http://127.0.0.1:5000/api/startOrderTest', data={
                'orderNo': order_no,
                'amount': amount,
                'payType': payment
            })
            response.raise_for_status()  # 检查请求是否成功
            qt.QMessageBox.information(self.uiWidget, "支付信息",
                                       f"订单编号: {order_no}\n支付金额: {amount}\n支付方式: {payment}\n服务器响应: {response.text}")
            self.close()  # 关闭支付窗口
        except requests.RequestException as e:
            qt.QMessageBox.warning(self.uiWidget, "支付失败", f"支付请求失败: {e}")

    def show(self):
        self.uiWidget.show()

    def close(self):
        self.uiWidget.close()
