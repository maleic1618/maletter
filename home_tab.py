#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Tab import *

class HomeTab(TweetList):
    def __init__(self, mainwindow):
        super(HomeTab, self).__init__(mainwindow)
        self.change_header(id_name = 'UserID', textname = 'Tweet')
        self.tabname = u'ホーム'

    def on_status(self, status):
        if status.has_key('text') == True:
            self.append_status(status)
