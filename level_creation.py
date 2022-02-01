import sys
from PyQt5.QtWidgets import *
from event import Signal


class Create(QWidget):
    def __init__(self):
        super().__init__()
        print('init_create')
        self.level_chosen = Signal()
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle("Qtextedit use")

        self.text = QTextEdit()
        self.btn1 = QPushButton("Показать текст")
        self.btn2 = QPushButton("Показать HTML")

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        self.setLayout(layout)

        self.btn1.clicked.connect(self.click1)
        self.btn2.clicked.connect(self.click2)

    def click1(self):
        name = '123'
        f = open("data/levels/" + name + ".txt", 'w')
        t_map = self.text.toPlainText()
        f.write(t_map)
        f.close()
        # self.text.setPlainText("Hello")

    def click2(self):
        self.text.setHtml("<font color='red' size='9'>Hello</font>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Create()
    form.show()
    sys.exit(app.exec_())
