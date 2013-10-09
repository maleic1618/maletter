#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from tab_widget import *
from button_widget import *
from plugin import *
from StringIO import StringIO

class Home(Plugin):
    def __init__(self, mainwindow):
        super(Home, self).__init__(mainwindow)
        self.tab = TweetList(mainwindow, self)
        self.tab.change_header('User ID', 'Tweet')
        self.add_tab(self.tab, u'ホーム')

    def on_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                self.tab.append_status(status)

class Reply(Plugin):
    def __init__(self, mainwindow):
        super(Reply, self).__init__(mainwindow)
        self.tab = TweetList(mainwindow, self)
        self.tab.change_header('Reply from', 'Tweet')
        self.add_tab(self.tab, u'リプライ')

    def on_status(self, status):
        if status.has_key('event') == False:
            if status.has_key('text') == True:
                if status['in_reply_to_user_id'] == self.mystatus['id']:
                    self.tab.append_status(status)

class Favorite(Plugin):
    def __init__(self, mainwindow):
        super(Favorite, self).__init__(mainwindow)
        self.tab = TweetList(mainwindow, self)
        self.tab.change_header('Favorite', 'Your Tweet')
        self.add_tab(self.tab, u'ふぁぼられ')

    def on_status(self, status):
        if status.has_key('event') == True:
            if status['event'] == 'favorite':
                target = status['target_object']
                if target['user']['id'] == self.mystatus['id']:
                    self.tab.append_item(status['source']['screen_name'], target['text'], target['id'])

class Image(Plugin):
    def __init__(self, mainwindow):
        super(Image, self).__init__(mainwindow)
        self.button = ImageButton(mainwindow, self, u'画像')
        self.add_button(self.button)

class ImageButton(Button):
    def __init__(self, mainwindow, plugin, name):
        super(ImageButton, self).__init__(mainwindow, plugin, name)

    def button_clicked(self):
        img_path = QtGui.QFileDialog.getOpenFileName(self, 'Select Image', filter =  "Image Files (*.png *.jpg *.bmp)")
        with open(img_path, 'rb') as f:
            img = f.read()
        self.plugin.set_image_data(img)
