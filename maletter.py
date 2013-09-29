#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from twython import Twython, TwythonStreamer
from secretkey import *
import threading

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        me = self.api.get_account_settings()
        self.myid = self.api.show_user(screen_name=me['screen_name'])['id']
        self.twarray = []
        self.reply_status=[]

        self.initUI()

    def initUI(self):

        self.twlist=QtGui.QTreeWidget()
        self.twlist.setColumnCount(2)
        self.twlist.setHeaderLabels(['UserID','Tweet' ])
        self.twlist.itemClicked.connect(self.show_tweet)
        self.twlist.itemDoubleClicked.connect(self.set_reply)
        self.replylist=QtGui.QTreeWidget()
        self.replylist.setColumnCount(2)
        self.replylist.setHeaderLabels(['Reply from', 'Tweet'])
        self.actlist=QtGui.QTreeWidget()
        self.actlist.setColumnCount(2)
        self.actlist.setHeaderLabels(['Faved by', 'Your Tweet'])
        self.selecttext=QtGui.QTextEdit(self)
        self.selecttext.setReadOnly(True)
        self.selecttext.setGeometry(2,402,496,76)
        self.twtext=QtGui.QLineEdit(self)
        self.twtext.setGeometry(0,480,500,20)
        self.twtext.returnPressed.connect(self.twupdate)

        self.twtab=QtGui.QTabWidget(self)
        self.twtab.addTab(self.twlist, u"ホーム")
        self.twtab.addTab(self.replylist, u"リプライ")
        self.twtab.addTab(self.actlist, u"ふぁぼられ")
        self.twtab.setGeometry(0,0,500,400)

        self.setGeometry(300,300,500,500)
        self.setWindowTitle('maletter')
        self.show()

    def append_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                item1 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text']])
                item2 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text']])
                self.twlist.insertTopLevelItem(0, item1)
                self.twarray.insert(0, status)
                if status['in_reply_to_user_id'] == self.myid:
                    self.replylist.insertTopLevelItem(0, item2)

        elif status['event'] == 'favorite':
            if status['target']['id'] == self.myid:
                item1 = QtGui.QTreeWidgetItem([status['source']['screen_name'], status['target_object']['text']])
                self.actlist.insertTopLevelItem(0, item1)


    def tweet(self, posttext):
        if self.reply_status != []:
            if not(posttext.find('@'+self.reply_status['user']['screen_name'])):
                self.api.update_status(status=posttext, in_reply_to_status_id=self.reply_status['id'])
            else:
                self.api.update_status(status=posttext)
            self.reply_status =[]
        else:
            self.api.update_status(status=posttext)

    def twupdate(self):
        self.tweet(unicode(self.twtext.text()))
        self.twtext.setText('')

    def show_tweet(self):
        row = self.twlist.currentIndex().row()
        status=self.twarray[row]
        self.selecttext.setText(status['user']['screen_name']+':'+status['user']['name']+'\n'+status['text'])

    def set_reply(self):
        row = self.twlist.currentIndex().row()
        self.reply_status = self.twarray[row]
        self.twtext.setText('@'+self.reply_status['user']['screen_name']+' '+self.twtext.text())
        self.twtext.setFocus()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_S and e.modifiers() == QtCore.Qt.ControlModifier:
            row = self.twlist.currentIndex().row()
            self.twlist.currentItem().setTextColor(0, QtGui.QColor(255,0,0))
            self.twlist.currentItem().setTextColor(1, QtGui.QColor(255,0,0))
            fav = self.api.create_favorite(id=self.twarray[row]['id'])

        if e.key() == QtCore.Qt.Key_R and e.modifiers() == QtCore.Qt.ControlModifier:
            row = self.twlist.currentIndex().row()
            self.twlist.currentItem().setTextColor(0, QtGui.QColor(0,128,0))
            self.twlist.currentItem().setTextColor(1, QtGui.QColor(0,128,0))
            rt = self.api.retweet(id=self.twarray[row]['id'])

class MyStreamer(TwythonStreamer):

    def __init__(self, cls, *args):
        super(MyStreamer, self).__init__(*args)
        self.mw = cls

    def on_success(self, status):
        self.mw.append_status(status)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    mw = MainWindow(api_cls=api)

    stream = MyStreamer(mw, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    twit = threading.Thread(target=stream.user)
    twit.start()
    app.exec_()
    stream.disconnect() #終了したらユーザーストリームを切ること
