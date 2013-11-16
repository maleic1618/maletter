#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui,QtCore
from twython import TwythonError

class Button(QtGui.QPushButton):
    """
    Button
    """

    def __init__(self, mainwindow, plugin, name):
        self.plugin = plugin
        self.mw = mainwindow

        super(Button, self).__init__(name, mainwindow)
        self.clicked.connect(self.button_clicked)
        self.mystatus = self.mw.mystatus
        self.setFixedWidth(80)

    def button_clicked(self):
        """
        ボタンが押されたときに呼び出されます．
        """
        pass

#ここから先はラップしただけ

    def change_button_name(self, newname):
        self.setText(newname)

    def get_status_from_id(self, status):
        return self.plugin.get_status_from_id(status)

    def show_text(self, text):
        self.plugin.show_text(text)

    def show_html(self, htmltext):
        self.plugin.show_html(htmltext)

    def set_textbox_text(self, text):
        self.plugin.set_textbox_text(text)

    def get_textbox_text(self):
        return self.plugin.get_textbox_text()

    def set_textbox_focus(self):
        self.plugin.set_textbox_focus()

    def create_favorite(self, status_id):
        self.plugin.create_favorite(status_id)

    def create_retweet(self, status_id):
        self.plugin.create_retweet(status_id)

    def set_reply_status(self, status):
        self.plugin.set_reply_status(status)

    def set_reply(self, status):
        self.plugin.set_reply(status)

    def show_status(self, status):
        self.plugin.show_status(status)

class ImageButton(Button):
    def __init__(self, mainwindow, plugin, name):
        super(ImageButton, self).__init__(mainwindow, plugin, name)

    def button_clicked(self):
        img_path = QtGui.QFileDialog.getOpenFileName(self, 'Select Image', filter =  "Image Files (*.png *.jpg *.bmp)")
        with open(img_path, 'rb') as f:
            img = f.read()
        self.plugin.set_image_data(img)

