#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from PyQt4 import QtGui, QtCore
import threading

def get_oauth():
    consumer_key   =''
    consumer_secret  =''
    access_key =''
    access_secret  =''
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        self.myid=api.me().id
        self.twarray = []

        self.initUI()

    def initUI(self):

        self.twlist=QtGui.QTreeWidget()
        self.twlist.setColumnCount(2)
        self.twlist.setHeaderLabels(['UserID','Tweet' ])
        self.replylist=QtGui.QTreeWidget()
        self.replylist.setColumnCount(2)
        self.replylist.setHeaderLabels(['Reply from', 'Tweet'])
        self.actlist=QtGui.QTreeWidget()
        self.actlist.setColumnCount(2)
        self.actlist.setHeaderLabels(['Faved by', 'Your Tweet'])
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
        if hasattr(status, "event") == False:
            item1 = QtGui.QTreeWidgetItem([status.user.screen_name, status.text])
            item2 = QtGui.QTreeWidgetItem([status.user.screen_name, status.text])
            self.twlist.insertTopLevelItem(0, item1)
            self.twarray.insert(0, status)
            if status.in_reply_to_user_id == self.myid:
                self.replylist.insertTopLevelItem(0, item2)

        elif status.event == 'favorite':
            if status.target['id'] == self.myid:
                item1 = QtGui.QTreeWidgetItem([status.source['screen_name'], status.target_object['text']])
                self.actlist.insertTopLevelItem(0, item1)


    def tweet(self, status):
        self.api.update_status(status)

    def twupdate(self):
        self.tweet(unicode(self.twtext.text()))
        self.twtext.setText('')

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_S and e.modifiers() == QtCore.Qt.ControlModifier:
            row = self.twlist.currentIndex().row()
            self.twlist.currentItem().setTextColor(0, QtGui.QColor(255,0,0))
            self.twlist.currentItem().setTextColor(1, QtGui.QColor(255,0,0))
            fav = self.api.create_favorite(self.twarray[row].id)

        if e.key() == QtCore.Qt.Key_R and e.modifiers() == QtCore.Qt.ControlModifier:
            row = self.twlist.currentIndex().row()
            self.twlist.currentItem().setTextColor(0, QtGui.QColor(0,255,0))
            self.twlist.currentItem().setTextColor(1, QtGui.QColor(0,255,0))
            rt = self.api.retweet(self.twarray[row].id)

class StreamListener(StreamListener):

    def __init__(self, cls):
        super(StreamListener, self).__init__()
        self.mw = cls

    def on_status(self, status):
        self.mw.append_status(status)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    auth = get_oauth()
    api=tweepy.API(auth)
    mw = MainWindow(api_cls=api)
    stream = Stream(auth, StreamListener(mw), secure=True)
    twit = threading.Thread(target=stream.userstream)
    twit.start()
    app.exec_()
