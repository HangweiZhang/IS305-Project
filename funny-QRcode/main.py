import sys
import os
import shutil

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import generate

from Ui_qr_designer import Ui_MainWindow
from Ui_advancedWindow import Ui_advancedWindow

# 默认存放路径
working_dir = os.getcwd()
output_dir = working_dir + "/output/"

class qrThread(QThread):

    trigger = pyqtSignal(str)

    def __init__(self, words, version, level, picture, colorized, constract, brightness, saveName, outDic):
        super().__init__()
        self.words = words
        self.version = version
        self.level = level
        self.picture = picture
        self.colorized = colorized
        self.constract = constract
        self.brightness = brightness
        self.saveName = saveName
        self.outDic = outDic

    def run(self):
        _, _, qrName = generate.run(self.words, 
                                    self.version, 
                                    self.level, 
                                    self.picture, 
                                    self.colorized, 
                                    self.constract, 
                                    self.brightness,
                                    self.saveName,
                                    self.outDic)
        self.trigger.emit(qrName)

class advanceWindow(QDialog, Ui_advancedWindow):

    setData = pyqtSignal(int, str, bool, float, float)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.btn_click)

    def btn_click(self):
        version = int(self.versionEdit.text())
        level = str(self.leverBox.currentText())
        colorized = False if (self.colorizedBox.currentText() == "否") else True
        contrast = float(self.constractEdit.text())
        brightness = float(self.brightEdit.text())

        self.setData.emit(version, level, colorized, contrast, brightness)
        self.close()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.words = ""
        self.version = 5
        self.level = "H"
        self.imgName = None
        self.colorized = False
        self.constract = 1.0
        self.brightness = 1.0
        self.saveName = None
        self.outDic = output_dir

        self.advance = advanceWindow()

        self.advancedGen.clicked.connect(self.show_advance)
        self.quickGen.clicked.connect(self.qr_generate)
        self.btnPicture.clicked.connect(self.open_img)
        self.btnSave.clicked.connect(self.click_save)

    # 高级选项窗口
    def show_advance(self):
        self.advance.show()
        self.advance.setData.connect(self.getData)

    def getData(self, version, level, colorized, contrast, brightness):
        self.version = version
        self.level = level
        self.colorized = colorized
        self.constract = contrast
        self.brightness = brightness

    # 打开图片
    def open_img(self):
        self.imgName, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image files(*.jpg *.png *.bmp *.gif)")
        self.picEdit.setText(self.imgName)
        self.imgObj = QGraphicsScene()
        self.imgObj.addPixmap(QPixmap(self.imgName).scaled(self.imgView.size()))
        self.imgView.setScene(self.imgObj)
    
    # 生成个性化二维码
    def qr_generate(self):
        self.words = self.wordEdit.text()
        self.generate = qrThread(self.words, 
                                    self.version, 
                                    self.level, 
                                    self.imgName, 
                                    self.colorized, 
                                    self.constract, 
                                    self.brightness,
                                    self.saveName,
                                    self.outDic
                                    )
        self.generate.start()
        self.generate.trigger.connect(self.qr_display)

    # 显示生成二维码
    def qr_display(self, qrName):
        self.qrName = qrName
        self.qrObj = QGraphicsScene()
        self.qrObj.addPixmap(QPixmap(self.qrName).scaled(self.qrView.size()))
        self.qrView.setScene(self.qrObj)

    # 另存为
    def click_save(self):
        savePath, _  = QFileDialog.getSaveFileName(self, "另存为", "", "Image files(*.jpg *.png *.bmp *.gif)")
        shutil.copy(self.qrName, savePath)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())