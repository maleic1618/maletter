#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

class Plugin(object):
    """
    maletterのplugin用class
    """

    def __init__(self, mainwindow):
        """
        インスタンス生成時にmainwindowのインスタンスが渡されるので
        こっちの__init__を呼び出して渡すこと．
        plugin内ではmainwindow内にアクセスしないことが望ましい
        ※出来るだけラップされた関数だけを使うようにしてください
        """
        self.mw = mainwindow
        self.mystatus = self.mw.mystatus

    def on_status(self, status):
        """
        UserStreamからstatusが流れてきたときに呼ばれる．
        """
        pass

    def add_tab(self, widget, name):
        """
        widgetをタブに追加する．nameはタブ名．
        """
        self.mw.add_tab(widget, name)

    def add_button(self, button):
        """
        Buttonをツイート入力欄の横に追加．nameはボタン名
        """
        self.mw.add_button(button)

    def change_tab_name(self, widget, newname):
        """
        タブに追加されているwidgetの名前をnewnameに変更する．
        """
        self.mw.change_tab_name(widget, newname)

    def show_text(self, text):
        """
        詳細テキスト欄に表示．
        リンクを張りたい場合はhtmlで記述してshow_html()を使うこと．
        改行は/n
        """
        self.mw.show_text(text)

    def show_html(self, htmltext):
        """
        詳細テキスト欄に表示．
        タグが認識される．改行は\nではなく<br>なので置き換えてから呼び出すこと．
        """
        self.mw.show_html(htmltext)

    def set_textbox_text(self, text):
        """
        ツイート入力欄の文字列を設定．
        """
        self.mw.set_textbox_text(text)

    def get_textbox_text(self):
        """
        ツイート入力欄の文字列を取得．
        Unicode形式で返される．
        """
        return self.mw.get_textbox_text()

    def set_textbox_focus(self):
        """
        ツイート入力欄をアクティブにする．
        """
        self.mw.set_textbox_focus()

    def update_status(self, text, in_reply_to_status_id=None, image=None):
        """
        ツイート．
        """
        self.mw.update_status(text, in_reply_to_status_id, image)

    def create_faborite(self, status_id):
        """
        status_idをふぁぼる．
        文字列でもintでも可．
        """
        self.mw.api.create_favorite(id = int(status_id))

    def create_retweet(self, status_id):
        """
        status_idをリツイート．
        文字列でもintでも可．
        """
        self.mw.api.retweet(id = int(status_id))

    def get_status_from_id(self, status_id):
        """
        status_idからstatusを返す．
        既に読み込んだstatusは内部で保持しているのでAPIを消費しない．
        """
        return self.mw.get_status(status_id)

    def set_reply_status(self, status):
        """
        これは使わない方向で

        リプライ先のstatusをセットする．リツイートであってはならない．
        それぞれのpluginでリプライ先のstatus情報を持っていると
        ユーザーがどれがどれだか分からなくなるので，とりあえず現状この感じで．
        """
        self.mw.set_reply_status(status)

    def set_reply(self, status):
        """
        statusを投げるとツイート入力欄に@Maleic1618などと自動で入力し，
        リプライ先ツイート表示欄にstatusの情報を入れる．
        リツイートを入れた場合は自動で検出して，RT元のツイートを読み込む．
        """
        if status.has_key('retweeted_status') == True:
            status = status['retweeted_status']
        self.mw.set_reply_status(status)
        previous_text = self.get_textbox_text()
        new_text = '@{name} {text}'.format(name = status['user']['screen_name'], text = previous_text)
        self.set_textbox_text(new_text)
        self.set_textbox_focus()

    def set_image_data(self, image):
        """
        画像を追加．ツイート時に自動で画像を追加する
        """
        self.mw.set_image_data(image)

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
        self.show_html(text)

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