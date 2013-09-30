#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from twython import Twython, TwythonStreamer
from secretkey import *
import threading
import functools

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        me = self.api.get_account_settings()
        self.myid = self.api.show_user(screen_name=me['screen_name'])['id']
        self.tweet_array = []
        self.reply_array = []
        self.loaded_array = []
        self.reply_status = []

        self.initUI()

        init_status = self.api.get_home_timeline(count=20)
        for status in init_status[::-1]:
            self.append_status(status)

    def initUI(self):

        self.twlist=QtGui.QTreeWidget()
        self.twlist.setColumnCount(3)
        self.twlist.setHeaderLabels(['UserID', 'Tweet', 'status ID'])
        self.twlist.setColumnHidden(2, True)
        self.twlist.currentItemChanged.connect(functools.partial(self.show_tweet, list=self.twlist, status_array=self.tweet_array))
        self.twlist.itemClicked.connect(functools.partial(self.show_tweet, list=self.twlist, status_array=self.tweet_array))
        self.twlist.itemDoubleClicked.connect(functools.partial(self.set_reply, list=self.twlist, status_array=self.tweet_array))

        self.replylist=QtGui.QTreeWidget()
        self.replylist.setColumnCount(3)
        self.replylist.setHeaderLabels(['Reply from', 'Tweet', 'status ID'])
        self.replylist.setColumnHidden(2, True)
        self.replylist.currentItemChanged.connect(functools.partial(self.show_tweet, list=self.replylist, status_array=self.reply_array))
        self.replylist.itemClicked.connect(functools.partial(self.show_tweet, list=self.replylist, status_array=self.reply_array))
        self.replylist.itemDoubleClicked.connect(functools.partial(self.set_reply, list=self.replylist, status_array=self.reply_array))

        self.actlist=QtGui.QTreeWidget()
        self.actlist.setColumnCount(3)
        self.actlist.setHeaderLabels(['Faved by', 'Your Tweet', 'status ID'])
        self.actlist.setColumnHidden(2, True)

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
                if status.has_key('retweeted_status') == False:
                    item1 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text'].replace('\n', ' '), status['id_str']])
                    item2 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text'].replace('\n', ' '), status['id_str']])
                    self.twlist.insertTopLevelItem(0, item1)
                    self.tweet_array.insert(0, status)
                    if status['in_reply_to_status_id']!=None:
                        reply_item = self.twlist.topLevelItem(0)
                        in_reply_to_status = self.get_status(status['in_reply_to_status_id'])
                        if in_reply_to_status != None:
                            item_add = QtGui.QTreeWidgetItem([in_reply_to_status['user']['screen_name'], in_reply_to_status['text'], in_reply_to_status['id_str']])
                            reply_item.addChild(item_add)

                    if status['in_reply_to_user_id'] == self.myid:
                        self.replylist.insertTopLevelItem(0, item2)
                        self.reply_array.insert(0,status)
                else:
                    scname = status['retweeted_status']['user']['screen_name']
                    retext = status['retweeted_status']['text']
                    item1 = QtGui.QTreeWidgetItem([scname, retext.replace('\n', ' ')+' (Retweeted by @'+status['user']['screen_name']+')', status['id_str']])
                    item1.setTextColor(0, QtGui.QColor(0,128,0))
                    item1.setTextColor(1, QtGui.QColor(0,128,0))
                    self.twlist.insertTopLevelItem(0, item1)
                    self.tweet_array.insert(0, status)

        elif status['event'] == 'favorite':
            if status['target']['id'] == self.myid:
                item1 = QtGui.QTreeWidgetItem([status['source']['screen_name'], status['target_object']['text'], status['id_str']])
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

    def show_tweet(self, list, status_array):
        current_index = list.currentIndex()
        current_item = list.currentItem()
        current_id = current_item.text(2)
        status = self.get_status(current_id)

        username = status['user']['screen_name']
        userid = status['user']['name']
        texttmp = status['text']

        if status.has_key("retweeted_status") == False:
            self.selecttext.setText(username+':'+userid+'\n'+texttmp)
        else:
            reusername = status['retweeted_status']['user']['screen_name']
            reuserid = status['retweeted_status']['user']['name']
            retexttmp = status['retweeted_status']['text']
            self.selecttext.setText(reusername+':'+reuserid+'\n'+retexttmp+'\n\n(Retweeted by @'+username+')')


        #load replytweet
        if status['in_reply_to_status_id'] != None and current_item.childCount() == 0:
            reply_status = api.show_status(id=status['in_reply_to_status_id'])
            additem = QtGui.QTreeWidgetItem([reply_status['user']['screen_name'], reply_status['text'], reply_status['id_str']])
            current_item.addChild(additem)
            self.loaded_array.append(reply_status)

    def set_reply(self, list, status_array):
        current_id = list.currentItem().text(2)
        status = get_status(current_id)
        self.twtext.setText('@'+self.reply_status['user']['screen_name']+' '+self.twtext.text())
        self.twtext.setFocus()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_S and e.modifiers() == QtCore.Qt.ControlModifier:
            current_item = self.twlist.currentItem()
            current_item.setTextColor(0, QtGui.QColor(255,0,0))
            current_item.setTextColor(1, QtGui.QColor(255,0,0))
            fav = self.api.create_favorite(id=int(current_item.text(2)))

        if e.key() == QtCore.Qt.Key_R and e.modifiers() == QtCore.Qt.ControlModifier:
            current_item = self.twlist.currentItem()
            rt = self.api.retweet(id=int(current_item.text(2)))

    def get_status(self, twid):
        for status in self.tweet_array:
            if status['id_str'] == str(twid):
                return status
        for status in self.loaded_array:
            if status['id_str'] == str(twid):
                return status
        return None

    def get_alllist(self, list): #list.item()? <-Protected Function
        all_list = []
        for i in range(list.topLevelItemCount):
            all_list.insert(0, list.topLevelItem(i))
        return all_list

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
