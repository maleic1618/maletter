#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from PyQt4 import QtGui, QtCore

from plugin_class import *
from StringIO import StringIO
from widget.box import DetailTextBox, ReplyTextBox, TweetTextBox
from widget.tab import TweetList
from widget.button import ImageButton

class DefaultLayout(Plugin):
    """
    デフォルトのレイアウトを設定
    このプラグインを上書きすることでレイアウトを自由に変更できます
    """
    def __init__(self, mainwindow):
        super(DefaultLayout, self).__init__(mainwindow)
        self.buttoncount = 0
        self.img = None
        self.initUI()
    
    def widget(self):
        """
        Layoutの上に乗るwidget(部品)の定義
        デフォルトプラグインはこれを参照するのでメンバにしておく
        """

        # 主にツイートを表示するタブを表示するためのwidget
        self.twtab = QtGui.QTabWidget(self.mw)

        # リプライの内容を表示するためのテキストボックス
        self.replytext = ReplyTextBox()
        
        # 詳細ツイート + 画像プレビュー部分
        self.detail_widget = QtGui.QWidget()
        self.detail_widget.setFixedHeight(80)
        
        self.detail_layout = QtGui.QHBoxLayout()
        self.detail_layout.setMargin(0)

        # 詳細ツイートボックスと画像プレビューを標準レイアウトに追加
        self.detail_widget.setLayout(self.detail_layout)
        
        # ツイートテキスト表示部分
        self.twtext_widget = QtGui.QWidget()
        self.twtext_widget.setFixedHeight(80)

        self.twtext_layout = QtGui.QHBoxLayout()
        self.twtext_layout.setMargin(0)
        self.twtext_widget.setLayout(self.twtext_layout)
        
        # ボタン表示部分
        self.button_widget = QtGui.QWidget()
        self.button_widget.setFixedSize(100, 80)
        
        # ボタンレイアウト
        self.button_layout = QtGui.QGridLayout()
        self.button_widget.setLayout(self.button_layout)
    
    def initUI(self):
        # MainWindowにはQGridLayoutが1つ
        self.mw.grid = QtGui.QGridLayout()
        
        self.widget()

        grid = self.mw.grid
        grid.addWidget(self.twtab,          0, 0, 1, 2)
        grid.addWidget(self.replytext,      1, 0, 1, 2)
        grid.addWidget(self.detail_widget,  2, 0, 1, 2)
        grid.addWidget(self.twtext_widget,  3, 0)
        grid.addWidget(self.button_widget,  3, 1)
        grid.setMargin(5)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(self.mw.grid)
        self.mw.setCentralWidget(central_widget)

class LayoutPlugin(Plugin):
    """
    DefaultLayoutクラス(またはそれに類するLayout管理系クラス)の
    部品となるプラグインを定義するためのクラス
    
    DefaultLayoutを置き換える場合はself.dlayoutの定義を
    書き換えてください
    """
    def __init__(self, mainwindow):
        super(LayoutPlugin, self).__init__(mainwindow)
    
    def on_load(self):
        self.dlayout = self.mw.plugin['DefaultLayout']
        self.initUI()

    def initUI(self):
        self.dlayout.twtab.currentChanged.connect(self.current_tab_changed)

    def delete_image_data(self):
        self.dlayout.img = None
        self.dlayout.preview.detach()
        self.dlayout.picture_prv.setHidden(True)

    def delete_reply_status(self):
        self.dlayout.replytext.delete_reply_status()

    def current_tab_changed(self, index):
        self.dlayout.twtab.widget(index).tab_activated()

    def get_reply_status(self):
        return self.dlayout.replytext.reply_status

    def get_image_data(self):
        return self.dlayout.img

    def add_tab(self, widget, name, idx=None):
        """
        widgetをタブに追加する．nameはタブ名．
        """
        if idx is None:
            self.dlayout.twtab.addTab(widget, name)
        else:
            self.dlayout.twtab.insertTab(idx, widget, name)

    def add_button(self, button):
        """
        Buttonをツイート入力欄の横に追加
        """
        self.dlayout.button_layout.addWidget(button, self.dlayout.buttoncount, 0)
        self.dlayout.buttoncount += 1

    def change_tab_name(self, widget, newname):
        """
        タブに追加されているwidgetの名前をnewnameに変更する．
        """
        index = self.dlayout.twtab.indexOf(widget)
        self.dlayout.twtab.setTabText(index, newname)

    def show_text(self, text):
        """
        詳細テキスト欄に表示．
        リンクを張りたい場合はhtmlで記述してshow_html()を使うこと．
        改行は/n
        """
        self.dlayout.detailtext.setText(text)

    def show_html(self, htmltext):
        """
        詳細テキスト欄に表示．
        タグが認識される．改行は\nではなく<br>なので置き換えてから呼び出すこと．
        """
        self.dlayout.detailtext.setHtml(htmltext)

    def set_textbox_text(self, text):
        """
        ツイート入力欄の文字列を設定．
        """
        self.dlayout.twtext.setText(text)

    def get_textbox_text(self):
        """
        ツイート入力欄の文字列を取得．
        Unicode形式で返される．
        """
        return unicode(self.dlayout.twtext.toPlainText())

    def set_textbox_focus(self):
        """
        ツイート入力欄をアクティブにする．
        """
        self.dlayout.twtext.setFocus()

    def update_status(self, *args, **kwargs):
        """
        ツイート．
        """
        self.mw.update_status(*args, **kwargs)
        self.delete_image_data()
        self.delete_reply_status()

    def set_reply_status(self, status):
        """
        これは使わない方向で

        リプライ先のstatusをセットする．リツイートであってはならない．
        それぞれのpluginでリプライ先のstatus情報を持っていると
        ユーザーがどれがどれだか分からなくなるので，とりあえず現状この感じで．
        """
        self.dlayout.replytext.set_reply_status(status)

    def set_reply(self, status):
        """
        statusを投げるとツイート入力欄に@Maleic1618などと自動で入力し，
        リプライ先ツイート表示欄にstatusの情報を入れる．
        リツイートを入れた場合は自動で検出して，RT元のツイートを読み込む．
        """
        if status.has_key('retweeted_status') == True:
            status = status['retweeted_status']
        self.set_reply_status(status)
        previous_text = self.get_textbox_text()
        new_text = '@{name} {text}'.format(name = status['user']['screen_name'], text = previous_text)
        self.set_textbox_text(new_text)
        self.set_textbox_focus()

    def set_image_data(self, image):
        io_img = StringIO(image)
        prv_suc = self.dlayout.preview.loadFromData(io_img.getvalue())
        if prv_suc == False:
            print 'Error:set_image_data'
            self.delete_image_data()
            return
        self.dlayout.preview.scaled(100, 80, QtCore.Qt.KeepAspectRatio)
        self.dlayout.img = image
        self.dlayout.picture_prv.setPixmap(self.dlayout.preview)
        self.dlayout.picture_prv.setHidden(False)

    def show_status(self, status):
        """
        statusを投げると通常の形式で詳細欄に表示
        """
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
        self.show_html("<br>".join(text.split('\n')))

    def add_link_status(self, status):
        """
        statusを投げるとtextにリンクを付けたhtmlを返す．
        """
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

class Home(LayoutPlugin):
    def __init__(self, mainwindow):
        super(Home, self).__init__(mainwindow)

    def initUI(self):
        self.tab = TweetList(self.mw, self)
        self.tab.change_header('User ID', 'Tweet')
        self.add_tab(self.tab, u'ホーム', idx=0)

    def on_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                self.tab.append_status(status)

class Reply(LayoutPlugin):
    def __init__(self, mainwindow):
        super(Reply, self).__init__(mainwindow)

    def initUI(self):
        self.tab = TweetList(self.mw, self)
        self.tab.change_header('Reply from', 'Tweet')
        self.add_tab(self.tab, u'リプライ', idx=1)

    def on_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                if status['in_reply_to_user_id'] == self.mystatus['id']:
                    self.tab.append_status(status)

class Favorite(LayoutPlugin):
    def __init__(self, mainwindow):
        super(Favorite, self).__init__(mainwindow)

    def initUI(self):
        self.tab = TweetList(self.mw, self)
        self.tab.change_header('Favorite', 'Your Tweet')
        self.add_tab(self.tab, u'ふぁぼられ', idx=2)

    def on_status(self, status):
        if status.has_key('event') == True:
            if status['event'] == 'favorite':
                target = status['target_object']
                if target['user']['id'] == self.mystatus['id']:
                    self.tab.append_item(status['source']['screen_name'], target['text'], target['id'])

class Image(LayoutPlugin):
    def __init__(self, mainwindow):
        super(Image, self).__init__(mainwindow)
    
    def initUI(self):
        self.button = ImageButton(self.mw, self, u'画像')
        self.add_button(self.button)

class TweetArea(LayoutPlugin):
    def __init__(self, mainwindow):
        super(TweetArea, self).__init__(mainwindow)
    
    def initUI(self):
        self.twtext = TweetTextBox(self)
        self.dlayout.twtext_layout.addWidget(self.twtext)
        
        self.dlayout.twtext = self.twtext

class DetailPreviewArea(LayoutPlugin):
    def __init__(self, mainwindow):
        super(DetailPreviewArea, self).__init__(mainwindow)

    def initUI(self):        
        self.detailtext = DetailTextBox()
        self.detailtext.setFixedHeight(80)

        self.preview = QtGui.QPixmap()    
        self.picture_prv = QtGui.QLabel()
        self.picture_prv.setFixedSize(100, 80)
        self.picture_prv.setHidden(True)
        self.picture_prv.setPixmap(self.preview)

        self.dlayout.detail_layout.addWidget(self.detailtext)
        self.dlayout.detail_layout.addWidget(self.picture_prv)
        
        self.dlayout.detailtext = self.detailtext
        self.dlayout.preview = self.preview
        self.dlayout.picture_prv = self.picture_prv
