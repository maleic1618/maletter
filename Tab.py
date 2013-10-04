#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

"""
TweetList
検索結果を表示したり，他人のホーム表示等
ツイートのリストを表示するクラス．
リストのツイートについてはデフォルトでHomeタブなどと同じように動く．
何を追加するか，などを変えていけばいいかなと．
"""

class TweetList(QtGui.QTreeWidget):

    def __init__(self, mainwindow):
        self.mw = mainwindow

        super(TweetList, self).__init__(mainwindow)
        self.setColumnCount(2)
        self.currentItemChanged.connect(self.item_changed)
        self.itemDoubleClicked.connect(self.item_double_clicked)
        self.itemExpanded.connect(self.item_expanded)
        self.mystatus = self.mw.mystatus
        self.tabname = ''

    def item_changed(self, current_item, previous_item):
        status = self.get_status_from_id(current_item.status_id)
        self.show_status(status)

    def item_double_clicked(self, item):
        status = self.get_status_from_id(item.status_id)
        self.set_reply(status)

    def item_expanded(self, item):
        self.load_replied_tweet(item)

    def tab_activated(self):
        pass

    def keyPressEvent(self, e):
        self.default_key_event(e)

    def on_status(self, status):
        #UserStreamで流れてきたときの処理をここに書く．
        pass

#=================ここから下はdefaultで実装されてる関数===================
#=========================基本的に書き換えはなし==========================

    def change_header(self, id_name, textname):
        self.setHeaderLabels([id_name, textname])

    def show_text(self, text):
        self.mw.show_text(text)

    def show_html(self, htmltext):
        self.mw.show_html(htmltext)

    def set_textbox_text(self, text):
        self.mw.twtext.setText(text)

    def get_textbox_text(self):
        return self.mw.get_textbox_text()

    def create_favorite(self, status_id):
        self.mw.api.create_favorite(id = int(status_id))

    def create_retweet(self, status_id):
        self.mw.api.retweet(id = int(status_id))

    def get_status_from_id(self, status_id):
        return self.mw.get_status(status_id)

    def set_reply_status(self, status):
        self.mw.reply_status = status

    def set_textbox_focus(self):
        self.mw.twtext.setFocus()

    def change_tab_name(self, newname):
        self.mw.change_tab_name(self, newname)

    def append_status(self, status):
        #statusを渡すと，それをHomeと同じ形式でリストに追加．

        if status.has_key('retweeted_status') == False:
            item = TweetListItem(status['user']['screen_name'], status['text'].replace('\n', ' '), status['id'])
            if status['favorited'] == True:
                item.change_color(backgroundcolor=(255, 0, 0))
            if status['in_reply_to_user_id'] == self.mystatus['id']:
                item.change_color(backgroundcolor=(255, 170, 130))
            elif status['in_reply_to_user_id'] != None:
                item.change_color(backgroundcolor=(255, 239, 133))
        else:
            retweeted_status = status['retweeted_status']
            item = TweetListItem(retweeted_status['user']['screen_name'], retweeted_status['text'].replace('\n', ' '), status['id'])
            item.change_color(textcolor=(0, 128, 0))

        if status['in_reply_to_status_id'] != None:
            item_add = TweetListItem('', '', status['in_reply_to_status_id'])
            item.addChild(item_add)

        self.insertTopLevelItem(0, item)

    def append_item(self, screen_name, text, status_id, textcolor=None, backgroundcolor=None):
        item = TweetListItem(screen_name, text, status_id)
        item.change_color(textcolor, backgroundcolor)
        self.insertTopLevelItem(0, item)

    def get_current_status(self):
        current_item = self.currentItem()
        if current_item == None:
            return None
        return self.mw.get_status(current_item.status_id)

    def get_current_status_id(self):
        current_item = self.currentItem()
        if current_item == None:
            return
        return current_item.status_id

    def default_key_event(self, e):
        #ふぁぼとRTとリプライセットだけ．標準．
        current_item = self.currentItem()
        if current_item == None:
            return
        current_id = current_item.status_id

        if e.key() == QtCore.Qt.Key_S and e.modifiers() == QtCore.Qt.ControlModifier:
            try:
                fav = self.create_favorite(current_id)
                current_item.change_color(textcolor=(255,0,0))
            except TwythonError as err:
                #エラーメッセージ
                pass

        if e.key() == QtCore.Qt.Key_R and e.modifiers() == QtCore.Qt.ControlModifier:
            try:
                rt = self.create_retweet(current_id)
            except TwythonError as err:
                #エラーメッセージ
                pass

        if e.key() == QtCore.Qt.Key_Return:
            status = self.get_status_from_id(current_id)
            self.set_reply(status)

        if e.key() == QtCore.Qt.Key_R and int(e.modifiers()) == QtCore.Qt.ControlModifier+QtCore.Qt.ShiftModifier:
            status = self.get_status_from_id(current_id)
            if status.has_key('retweeted_status') == True:
                status = status['retweeted_status']
            if status['user']['protected'] == True:
                username = u'鍵'
            else:
                username = status['user']['screen_name']
            self.set_reply_status = status
            self.set_textbox_text(self.get_textbox_text() + 'RT @' + username + ' ' + status['text'])
            self.set_textbox_focus()

        if e.key() == QtCore.Qt.Key_R and int(e.modifiers()) == QtCore.Qt.ControlModifier+QtCore.Qt.AltModifier:
            status = self.get_status_from_id(current_id)
            if status.has_key('retweeted_status') == True:
                status = status['retweeted_status']
            username = status['user']['screen_name']
            self.set_textbox_text('https://twitter.com/'+username+'/status/'+status['id_str']+' ' + self.get_textbox_text())
            self.set_textbox_focus()

    def show_status(self, status):
        #statusを投げると通常の形式で詳細欄に表示
        userid = status['user']['screen_name']
        username = status['user']['name']
        source = status['source']

        if status.has_key('retweeted_status') == False:
            status_text = self.add_link_status(status)
            text = username+':'+userid+'<br>'+status_text+'<br><br>(via '+source+')'
        else:
            retweeted_userid = status['retweeted_status']['user']['screen_name']
            retweeted_username = status['retweeted_status']['user']['name']
            retweeted_text = self.add_link_status(status['retweeted_status'])
            retweeted_source = status['retweeted_status']['source']
            text = retweeted_username+':'+retweeted_userid+'<br>'+retweeted_text+'<br><br>(Retweeted by @'+userid+', via ' +retweeted_source+')'
        self.show_html(text)

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

    def add_hyperlink(self, text):
        r = re.compile(r"(http://[^ ]+)")
        return r.sub(r'<a href="\1">\1</a>', text)

    def set_reply(self, status):
        #statusを投げるとリプライをセット
        if status.has_key('retweeted_status') == True:
            status = status['retweeted_status']
        self.set_reply_status(status)
        previous_text = self.get_textbox_text()
        new_text = '@'+status['user']['screen_name'] + ' ' + previous_text
        self.set_textbox_text(new_text)
        self.set_textbox_focus()

    def load_replied_tweet(self, item):
        #ロード用．正直デフォの使い方以外に使い道はない気もする
        child = item.child(0)
        if child.text(0) != '':
            return
        replied_status = self.get_status_from_id(child.status_id)
        child.set_display_id(replied_status['user']['screen_name'])
        child.set_display_text(replied_status['text'])
        if replied_status['in_reply_to_status_id'] != None:
            item_add = TweetListItem('', '', replied_status['in_reply_to_status_id'])
            child.addChild(item_add)

class TweetListItem(QtGui.QTreeWidgetItem):
    def __init__(self, display_id='', display_text='', status_id=None):
        super(TweetListItem, self).__init__([display_id, display_text])
        self.status_id = status_id

    def set_display_id(self, id):
        self.setText(0, id)

    def set_display_text(self, text):
        self.setText(1, text)

    def change_color(self, textcolor=None, backgroundcolor=None):
        #textcolorはタプルで渡すこと
        if textcolor != None:
            self.setTextColor(0, QtGui.QColor(*textcolor))
            self.setTextColor(1, QtGui.QColor(*textcolor))
        if backgroundcolor != None:
            self.setBackgroundColor(0, QtGui.QColor(*backgroundcolor))
            self.setBackgroundColor(1, QtGui.QColor(*backgroundcolor))
