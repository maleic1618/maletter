#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from twython import Twython, TwythonStreamer, TwythonError
from secretkey import *
from StringIO import StringIO
import io
from plugin_manager import *
from tab_widget import TweetListMenu

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        me = self.api.get_account_settings()
        self.mystatus = self.api.show_user(screen_name=me['screen_name'])
        self.myid = self.mystatus['id']
        self.status_array = []
        self.img = None
        self.preview = QtGui.QPixmap()
        self.buttoncount = 0
        self.init_menu()
        self.initUI()

        self.streamer = MyStreamer(self, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        self.streamer_thread = StreamerThread(streamer=self.streamer, on_finished=self.streamer.disconnect)
        self.streamer_thread.start()

        init_status = self.api.get_home_timeline(count=20)
        for status in init_status[::-1]:
            self.status_received(status)

    def closeEvent(self, event):
        return QtGui.QMainWindow.closeEvent(self, event)

    def init_menu(self):
        """
        Widgetのコンテキストメニューのインスタンスを生成しておく．
        後にWidget部分をフォルダにまとめたときはplugin_managerみたいなので
        まとめて管理するが，今は少ないのでここにまとめておく
        """
        self.menu = {}
        self.menu['TweetListMenu'] = TweetListMenu(self)

    def initUI(self):
        self.detailtext=DetailTextBox()
        self.detailtext.setFixedHeight(80)
        self.replytext = ReplyTextBox()
        self.picture_prv = QtGui.QLabel()
        self.picture_prv.setFixedSize(100, 80)
        self.picture_prv.setHidden(True)
        self.picture_prv.setPixmap(self.preview)
        self.twtext=TweetTextBox(self)
        self.twtext.setFixedHeight(80)

        buttonwidget = QtGui.QWidget()
        buttonwidget.setFixedSize(100, 80)
        self.buttonlayout = QtGui.QGridLayout()
        buttonwidget.setLayout(self.buttonlayout)

        detailtext_layout = QtGui.QHBoxLayout()
        detailtext_layout.addWidget(self.detailtext)
        detailtext_layout.addWidget(self.picture_prv)
        detailtext_layout.setMargin(0)

        detailtext_widget = QtGui.QWidget()
        detailtext_widget.setLayout(detailtext_layout)
        detailtext_widget.setFixedHeight(80)

        self.twtab=QtGui.QTabWidget(self)
        self.twtab.currentChanged.connect(self.current_tab_changed)

        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(self.twtab,        0,0, 1,2)
        self.grid.addWidget(self.replytext,    1,0, 1,2)
        self.grid.addWidget(detailtext_widget, 2,0, 1,2)
        self.grid.addWidget(self.twtext,       3,0)
        self.grid.addWidget(buttonwidget,      3,1)
        self.grid.setMargin(5)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(self.grid)
        self.setCentralWidget(central_widget)

        self.plugin_mng = PluginManager('./plugin', ['on_status'])
        self.plugin = {}
        for cls_name in self.plugin_mng.get_plugin_names():
            #インスタンスを生成
            self.plugin[cls_name] = self.plugin_mng.plugin_dict[cls_name](self)

        self.setWindowTitle('maletter')
        self.show()

    def add_tab(self, widget, name):
        self.twtab.addTab(widget, name)

    def add_button(self, button):
        self.buttonlayout.addWidget(button, self.buttoncount, 0)
        self.buttoncount += 1

    def set_reply(self, status):
        self.replytext.set_reply(status)

    def change_tab_name(self, widget, newname):
        index = self.twtab.indexOf(widget)
        self.twtab.setTabText(index, newname)

    def current_tab_changed(self, index):
        self.twtab.widget(index).tab_activated()

    def get_textbox_text(self):
        return unicode(self.twtext.toPlainText())

    def set_textbox_text(self, text):
        self.twtext.setText(text)

    def show_text(self, text):
        self.detailtext.setText(text)

    def show_html(self, htmltext):
        self.detailtext.setHtml(htmltext)

    def set_textbox_focus(self):
        self.twtext.setFocus()

    def get_reply_status(self):
        return self.replytext.reply_status

    def set_reply_status(self, status):
        self.replytext.set_reply_status(status)

    def delete_reply_status(self):
        self.replytext.delete_reply_status()

    def get_image_data(self):
        return self.img

    def set_image_data(self, image):
        io_img = StringIO(image)
        prv_suc = self.preview.loadFromData(io_img.getvalue())
        if prv_suc == False:
            print 'Error:set_image_data'
            self.delete_image_data()
            return
        self.preview.scaled(100, 80, QtCore.Qt.KeepAspectRatio)
        self.img = image
        self.picture_prv.setPixmap(self.preview)
        self.picture_prv.setHidden(False)

    def delete_image_data(self):
        self.img = None
        self.preview.detach()
        self.picture_prv.setHidden(True)

    def status_received(self, status):
        for cls in self.plugin.values():
            cls.on_status(status)

        #取得したstatusをstatus_arrayに保存
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                self.status_array.append(status)
                if status.has_key('retweeted_status') == True:
                    self.status_array.append(status['retweeted_status'])
        elif status['event'] == 'favorite':
            self.status_array.append(status['target_object'])

    def update_status(self, posttext, in_reply_to_status_id=None, image=None):
        posttext = unicode(posttext)
        try:
            if image == None:
                if in_reply_to_status_id == None:
                    self.api.update_status(status = posttext)
                else:
                    self.api.update_status(status = posttext, in_reply_to_status_id = in_reply_to_status_id)
            else:
                if in_reply_to_status_id == None:
                    self.api.update_status_with_media(status = posttext, media = io.BytesIO(image))
                else:
                    self.api.update_status_with_media(status = posttext, in_reply_to_status_id = in_reply_to_status_id, media = io.BytesIO(image))
        except TwythonError as err:
            print err

        self.delete_image_data()
        self.delete_reply_status()

    def get_status(self, twid):
        for status in self.status_array:
            if status.has_key('id') == False: print status
            if status['id'] == twid:
                return status
        status = api.show_status(id = twid)
        self.status_array.append(status)
        return status

class TweetTextBox(QtGui.QTextEdit):
    def __init__(self, mainwindow):
        super(TweetTextBox, self).__init__()
        self.mw = mainwindow

    def key_pressed(self, event):
        self.default_key_event(event)

    def keyPressEvent(self, event):
        self.key_pressed(event)
        return QtGui.QTextEdit.keyPressEvent(self, event)

    def default_key_event(self, e):
        if e.key() == QtCore.Qt.Key_Return and e.modifiers() == QtCore.Qt.ControlModifier:
            self.tweet(unicode(self.toPlainText()))

        if e.key() == QtCore.Qt.Key_Escape:
            self.setText('')

    def tweet(self, posttext):
        image = self.mw.get_image_data()
        reply_status = self.mw.get_reply_status()
        if reply_status != None:
            self.mw.update_status(posttext = posttext, in_reply_to_status_id = reply_status['id'], image = image)
        else:
            self.mw.update_status(posttext = posttext, image = image)
        self.setText('')
        self.mw.delete_reply_status()
        self.mw.delete_image_data()

class DetailTextBox(QtGui.QTextBrowser):
    def __init__(self):
        super(DetailTextBox, self).__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)

class ReplyTextBox(QtGui.QLineEdit):
    def __init__(self):
        super(ReplyTextBox, self).__init__()
        self.setReadOnly(True)
        self.reply_status = None
        self.setHidden(True)

    def set_reply_status(self, status):
        if status != None:
            try:
                self.setText(u'Reply to @{id}:{tweettext}'.format(id = status['user']['screen_name'],
                    tweettext = status['text'].replace('\n', ' ')))
                self.reply_status = status
                self.setHidden(False)
            except:
                self.setText('Error!')
                self.reply_status = None
        else:
            self.delete_reply()

    def delete_reply_status(self):
        self.setText('')
        self.reply_status = None
        self.setHidden(True)

class MyStreamer(TwythonStreamer):
    def __init__(self, cls, *args):
        super(MyStreamer, self).__init__(*args)
        self.mw = cls

    def on_success(self, status):
        self.mw.status_received(status)

class StreamerThread(QtCore.QThread):
    def __init__(self, streamer, on_finished=None):
        super(StreamerThread, self).__init__()
        self.streamer = streamer
        self.on_terminal = on_finished

    def run(self):
        self.streamer.user()
    
    def terminate(self):
        if self.on_finished is not None:
            self.on_finished()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    mw = MainWindow(api_cls=api)

    app.exec_()
