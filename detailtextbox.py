#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

class DetailTextBox(QtGui.QTextBrowser):
    def __init__(self, mainwindow):
        super(DetailTextBox, self).__init__(mainwindow)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
