#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Tab import *

class ActTab(TweetList):
    def __init__(self, mainwindow):
        super(ActTab, self).__init__(mainwindow)
        self.change_header(id_name = 'Faved by', textname = 'Your Tweet')
        self.tabname = u'ふぁぼられ'
        self.unread_count = 0

    def on_status(self, status):
        if status.has_key('event') == True:
            if status['event'] == 'favorite':
                if status['target_object']['user']['id'] == self.mystatus['id']:
                    self.append_item(status['source']['screen_name'], status['target_object']['text'].replace('\n', ' '), status['target_object']['id'])
                    self.unread_count += 1
                    self.update_tab_name()

    def update_tab_name(self):
        if self.unread_count == 0:
            self.change_tab_name(u'ふぁぼられ')
        else:
            self.change_tab_name(u'ふぁぼられ[' + str(self.unread_count) + ']')

    def tab_activated(self):
        self.unread_count = 0
        self.update_tab_name()
