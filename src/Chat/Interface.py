from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QLineEdit, QGridLayout
import datetime


class ChatBotWindow(QWidget):

    def __init__(self):
        super(ChatBotWindow, self).__init__()
        self.text_area = QTextEdit()
        self.chat_line = QLineEdit()
        self.send_button = QPushButton("Send")

        self.setWindowTitle("Train ChatBot")
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.setLayout(Layout(self.text_area, self.chat_line, self.send_button))

        self.send_button.clicked.connect(lambda: self.process_send("You"))
        self.chat_line.returnPressed.connect(self.send_button.click)

        self.show()

    def process_send(self, sender):
        now = datetime.datetime.now()
        self.text_area.append(sender + ': (' + str(now.hour) + ':' + str(now.minute) + ')')
        self.text_area.append('    ' + self.chat_line.text())
        self.text_area.append('')
        self.chat_line.clear()


class Layout(QGridLayout):
    def __init__(self, text_area, chat_line, send_button):
        super(Layout, self).__init__()
        self.addWidget(text_area, 0, 0, 1, -1)
        self.addWidget(chat_line, 1, 0)
        self.addWidget(send_button, 1, 1)


if __name__ == '__main__':
    app = QApplication([])
    window = ChatBotWindow()
    app.exec()
