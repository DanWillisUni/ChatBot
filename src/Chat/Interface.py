from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QLineEdit, QGridLayout
import datetime

from src.Engine import KEngine

from pymitter import EventEmitter

eventEmitter = EventEmitter()

class EngineWorker(QObject):

    def __init__(self, ui):
        super(EngineWorker, self).__init__()

        self.engine = KEngine(ui)
        self.start.connect(self.run)

    start = pyqtSignal(str)

    @pyqtSlot()
    def run(self):
        self.engine.reset()
        self.engine.run()


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

        self.show()

        # https://stackoverflow.com/questions/20324804/how-to-use-qthread-correctly-in-pyqt-with-movetothread
        self.engine_thread = QThread()
        self.engine_thread.start()

        self.engine_worker = EngineWorker(self)

        self.send_button.clicked.connect(lambda: self.engine_worker.engine.set_input(self.process_response("You")))
        self.chat_line.returnPressed.connect(self.send_button.click)

        self.engine_worker.moveToThread(self.engine_thread)

        self.engine_worker.start.emit("hello")

    def send_message(self, sender, message):
        now = datetime.datetime.now()
        self.text_area.append(sender + ': (' + str(now.hour) + ':' + str(now.minute) + ')')
        self.text_area.append('    ' + message)
        self.text_area.append('')

    def process_response(self, sender):
        response = self.chat_line.text()
        self.send_message(sender, response)
        self.chat_line.clear()
        return response


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
