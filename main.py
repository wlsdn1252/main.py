import sys
import data_reader
import tensorflow_hub as hub

from PyQt5 import QtCore
from PyQt5.QtCore import QPropertyAnimation, QPoint, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("ai_mix.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1800, 1000)  # 윈도우 창 크기를 800x600으로 고정

        self.comboBox.addItem("작가 선택")
        self.comboBox.addItem("고흐")
        self.comboBox.addItem("뒤샹")
        self.comboBox.addItem("르누아르")
        self.comboBox.addItem("피카소")
        self.comboBox.currentIndexChanged.connect(self.updateImage)

        #버튼에 기능을 연결하는 코드
        self.content_btn.clicked.connect(self.load_image1)
        self.style_btn.clicked.connect(self.load_image2)
        self.mix_btn.clicked.connect(self.mix_image)

    def updateImage(self):
        self.imageLabel3.setVisible(False)

        selected_value = self.comboBox.currentText()

        # 이미지 업데이트 로직
        if selected_value == "고흐":
            pixmap = QPixmap("Gogh.jpg")
            self.imageLabel2.image_name = "Gogh.jpg"
        elif selected_value == "뒤샹":
            pixmap = QPixmap("Duchamp.JPG")
            self.imageLabel2.image_name = "Duchamp.JPG"
        elif selected_value == "르누아르":
            pixmap = QPixmap("Renoir.jpg")
            self.imageLabel2.image_name = "Renoir.jpg"
        elif selected_value == "피카소":
            pixmap = QPixmap("Picasso.jpg")
            self.imageLabel2.image_name = "Picasso.jpg"
        else:
            pixmap = QPixmap()

        self.imageLabel2.setPixmap(pixmap.scaled(512, 512, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        self.imageLabel2.move(1130, 90)
        self.imageLabel2.setVisible(True)

    def load_image1(self):
        # 이미지 파일 선택 다이얼로그 표시
        self.imageLabel3.setVisible(False)
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "JPEG Files (*.jpg)")

        if image_path:
            # QPixmap 객체 생성
            pixmap = QPixmap(image_path)
            self.imageLabel1.image_name = image_path.split("/")[-1]
            print("Image Name:", self.imageLabel1.image_name)

            # QLabel에 QPixmap 설정
            self.imageLabel1.setPixmap(pixmap.scaled(512, 512, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            self.imageLabel1.move(100,90)
            self.imageLabel1.setVisible(True)


    def load_image2(self):
        # 이미지 파일 선택 다이얼로그 표시
        self.imageLabel3.setVisible(False)
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "JPEG Files (*.jpg)")
        if image_path:
            # QPixmap 객체 생성
            pixmap = QPixmap(image_path)
            self.imageLabel2.image_name = image_path.split("/")[-1]
            print("Image Name:", self.imageLabel2.image_name)

        # QLabel에 QPixmap 설정
        # self.imageLabel.setPixmap(pixmap)
        self.imageLabel2.setPixmap(pixmap.scaled(512, 512, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        self.imageLabel2.move(1130, 90)
        self.imageLabel2.setVisible(True)

    def mix_image(self):
        # 이미지 파일 선택 다이얼로그 표시
        if self.imageLabel1.pixmap() is not None and self.imageLabel2.pixmap() is not None:

            self.animation1 = QPropertyAnimation(self.imageLabel1, b"pos")
            self.animation1.setDuration(1000)  # 애니메이션 지속 시간 (1초)
            self.animation1.setStartValue(QPoint(150, 90))  # 시작 위치
            self.animation1.setEndValue(QPoint(640, 90))  # 끝 위치
            self.animation1.setEasingCurve(QtCore.QEasingCurve.Linear)  # 이동 속도 곡선

            self.animation2 = QPropertyAnimation(self.imageLabel2, b"pos")
            self.animation2.setDuration(1000)  # 애니메이션 지속 시간 (1초)
            self.animation2.setStartValue(QPoint(1130, 90))  # 시작 위치
            self.animation2.setEndValue(QPoint(640, 90))  # 끝 위치
            self.animation2.setEasingCurve(QtCore.QEasingCurve.Linear)  # 이동 속도 곡선

            # 애니메이션 실행
            self.animation1.start()
            self.animation2.start()

            content_file = self.imageLabel1.image_name
            style_file = self.imageLabel2.image_name

            self.run_ai(content_file, style_file)

            QTimer.singleShot(1000, self.doAction)  # 1초 후에 doAction() 실행

        else:
            QMessageBox.warning(self,"똑바로해라ㅡㅡ","사진이 없습니다.")

    # 섞기 버튼
    def doAction(self):
        # 원하는 동작 수행

        pixmap = QPixmap("result.jpg")
        self.imageLabel1.setVisible(False)
        self.imageLabel2.setVisible(False)
        self.imageLabel3.setVisible(True)
        self.imageLabel3.setPixmap(pixmap.scaled(512, 512, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def run_ai(self, content, style):
        # 데이터를 불러옵니다.
        dr = data_reader.DataReader(content, style)

        # Hub로부터 style transfer 모듈을 불러옵니다.
        hub_module = hub.load(
            'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1'
        )

        # 모듈에 이미지를 삽입해 Style Transfer를 실시합니다.
        stylized_image = hub_module(dr.content, dr.style)[0]

        # 결과를 출력합니다.
        result = data_reader.tensor_to_image(stylized_image)

        # 결과를 저장합니다.
        result.save("result.jpg")



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()