#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from default import *

"""
デフォルトプラグインの上書きサンプル
self.replace(PLUGIN_NAME)とすることで
先に読み込まれているプラグインを自由に上書きできます.

class MyLayout(DefaultLayout):
    def __init__(self, mainwindow):
        super(MyLayout, self).__init__(mainwindow)
        # DefaultLayoutを上書き
        self.replace("DefaultLayout")
    
    def initUI(self):
        # MainWindowにはQGridLayoutが1つ
        self.mw.grid = QtGui.QGridLayout()
        
        self.widget()

        grid = self.mw.grid
        grid.addWidget(self.twtext_widget,  0, 0)
        grid.addWidget(self.button_widget,  0, 1)
        grid.addWidget(self.twtab,          1, 0, 2, 2)
        grid.addWidget(self.replytext,      2, 0, 2, 2)
        grid.addWidget(self.detail_widget,  3, 0, 2, 2)
        grid.setMargin(5)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(self.mw.grid)
        self.mw.setCentralWidget(central_widget)
"""
