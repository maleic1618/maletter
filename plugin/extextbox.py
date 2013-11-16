#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

import urllib
from default import *

import webbrowser
from PyQt4 import QtGui, QtCore, QtWebKit

class ExtDetailTextBox(DetailTextBox):
    def __init__(self, plugin):
        super(ExtDetailTextBox, self).__init__()
        self.plugin = plugin
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self.on_clicked)

    def on_clicked(self, url):
        def close():
            dialog.closeEvent(QtGui.QCloseEvent())

        def pushed_ok(url):
            def run():
                webbrowser.open(url.toString())
                close()
            return run
        
        dialog = QtGui.QDialog()
        dialog.open()
        
        web = QtWebKit.QWebView()
        web.load(url)
        
        ok = QtGui.QPushButton(u"開く")
        ok.clicked.connect(pushed_ok(url))

        exit = QtGui.QPushButton(u"閉じる")
        exit.clicked.connect(close)

        grid = QtGui.QGridLayout()
        grid.addWidget(web, 0, 0, 2, 2)
        grid.addWidget(ok, 0, 2, 1, 3)
        grid.addWidget(exit, 1, 2, 2, 3)
        grid.setMargin(5)
        
        dialog.setLayout(grid)
        dialog.exec_()

class ExtDetailPreviewArea(DetailPreviewArea):
    def __init__(self, mainwindow):
        super(ExtDetailPreviewArea, self).__init__(mainwindow)

    def initUI(self):
        self.replace("DetailPreviewArea")
        self.detailtext = ExtDetailTextBox(self)
        self.detailtext.setFixedHeight(80)
        
        self.dlayout.detail_layout.takeAt(0)
        self.dlayout.detail_layout.insertWidget(0, self.detailtext)

        self.dlayout.detailtext = self.detailtext

