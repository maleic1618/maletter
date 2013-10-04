#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from twython import Twython, TwythonStreamer
from secretkey import *
import threading
import functools
import re
from StringIO import StringIO
import Tkinter
from tkFileDialog import *
from urllib import urlopen
import io
from Tab import TweetList, TweetListItem
from home_tab import *
from reply_tab import *
from faved_tab import *
from twtext import *
from detailtextbox import *

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        me = self.api.get_account_settings()
        self.mystatus = self.api.show_user(screen_name=me['screen_name'])
        self.myid = self.mystatus['id']
        self.status_array = []
        self.reply_status = None
        self.img = None

        self.initUI()

        init_status = self.api.get_home_timeline(count=20)
        for status in init_status[::-1]:
            self.status_received(status)

    def initUI(self):

        self.twlist = HomeTab(self)
        self.replylist = ReplyTab(self)
        self.actlist = ActTab(self)
        self.detailtext=DetailTextBox(self)
        self.twtext=TweetTextBox(self)

        self.detailtext.setGeometry(2,402,496,76)
        self.twtext.setGeometry(0,480,400,60)

        self.mediabutton = QtGui.QPushButton(self)
        self.mediabutton.setGeometry(450,480,50,20)
        self.mediabutton.setText(u'画像')
        self.mediabutton.clicked.connect(self.set_media)

        self.texbutton = QtGui.QPushButton(self)
        self.texbutton.setGeometry(400,480,50,20)
        self.texbutton.setText(u'TeX')
        self.texbutton.clicked.connect(self.set_tex)

        self.twtab=QtGui.QTabWidget(self)
        self.twtab.addTab(self.twlist, self.twlist.tabname)
        self.twtab.addTab(self.replylist, self.replylist.tabname)
        self.twtab.addTab(self.actlist, self.actlist.tabname)
        self.twtab.currentChanged.connect(self.current_tab_changed)
        self.twtab.setGeometry(0,0,500,400)

        self.setFixedSize(500,540)
        self.move(300,300)
        self.setWindowTitle('maletter')
        self.show()

    def status_received(self, status):
        self.twlist.on_status(status)
        self.replylist.on_status(status)
        self.actlist.on_status(status)

        #取得したstatusをstatus_arrayに保存
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                self.status_array.append(status)
                if status.has_key('retweeted_status') == True:
                    self.status_array.append(status['retweeted_status'])
        elif status['event'] == 'favorite':
            self.status_array.append(status['target_object'])

    def change_tab_name(self, tab_widget, newname):
        index = self.twtab.indexOf(tab_widget)
        self.twtab.setTabText(index, newname)

    def current_tab_changed(self, index):
        self.twtab.widget(index).tab_activated()

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
            #Error Message
            pass

    def set_media(self):
        root = Tkinter.Tk()
        root.withdraw()
        img_path = askopenfilename(filetypes = [(u'画像ファイル', ('.png', '.jpg', '.jpeg', '.gif'))])
        with open(img_path, 'rb') as f:
            self.img = f.read()

    def set_tex(self):
        tex = raw_input('数式を入力')
        tex = tex.replace('+', '%2B')
        base_url = 'http://chart.apis.google.com/chart'
        url_ext = 'cht=tx&chl=' + tex
        opener = urlopen(base_url, url_ext.encode('utf-8'))
        self.img = opener.read()

    def get_status(self, twid):
        for status in self.status_array:
            if status.has_key('id') == False: print status
            if status['id'] == twid:
                return status
        status = api.show_status(id = twid)
        self.status_array.append(status)
        return status

    def show_text(self, text):
        self.detailtext.setText(text)

    def show_html(self, htmltext):
        self.detailtext.setHtml(htmltext)

    def get_textbox_text(self):
        return self.twtext.toPlainText()

class MyStreamer(TwythonStreamer):

    def __init__(self, cls, *args):
        super(MyStreamer, self).__init__(*args)
        self.mw = cls

    def on_success(self, status):
        self.mw.status_received(status)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    mw = MainWindow(api_cls=api)

    stream = MyStreamer(mw, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    twit = threading.Thread(target=stream.user)
    twit.start()
    app.exec_()
    stream.disconnect() #終了したらユーザーストリームを切ること
