#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

class TweetTextBox(QtGui.QTextEdit):
    def __init__(self, mainwindow):
        super(TweetTextBox, self).__init__(mainwindow)
        self.mw = mainwindow

    def key_pressed(self, event):
        #キー入力があった時
        self.default_key_event(event)

#==================ここから下は書き換え不可====================

    def keyPressEvent(self, event):
        self.key_pressed(event)
        return QtGui.QTextEdit.keyPressEvent(self, event)

    def get_text(self):
        return self.toPlainText()

    def set_text(self, text):
        self.setText(text)

    def get_image_data(self):
        return self.mw.img

    def get_reply_status(self):
        return self.mw.reply_status

    def update_status(self, posttext, in_reply_to_status_id=None, image=None):
        self.mw.update_status(posttext, in_reply_to_status_id, image)

    def default_key_event(self, e):
        if e.key() == QtCore.Qt.Key_Return and e.modifiers() == QtCore.Qt.ControlModifier:
            self.tweet(self.get_text())

    def tweet(self, posttext):
        image = self.get_image_data()
        reply_status = self.get_reply_status()
        if reply_status != None:
            if not(posttext.find('@'+reply_status['user']['screen_name'])):
                self.update_status(posttext = posttext, in_reply_to_status_id = reply_status['id'], image = image)
            else:
                self.update_status(posttext = posttext, image = image)
        else:
            self.update_status(posttext = posttext, image = image)
        self.set_text('')
