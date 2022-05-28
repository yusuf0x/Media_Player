from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QApplication,
    QLineEdit,
    QPushButton,
    QStyle,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QShortcut,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import (
    QDir,
    Qt,
    QUrl,
    QSize,
    QTime,
    QProcess,
    QEvent,
)

from PyQt5.QtGui import QPalette, QKeySequence, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaMetaData
from PyQt5.QtMultimediaWidgets import QVideoWidget

import sys, os


class Player(QWidget):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        # make black background
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAcceptDrops(True)

        self.media_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.media_player.setVolume(80)
        self.video_widget = QVideoWidget(self)

        #
        self.left_label = QLineEdit("00:00:00")
        self.left_label.setReadOnly(True)
        self.left_label.setFixedWidth(70)
        self.left_label.setUpdatesEnabled(True)
        self.left_label.selectionChanged.connect(
            lambda: self.left_label.setSelection(0, 0)
        )
        # self.left_label.show()
        #
        self.right_label = QLineEdit("00:00:00")
        self.right_label.setReadOnly(True)
        self.right_label.setFixedWidth(70)
        self.right_label.setUpdatesEnabled(True)
        self.right_label.selectionChanged.connect(
            lambda: self.right_label.setSelection(0, 0)
        )
        # self.right_label.show()
        #

        self.play_button = QPushButton()
        # self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setIcon(QIcon('play.png'))
        self.play_button.setEnabled(False)
        self.play_button.setFixedWidth(32)
        self.play_button.setStyleSheet("background-color: black")
        self.play_button.clicked.connect(self.playVideo)
        # self.play_button.show()

        # slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        # setPosition
        self.slider.sliderMoved.connect(self.setPosition)
        # self.slider.show()

        self.clipboard = QApplication.clipboard()
        # for executing external command
        self.process = QProcess(self)

        #
        HorizonalLayout = QHBoxLayout()
        HorizonalLayout.addWidget(self.play_button)
        HorizonalLayout.addWidget(self.left_label)
        HorizonalLayout.addWidget(self.slider)
        HorizonalLayout.addWidget(self.right_label)
        #
        VerticalLayout = QVBoxLayout()
        VerticalLayout.addWidget(self.video_widget)
        VerticalLayout.addLayout(HorizonalLayout)

        self.setLayout(VerticalLayout)

        self.about = "©2022\ncreated by yusuf0x\n"

        # shortcut
        self.quit = QShortcut(QKeySequence("Q"), self)
        self.quit.activated.connect(QApplication.instance().quit)

        self.open = QShortcut(QKeySequence("O"), self)
        self.open.activated.connect(self.openFile)

        self.play = QShortcut(QKeySequence("P"), self)
        self.play.activated.connect(self.playVideo)

        self.full_screen = QShortcut(QKeySequence("F"), self)
        self.full_screen.activated.connect(self.fullScreen)

        self.about_me = QShortcut(QKeySequence("A"), self)
        self.about_me.activated.connect(self.About)

        self.show_slider_act = QShortcut(QKeySequence("S"), self)
        self.show_slider_act.activated.connect(self.show_hide_slider)

        self.arrow_key_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.arrow_key_left.activated.connect(self.skip_backward)
        self.arrow_key_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.arrow_key_right.activated.connect(self.skip_forward)
        self.arrow_key_up = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.arrow_key_up.activated.connect(self.volume_up)
        self.arrow_key_down = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.arrow_key_down.activated.connect(self.volume_down)

        self.play_url = QShortcut(QKeySequence("U"), self)
        self.play_url.activated.connect(self.play_from_url)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)

    def openFile(self):
        fileName, s = QFileDialog.getOpenFileName(
            self, "Open File", QDir.homePath() + "/Videos"
        )
        print(fileName)
        if fileName != "":
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.play_button.setEnabled(True)

    def playVideo(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def About(self):
        msg = QMessageBox.about(self, "Media Player", self.about)

    def show_hide_slider(self):
        if self.slider.isVisible():
            self.hide_slider()
        else:
            self.show_slider()

    def hide_slider(self):
        self.play_button.hide()
        self.left_label.hide()
        self.right_label.hide()
        self.slider.hide()
        pass

    def show_slider(self):
        self.play_button.show()
        self.left_label.show()
        self.right_label.show()
        self.slider.show()

    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(QIcon('pause.png'))
        else:
            self.play_button.setIcon(QIcon('play.png'))

    def positionChanged(self, positon):
        self.slider.setValue(positon)
        mtime = QTime(0, 0, 0, 0)
        mtime = mtime.addMSecs(self.media_player.position())
        self.left_label.setText(mtime.toString())

    def durationChanged(self, duration):
        print(duration)
        self.slider.setRange(0, duration)
        mtime = QTime(0, 0, 0, 0)
        mtime = mtime.addMSecs(self.media_player.duration())

        self.right_label.setText(mtime.toString())
        print(self.left_label.text())

    def setPosition(self, position):
        # self.media_player.setPosition(position)
        pass

    def handleError(self):
        self.play_button.setEnabled(False)
        msg = QMessageBox.about(
            self, "Player", "Error:" + self.media_player.errorString()
        )

    def mouseDoubleClickEvent(self, event):
        self.fullScreen()

    def fullScreen(self):
        if self.windowState() & Qt.WindowFullScreen:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.showNormal()
        else:
            self.showFullScreen()
            QApplication.setOverrideCursor(Qt.BlankCursor)

    def skip_forward(self):
        print("skip_forward")
        self.media_player.setPosition(self.media_player.position() + 1000 * 60)

    def skip_backward(self):
        print("skip_backward")
        self.media_player.setPosition(self.media_player.position() - 1000 * 60)

    def volume_up(self):
        self.media_player.setVolume(self.media_player.volume() + 10)
        print("Volume: " + str(self.media_player.volume()))

    def volume_down(self):
        self.media_player.setVolume(self.media_player.volume() - 10)
        print("Volume: " + str(self.media_player.volume()))

    # url playing
    def play_from_url(self):
        self.media_player.pause()
        self.url = self.clipboard.text()
        self.media_player.setMedia(QMediaContent(QUrl(self.url)))
        self.play_button.setEnabled(True)
        self.media_player.play()
        self.hide_slider()
        print(self.url)

    def get_youtube_url(self):
        command = "yt-dlp -f 'bv*[height<=480]+ba'" + self.clipboard.text()
        self.process.start(command)

    #
    def play_from_commandLine(self, fileName):
        fileName = os.getcwd() + "/" + fileName
        print(fileName)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
        self.play_button.setEnabled(True)
        self.media_player.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    player.setWindowTitle("media player")
    player.setGeometry(100, 300, 600, 380)
    player.setWindowIcon(QIcon("logo.jpg"))
    player.show()

    if len(sys.argv) > 1:
        player.play_from_commandLine(sys.argv[1])
    app.exec_()