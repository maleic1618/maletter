#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore

class DetailTextBox(QtGui.QTextBrowser):
    def __init__(self):
        super(DetailTextBox, self).__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)

class ReplyTextBox(QtGui.QLineEdit):
    def __init__(self):
        super(ReplyTextBox, self).__init__()
        self.setReadOnly(True)
        self.reply_status = None
        self.setHidden(True)

    def set_reply_status(self, status):
        if status != None:
            try:
                self.setText(u'Reply to @{id}:{tweettext}'.format(id = status['user']['screen_name'],
                    tweettext = status['text'].replace('\n', ' ')))
                self.reply_status = status
                self.setHidden(False)
            except:
                self.setText('Error!')
                self.reply_status = None
        else:
            self.delete_reply()

    def delete_reply_status(self):
        self.setText('')
        self.reply_status = None
        self.setHidden(True)

class TweetTextBox(QtGui.QTextEdit):
    def __init__(self, plugin):
        super(TweetTextBox, self).__init__()
        self.plugin = plugin

    def key_pressed(self, event):
        self.default_key_event(event)

    def keyPressEvent(self, event):
        self.key_pressed(event)
        return QtGui.QTextEdit.keyPressEvent(self, event)

    def default_key_event(self, e):
        if e.key() == QtCore.Qt.Key_Return and e.modifiers() == QtCore.Qt.ControlModifier:
            self.tweet(unicode(self.toPlainText()))

        if e.key() == QtCore.Qt.Key_Escape:
            self.setText('')

    def tweet(self, posttext):
        image = self.plugin.get_image_data()
        reply_status = self.plugin.get_reply_status()
        if reply_status != None:
            self.plugin.update_status(posttext = posttext, in_reply_to_status_id = reply_status['id'], image = image)
        else:
            self.plugin.update_status(posttext = posttext, image = image)
        self.setText('')
        self.plugin.delete_reply_status()
        self.plugin.delete_image_data()
