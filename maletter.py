#!/usr/bin/env python
#-*- coding:utf-8 -*-

import io, sys
from PyQt4 import QtGui, QtCore
from twython import Twython, TwythonStreamer, TwythonError
from twython.streaming.types import TwythonStreamerTypesStatuses
from secretkey import *
from StringIO import StringIO
from widget.tab import TweetList, TweetListItem, TweetListMenu
from plugin_manager import PluginManager

class MainWindow(QtGui.QMainWindow):
    def __init__(self, api_cls, parent = None):
        super(MainWindow, self).__init__()
        self.api=api_cls
        me = self.api.get_account_settings()
        self.mystatus = self.api.show_user(screen_name=me['screen_name'])
        self.myid = self.mystatus['id']
        self.status_array = []
        self.buttoncount = 0
        self.init_menu()
        self.plugin_mng = PluginManager('./plugin', ['on_status'])
        self.plugin = {}
        for cls_name in self.plugin_mng.get_plugin_names():
            #インスタンスを生成
            self.plugin[cls_name] = self.plugin_mng.plugin_dict[cls_name](self)
        self.initUI()

        self.streamer = MyStreamer(self, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        self.streamer_thread = StreamerThread(streamer=self.streamer, on_finished=self.streamer.disconnect)
        self.streamer_thread.start()

        init_status = self.api.get_home_timeline(count=20)
        for status in init_status[::-1]:
            self.status_received(status)

    def closeEvent(self, event):
        return QtGui.QMainWindow.closeEvent(self, event)

    def init_menu(self):
        """
        Widgetのコンテキストメニューのインスタンスを生成しておく．
        後にWidget部分をフォルダにまとめたときはplugin_managerみたいなので
        まとめて管理するが，今は少ないのでここにまとめておく
        """
        self.menu = {}
        self.menu['TweetListMenu'] = TweetListMenu(self)

    def initUI(self):
        for cls_name in self.plugin_mng.get_plugin_names():
            # プラグインのUIを初期化
            self.plugin[cls_name].on_load()
        
        self.setWindowTitle('maletter')
        self.show()

    def status_received(self, status):
        for cls_name in self.plugin_mng.get_plugin_names():
            self.plugin[cls_name].on_status(status)

        #取得したstatusをstatus_arrayに保存
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                self.status_array.append(status)
                if status.has_key('retweeted_status') == True:
                    self.status_array.append(status['retweeted_status'])
        elif status['event'] == 'favorite':
            self.status_array.append(status['target_object'])

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

    def get_status(self, twid):
        for status in self.status_array:
            if status.has_key('id') == False: print status
            if status['id'] == twid:
                return status
        status = api.show_status(id = twid)
        self.status_array.append(status)
        return status

class MyStreamer(TwythonStreamer):
    def __init__(self, cls, *args):
        super(MyStreamer, self).__init__(*args)
        self.mw = cls

    def on_success(self, status):
        self.mw.status_received(status)

class StreamerThread(QtCore.QThread):
    def __init__(self, streamer, on_finished=None):
        super(StreamerThread, self).__init__()
        self.streamer = streamer
        self.streamer2 = TwythonStreamerTypesStatuses(streamer)
        self.on_finished = on_finished

    def run(self):
        self.streamer.user()
    
    def terminate(self):
        if self.on_finished is not None:
            self.on_finished()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    mw = MainWindow(api_cls=api)

    app.exec_()
