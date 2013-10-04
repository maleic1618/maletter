#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Tab import *

class ReplyTab(TweetList):
    def __init__(self, mainwindow):
        super(ReplyTab, self).__init__(mainwindow)
        self.change_header(id_name = 'Reply from', textname = 'Tweet')
        self.tabname = u'リプライ'
        self.unread_count = 0

    def on_status(self, status):
        if status.has_key('text') == True:
            if status['in_reply_to_user_id'] == self.mystatus['id']:
                self.append_status(status)
                self.unread_count += 1

    def update_tab_name(self):
        if self.unread_count == 0:
            self.change_tab_name(u'リプライ')
        else:
            self.change_tab_name(u'リプライ[' + str(self.unread_count) + ']')

    def tab_activated(self):
        self.unread_count = 0
        self.update_tab_name()
