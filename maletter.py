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
        self.img = ''

        self.initUI()

        init_status = self.api.get_home_timeline(count=20)
        for status in init_status[::-1]:
            self.append_status(status)

    def initUI(self):

        self.twlist=QtGui.QTreeWidget()
        self.twlist.setColumnCount(3)
        self.twlist.setHeaderLabels(['UserID', 'Tweet', 'status ID'])
        self.twlist.setColumnHidden(2, True)
        self.twlist.currentItemChanged.connect(functools.partial(self.show_tweet, list=self.twlist))
        self.twlist.itemDoubleClicked.connect(functools.partial(self.set_reply, list=self.twlist))

        self.replylist=QtGui.QTreeWidget()
        self.replylist.setColumnCount(3)
        self.replylist.setHeaderLabels(['Reply from', 'Tweet', 'status ID'])
        self.replylist.setColumnHidden(2, True)
        self.replylist.currentItemChanged.connect(functools.partial(self.show_tweet, list=self.replylist))
        self.replylist.itemDoubleClicked.connect(functools.partial(self.set_reply, list=self.replylist))

        self.actlist=QtGui.QTreeWidget()
        self.actlist.setColumnCount(3)
        self.actlist.setHeaderLabels(['Faved by', 'Your Tweet', 'status ID'])
        self.actlist.setColumnHidden(2, True)
        self.actlist.currentItemChanged.connect(functools.partial(self.show_tweet, list=self.actlist))

        self.selecttext=QtGui.QTextBrowser(self)
        self.selecttext.setReadOnly(True)
        self.selecttext.setOpenExternalLinks(True)
        self.selecttext.setGeometry(2,402,496,76)

        self.twtext=QtGui.QLineEdit(self)
        self.twtext.setGeometry(0,480,400,20)
        self.twtext.returnPressed.connect(self.twupdate)

        self.mediabutton = QtGui.QPushButton(self)
        self.mediabutton.setGeometry(450,480,50,20)
        self.mediabutton.setText(u'画像')
        self.mediabutton.clicked.connect(self.set_media)

        self.mediabutton = QtGui.QPushButton(self)
        self.mediabutton.setGeometry(400,480,50,20)
        self.mediabutton.setText(u'TeX')
        self.mediabutton.clicked.connect(self.set_tex)

        self.twtab=QtGui.QTabWidget(self)
        self.twtab.addTab(self.twlist, u"ホーム")
        self.twtab.addTab(self.replylist, u"リプライ")
        self.twtab.addTab(self.actlist, u"ふぁぼられ")
        self.twtab.setGeometry(0,0,500,400)

        self.setFixedSize(500,500)
        self.move(300,300)
        self.setWindowTitle('maletter')
        self.show()

    def append_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                if status.has_key('retweeted_status') == False:
                    item_add2 = ''
                    item1 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text'].replace('\n', ' '), status['id_str']])
                    item2 = QtGui.QTreeWidgetItem([status['user']['screen_name'], status['text'].replace('\n', ' '), status['id_str']])
                    if status['in_reply_to_user_id'] == self.myid:
                        item1.setBackgroundColor(0, QtGui.QColor(255, 100, 25))
                        item1.setBackgroundColor(1, QtGui.QColor(255, 100, 25))
                    elif status['in_reply_to_user_id'] != None:
                        item1.setBackgroundColor(0, QtGui.QColor(255, 239, 133))
                        item1.setBackgroundColor(1, QtGui.QColor(255, 239, 133))
                    self.twlist.insertTopLevelItem(0, item1)
                    self.tweet_array.insert(0, status)
                    if status['in_reply_to_status_id']!=None:
                        reply_item = self.twlist.topLevelItem(0)
                        in_reply_to_status = self.get_status(status['in_reply_to_status_id'])
                        if in_reply_to_status != None:
                            item_add = QtGui.QTreeWidgetItem([in_reply_to_status['user']['screen_name'], in_reply_to_status['text'], in_reply_to_status['id_str']])
                            item_add2 = item_add
                            if in_reply_to_status['favorited'] == True:
                                item_add.setTextColor(0, QtGui.QColor(255,0,0))
                                item_add.setTextColor(1, QtGui.QColor(255,0,0))
                            reply_item.addChild(item_add)

                    if status['in_reply_to_user_id'] == self.myid:
                        if item_add2 != '':
                            item2.addChile(item_add2)
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
                item1 = QtGui.QTreeWidgetItem([status['source']['screen_name'], status['target_object']['text'], status['target_object']['id_str']])
                self.actlist.insertTopLevelItem(0, item1)
                self.loaded_array.append(status['target_object'])

    def tweet(self, posttext):
        reply_id=''

        if self.img == '':
            if self.reply_status != []:
                if not(posttext.find('@'+self.reply_status['user']['screen_name'])):
                    reply_id=self.reply_status['id']
                    self.api.update_status(status = posttext, in_reply_to_status_id = reply_id)
                else:
                    self.api.update_status(status = posttext)
            else:
                self.api.update_status(status = posttext)
        else:
            if self.reply_status != []:
                if not(posttext.find('@'+self.reply_status['user']['screen_name'])):
                    reply_id=self.reply_status['id']
                    self.api.update_status_with_media(status = posttext, in_reply_to_status_id = reply_id,
                        media = io.BytesIO(self.img))
                else:
                    self.api.update_status_with_media(status = posttext, media = io.BytesIO(self.img))
            else:
                self.api.update_status_with_media(status = posttext, media = io.BytesIO(self.img))
            self.img = ''

    def twupdate(self):
        self.tweet(unicode(self.twtext.text()))
        self.twtext.setText('')

    def show_tweet(self, list):
        current_item = list.currentItem()
        current_id = current_item.text(2)
        status = self.get_status(current_id)

        username = status['user']['screen_name']
        userid = status['user']['name']
        source = status['source']

        if status.has_key("retweeted_status") == False:
            texttmp = self.add_link_status(status)
            self.selecttext.setHtml(userid+':'+username+'<br>'+texttmp+'<br><br>(via '+source+')')
        else:
            reusername = status['retweeted_status']['user']['screen_name']
            reuserid = status['retweeted_status']['user']['name']
            retexttmp = self.add_link_status(status['retweeted_status'])
            re_source = status['retweeted_status']['source']
            self.selecttext.setHtml(reuserid+':'+reusername+'<br>'+retexttmp+'<br><br>(Retweeted by @'+username+', via ' +re_source+')')

        #load reply
        if status['in_reply_to_status_id'] != None and current_item.childCount() == 0:
            reply_status = api.show_status(id=status['in_reply_to_status_id'])
            additem = QtGui.QTreeWidgetItem([reply_status['user']['screen_name'], reply_status['text'], reply_status['id_str']])
            current_item.addChild(additem)
            self.loaded_array.append(reply_status)

    def set_reply(self, list):
        current_id = list.currentItem().text(2)
        status = self.get_status(current_id)
        if status['retweeted'] == True:
            status = status['retweeted_status']
        self.reply_status = status
        self.twtext.setText('@'+status['user']['screen_name']+' '+self.twtext.text())
        self.twtext.setFocus()

    def set_media(self):
        root = Tkinter.Tk()
        root.withdraw()
        img_path = askopenfilename(filetypes = [(u'画像ファイル', ('.png', '.jpg', '.jpeg', '.gif'))])
        with open(img_path, 'rb') as f:
            img = f.read()

    def set_tex(self):
        tex = raw_input('数式を入力')
        tex = tex.replace('+', '%2B')
        base_url = 'http://chart.apis.google.com/chart'
        url_ext = 'cht=tx&chl=' + tex
        opener = urlopen(base_url, url_ext.encode('utf-8'))
        self.img = opener.read()

    def keyPressEvent(self, e):
        current_list = self.twtab.currentWidget()
        current_item = current_list.currentItem()
        if current_item != None:
            current_id = current_item.text(2)
        if e.key() == QtCore.Qt.Key_S and e.modifiers() == QtCore.Qt.ControlModifier:
            current_item.setTextColor(0, QtGui.QColor(255,0,0))
            current_item.setTextColor(1, QtGui.QColor(255,0,0))
            fav = self.api.create_favorite(id=int(current_item.text(2)))

        if e.key() == QtCore.Qt.Key_R and e.modifiers() == QtCore.Qt.ControlModifier:
            rt = self.api.retweet(id=int(current_item.text(2)))

        if e.key() == QtCore.Qt.Key_R and int(e.modifiers()) == QtCore.Qt.ControlModifier+QtCore.Qt.ShiftModifier:
            status = self.get_status(current_id)
            if status.has_key("retweeted_status") == True:
                status = status['retweeted_status']
            if status['user']['protected'] == True:
                username = u'鍵'
            else:
                username = status['user']['screen_name']
            self.reply_status = status
            self.twtext.setText(self.twtext.text() + 'RT @' + username + ' ' + status['text'])
            self.twtext.setFocus()

        if e.key() == QtCore.Qt.Key_R and int(e.modifiers()) == QtCore.Qt.ControlModifier+QtCore.Qt.AltModifier:
            status = self.get_status(current_id)
            username = status['user']['screen_name']
            self.twtext.setText('https://twitter.com/'+username+'/status/'+current_id+' ' + self.twtext.text())
            self.twtext.setFocus()

    def get_status(self, twid):
        for status in self.tweet_array:
            if status['id_str'] == str(twid):
                return status
        for status in self.loaded_array:
            if status['id_str'] == str(twid):
                return status
        #status = api.show_status(int(twid))
        #self.loaded_array.append(status)
        return None

    def get_alllist(self, list): #list.item()? <-Protected Function
        all_list = []
        for i in range(list.topLevelItemCount):
            all_list.insert(0, list.topLevelItem(i))
        return all_list

    def add_hyperlink(self, text): #entities見たらいいので使わない
        r = re.compile(r"(http://[^ ]+)")
        return r.sub(r'<a href="\1">\1</a>', text)

    def add_link_status(self, status):
        entities_url = status['entities']['urls']
        text = status['text']
        if entities_url != []:
            for i in range(len(entities_url)):
                text = text.replace(entities_url[i]['url'],
                    '<a href="' + entities_url[i]['expanded_url'] + '">' + entities_url[i]['display_url'] + '</a>')
        if status['entities'].has_key('media') == True:
            entities_media = status['entities']['media']
            for i in range(len(entities_media)):
                text = text.replace(entities_media[i]['url'],
                    '<a href="' + entities_media[i]['expanded_url'] + '">' + entities_media[i]['display_url'] + '</a>')
        return text

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
