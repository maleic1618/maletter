#!/usr/bin/env python
#-*- coding:utf-8 -*-

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

    def on_load(self):
        """
        プラグインのロード時に呼ばれる.
        """
        pass

    def on_status(self, status):
        """
        UserStreamからstatusが流れてきたときに呼ばれる．
        """
        pass
    
    def replace(self, name):
        """
        特定のプラグインを自分自身で置き換える.
        デフォルトプラグインの挙動を変えたいときなどに
        """
        if not self.mw.plugin.has_key(name):
            print "the plugin which has specified name does not exist."
            return None

        self.mw.plugin[name] = self
        self.mw.plugin_mng.delete_plugin(self.mw, self.__class__.__name__)

    def update_status(self, text, in_reply_to_status_id=None, image=None):
        """
        ツイート．
        """
        self.mw.update_status(text, in_reply_to_status_id, image)

    def create_favorite(self, status_id):
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

    def set_image_data(self, image):
        """
        画像を追加．ツイート時に自動で画像を追加する
        """
        self.mw.set_image_data(image)
