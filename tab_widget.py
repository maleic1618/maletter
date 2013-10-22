#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

class TweetList(QtGui.QTreeWidget):
    """
    TweetList
    ツイートのリストを表示するクラス．IDとTextの一覧．
    リストのツイートについてはデフォルトでHomeタブなどと同じように動く．
    mainクラス内でこのインスタンスを作って
    (mainの中で)__init__の中でadd_tab()を呼び出してタブに追加すること．
    また__init__でmainwindowとpluginを渡すこと．
    """

    def __init__(self, mainwindow, plugin):
        self.plugin = plugin
        self.mw = mainwindow

        super(TweetList, self).__init__(mainwindow)
        self.setColumnCount(2)
        self.currentItemChanged.connect(self.item_changed)
        self.itemDoubleClicked.connect(self.item_double_clicked)
        self.itemExpanded.connect(self.item_expanded)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

        self.mystatus = self.mw.mystatus
        self.menu = QtGui.QMenu(self)

    def item_changed(self, current_item, previous_item):
        if current_item.status_id == None:
            return
        status = self.get_status_from_id(current_item.status_id)
        self.show_status(status)

    def item_double_clicked(self, item):
        status = self.get_status_from_id(item.status_id)
        self.set_reply(status)

    def item_expanded(self, item):
        self.load_replied_tweet(item)

    def tab_activated(self):
        pass

    def keyPressEvent(self, event):
        """
        このリストがアクティブになっているときにキーが押されると呼び出されます
        """
        self.default_key_event(event)

    def change_header(self, id_name, textname):
        """
        リストのヘッダーを変更．
        """
        self.setHeaderLabels([id_name, textname])

    def on_context_menu(self, point):
        self.mw.menu['TweetListMenu'].execute(point, self)

    def append_status(self, status):
        """
        ツイート，またはリツイートstatusを渡すと
        それをHomeと同じ形式でリストに追加．
        """

        if status.has_key('retweeted_status') == False:
            item = TweetListItem(status['user']['screen_name'], status['text'].replace('\n', ' '), status['id'])
            if status['favorited'] == True:
                item.change_color(textcolor=(255, 0, 0))
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

    def append_item(self, id, text, status_id, textcolor=None, backgroundcolor=None, multi_line=False):
        """
        id, textのリストを追加．
        status_idは(デフォでは)そのアイテムをクリックされたときに
        詳細ツイート欄に表示するstatusのid．
        (TweetListItemのstatus_idになる)
        Noneにしておくとクリックしてもｽﾙｰされる．
        """
        if multi_line == False:
            id = id.replace('\n', ' ')
            text = text.replace('\n', ' ')
        item = TweetListItem(id, text, status_id)
        item.change_color(textcolor, backgroundcolor)
        self.insertTopLevelItem(0, item)

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
        return QtGui.QTreeWidget.keyPressEvent(self, e)

    def load_replied_tweet(self, item):
        #ロード用．正直デフォの使い方以外に使い道はない気もする
        child = item.child(0)
        if child.text(0) != '':
            return
        replied_status = self.get_status_from_id(child.status_id)
        child.set_display_id(replied_status['user']['screen_name'])
        child.set_display_text(replied_status['text'].replace('\n', ' '))
        if replied_status['in_reply_to_status_id'] != None:
            item_add = TweetListItem('', '', replied_status['in_reply_to_status_id'])
            child.addChild(item_add)

#ここから先はpluginクラスのをラップしただけ

    def get_status_from_id(self, status):
        return self.plugin.get_status_from_id(status)

    def change_tab_name(self, newname):
        self.plugin.change_tab_name(self, newname)

    def show_text(self, text):
        self.plugin.show_text(text)

    def show_html(self, htmltext):
        self.plugin.show_html(text)

    def set_textbox_text(self, text):
        self.plugin.set_textbox_text(text)

    def get_textbox_text(self):
        return self.plugin.get_textbox_text()

    def set_textbox_focus(self):
        self.plugin.set_textbox_focus()

    def create_favorite(self, status_id):
        self.plugin.create_favorite(status_id)

    def create_retweet(self, status_id):
        self.plugin.create_retweet(status_id)

    def set_reply_status(self, status):
        self.plugin.set_reply_status(status)

    def set_reply(self, status):
        self.plugin.set_reply(status)

    def show_status(self, status):
        self.plugin.show_status(status)

class TweetListItem(QtGui.QTreeWidgetItem):
    def __init__(self, display_id='', display_text='', status_id=None):
        super(TweetListItem, self).__init__([display_id, display_text])
        self.status_id = status_id

    def set_display_id(self, id):
        self.setText(0, id)

    def set_display_text(self, text):
        self.setText(1, text)

    def change_color(self, textcolor=None, backgroundcolor=None):
        #textcolor, backgroundcolorはRGB値をタプルで渡すこと
        if textcolor != None:
            self.setTextColor(0, QtGui.QColor(*textcolor))
            self.setTextColor(1, QtGui.QColor(*textcolor))
        if backgroundcolor != None:
            self.setBackgroundColor(0, QtGui.QColor(*backgroundcolor))
            self.setBackgroundColor(1, QtGui.QColor(*backgroundcolor))

class TweetListMenu(QtGui.QMenu):
    def __init__(self, mw):
        super(TweetListMenu, self).__init__(mw)
        self.addAction(u'ふぁぼる(&F)', self.favorite_current)
        self.addAction(u'リツイート(&R)', self.retweet_current)
        self.current_list = None
        self.mw = mw

    def execute(self, point, tweetlist):
        self.current_list = tweetlist
        self.exec_(tweetlist.mapToGlobal(point))

    def favorite_current(self):
        current_item = self.current_list.currentItem()
        self.current_list.create_favorite(current_item.status_id)
        current_item.change_color(textcolor=(255,0,0))

    def retweet_current(self):
        current_item = self.current_list.currentItem()
        self.current_list.create_retweet(current_item.status_id)

    def add_action(self, text, receiver):
        self.addAction(text, receiver)
