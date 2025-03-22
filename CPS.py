import sys
import math
import time
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from pynput import keyboard, mouse


class KeySignals(QObject):
    update_key = pyqtSignal(str, bool)
    update_click = pyqtSignal()


class KeyDetector:
    def __init__(self):
        self.signals = KeySignals()
        self.key_states = {
            'w': False,
            'a': False,
            's': False,
            'd': False,
            'space': False,
            'mouse': False
        }
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click
        )

    def on_press(self, key):
        try:
            k = key.char.lower()
        except AttributeError:
            if key == keyboard.Key.space:
                k = 'space'
            else:
                return
        if k in self.key_states and not self.key_states[k]:
            self.key_states[k] = True
            self.signals.update_key.emit(k, True)

    def on_release(self, key):
        try:
            k = key.char.lower()
        except AttributeError:
            if key == keyboard.Key.space:
                k = 'space'
            else:
                return
        if k in self.key_states and self.key_states[k]:
            self.key_states[k] = False
            self.signals.update_key.emit(k, False)

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.key_states['mouse'] = pressed
            self.signals.update_key.emit('mouse', pressed)
            if pressed:
                self.signals.update_click.emit()

    def start(self):
        self.keyboard_listener.start()
        self.mouse_listener.start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initTimer()
        self.initDetector()
        self.click_times = []  # 存储每次点击的时间戳
        self.time_window = 1  # 时间窗口，单位：秒

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 175);")
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.buttons = {}
        self.create_button('W', 175, 600)
        self.create_button('A', 125, 650)
        self.create_button('S', 175, 650)
        self.create_button('D', 225, 650)
        self.buttons['space'] = QLabel(self)
        self.buttons['space'].setGeometry(125, 700, 150, 50)
        self.buttons['space'].setAlignment(Qt.AlignCenter)
        self.buttons['space'].setText('Spacebar')
        self.set_button_style('space', False)
        self.buttons['cps'] = QLabel(self)
        self.buttons['cps'].setGeometry(125, 750, 150, 50)
        self.buttons['cps'].setAlignment(Qt.AlignCenter)
        self.buttons['cps'].setText('CPS: 0.0')
        self.set_button_style('cps', False)

    def create_button(self, name, x, y):
        btn = QLabel(self)
        btn.setGeometry(x, y, 50, 50)
        btn.setAlignment(Qt.AlignCenter)
        btn.setText(name)
        self.buttons[name] = btn
        self.set_button_style(name, False)

    def set_button_style(self, name, pressed):
        color = '#FFFFFF' if pressed else '#010101'
        text_color = '#010101' if pressed else '#FFFFFF'
        if name == 'cps':
            style = f"""
                background-color: {color};
                color: {text_color};
                border: 3px solid;
                border-radius: 5px;
                font: bold 15px 'Comic Sans MS';
            """
        else:
            style = f"""
                background-color: {color};
                color: {text_color};
                border: 3px solid;
                border-radius: 5px;
                font: bold 15px 'Comic Sans MS';
            """
        self.buttons[name].setStyleSheet(style)

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(10)  # 每10毫秒更新一次UI

    def initDetector(self):
        self.detector = KeyDetector()
        self.detector.signals.update_key.connect(self.handle_key_event)
        self.detector.signals.update_click.connect(self.handle_click)
        self.detector.start()

    def handle_key_event(self, key, pressed):
        if key in ['w', 'a', 's', 'd', 'space', 'mouse']:
            if key == 'mouse':
                self.set_button_style('cps', pressed)
            else:
                self.set_button_style(
                    key.upper() if len(key) == 1 else key, pressed)

    def handle_click(self):
        # 每次点击记录当前时间
        self.click_times.append(time.time())

    def rgb(self, t, tick):
        r = math.sin(t + tick) * 127.5 + 128
        g = math.sin(t + tick + 2) * 127.5 + 128
        b = math.sin(t + tick + 4) * 127.5 + 128
        return QColor(int(r), int(g), int(b))

    def update_ui(self):
        current_time = time.time()
        # 移除超过1秒的旧点击记录
        self.click_times = [
            t for t in self.click_times if current_time - t <= self.time_window]
        cps = len(self.click_times)  # 过去1秒内的点击次数即为CPS
        self.buttons['cps'].setText(f"CPS: {cps:.1f}")

        # 更新边框颜色
        for i, key in enumerate(['W', 'A', 'S', 'D', 'space', 'cps']):
            color = self.rgb(current_time, i * 50)
            self.buttons[key].setStyleSheet(
                self.buttons[key].styleSheet(
                ) + f"border-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
