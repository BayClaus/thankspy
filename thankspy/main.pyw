import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit, QMessageBox
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream
import ctypes
from pathlib import Path

def get_documents_folder():
    CSIDL_PERSONAL = 0x0005
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf)
    return Path(buf.value)

thanksto = []
recover = []

documents_folder = get_documents_folder()
filename = documents_folder / "THANKS.txt"

class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Background Viewer")
        self.setGeometry(200, 200, 700, 500)
        self.setWindowIcon(QIcon("gui/ico.png"))
        self.setFixedSize(700,500)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.thankstoviewer = QTextEdit(self)
        self.thankstoviewer.setGeometry(10, 10, 200, 450)
        self.thankstoviewer.setReadOnly(True)

        self.recoverviewer = QTextEdit(self)
        self.recoverviewer.setGeometry(220,10,200,450)
        self.recoverviewer.setReadOnly(True)

        self.refresh = QPushButton('Refresh', self)
        self.refresh.setGeometry(430,10,50,30)
        self.refresh.clicked.connect(self.refresh_pages)

        self.rules = QTextEdit(self)
        self.rules.setGeometry(430,45,260,260)
        self.rules.setReadOnly(True)
        self.load_file()
        
        # Timer:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_pages)
        self.timer.start(2000)

    def refresh_pages(self):
        self.thankstoviewer.clear()
        self.recoverviewer.clear()
        for i in thanksto:
            self.thankstoviewer.append(i)
        for i in recover:
            self.recoverviewer.append(i)
    def load_file(self):
        # Dosya yolunu belirleme
        file_path = 'gui/file.txt'
        
        # Dosyayı açma ve okuma
        try:
            file = QFile(file_path)
            if file.open(QFile.ReadOnly | QFile.Text):
                text_stream = QTextStream(file)
                content = text_stream.readAll()
                self.rules.setPlainText(content)
                file.close()
            else:
                self.rules.setPlainText("Unable to open file.")
        except Exception as e:
            self.rules.setPlainText(f"An error occurred: {e}")

class BasicWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_stylesheet("gui/style.qss")

    def init_ui(self):
        self.setWindowTitle("Thankspy")
        self.setGeometry(100, 100, 370, 370)
        self.setWindowIcon(QIcon("gui/ico.png"))
        self.setFixedSize(370,370)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.save = QPushButton('>', self)
        self.save.setGeometry(310, 5, 50, 50)

        self.remove = QPushButton('<', self)
        self.remove.setGeometry(310, 60, 50, 50)

        self.removeAll = QPushButton('X', self)
        self.removeAll.setGeometry(310,115, 26, 26)

        self.recovery = QPushButton('=', self)
        self.recovery.setGeometry(335, 115, 26, 26)

        self.viewer = QPushButton('View', self)
        self.viewer.setGeometry(310, 145, 50, 30)

        self.saver = QPushButton('Save', self)
        self.saver.setGeometry(310, 180, 50, 30)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Type in here...")
        self.input.setGeometry(5, 5, 300, 30)
        self.input.installEventFilter(self)

        self.list = QTextEdit(self)
        self.list.setGeometry(5, 40, 300, 325)
        self.list.setReadOnly(True)

        self.save.clicked.connect(self.add_to_list)
        self.remove.clicked.connect(self.remove_from_list)
        self.removeAll.clicked.connect(self.remove_all)
        self.recovery.clicked.connect(self.recovert)
        self.viewer.clicked.connect(self.view_secondpage)
        self.saver.clicked.connect(self.save_note)

    def load_stylesheet(self, path):
        with open(path, "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)
    def add_to_list(self):
        text = self.input.text()
        if len(text) > 0:
            if text not in thanksto:
                self.list.clear()
                thanksto.append(text)
                self.input.clear()
                self.input.setFocus()
                thanksto.sort()
                for i in thanksto:
                    self.list.append(i)
            else:
                self.show_timed_message("You can't add the same value", 1000)
                self.input.setFocus()
        else:
            self.show_timed_message("You can't add an empty value", 1000)
            self.input.setFocus()
    def remove_from_list(self):
        if self.input.text() in thanksto:
            thanksto.remove(self.input.text())
            self.list.clear()
            for i in thanksto:
                self.list.append(i)
            self.input.clear()
            self.input.setFocus()
        else:
            self.show_timed_message("This item not founded in list.", 1000)
            return
    def remove_all(self):
        for i in thanksto:
            recover.append(i)
            self.list.clear()
        thanksto.clear()
    def recovert(self):
        self.list.clear()
        for i in recover:
            thanksto.append(i)
        for i in thanksto:
            self.list.append(i) 
        recover.clear()
    def view_secondpage(self):
        self.second_window = SecondWindow()  # Yeni pencereyi oluştur
        self.second_window.show()
    def show_timed_message(self, message, timeout=3000):
        msg_box = QMessageBox(self)
        msg_box.setText(message)
        msg_box.setWindowTitle("Information:")
        msg_box.setModal(False)
        msg_box.show()

        QTimer.singleShot(timeout, msg_box.close)
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save.click()
        if event.key() == Qt.Key_Escape:
            self.remove.click()
    def save_note(self):
        with open(filename, 'w') as file:
            file.write("Thanks to:"+"\n")
            for i in thanksto:
                file.write("- " + i + "\n")
    # Uygulama çalıştırma
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec())