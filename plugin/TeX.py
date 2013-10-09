#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)

from button_widget import *
from plugin import *
from StringIO import StringIO
from urllib import urlopen

class TeXButton(Button):
    def __init__(self, mainwindow, plugin, name):
        super(TeXButton, self).__init__(mainwindow, plugin, name)

    def button_clicked(self):
        tex = raw_input('数式を入力')
        tex = tex.replace('+', '%2B')
        base_url = 'http://chart.apis.google.com/chart'
        url_ext = 'cht=tx&chl=' + tex
        opener = urlopen(base_url, url_ext.encode('utf-8'))
        img = opener.read()
        self.plugin.set_image_data(img)

class TeX(Plugin):
    def __init__(self, mainwindow):
        super(TeX, self).__init__(mainwindow)
        self.button = TeXButton(mainwindow, self, u'TeX')
        self.add_button(self.button)