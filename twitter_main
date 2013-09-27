#! /usr/bin/env python
# -*- coding: shift_jis -*-

import Tkinter as Tk
import twitter
import random

#Twitterのごにょごにょ
consumerKey   =''
consumerSecret  =''
accessToken     =''
accessSecret  =''

api = twitter.Api(consumerKey,consumerSecret,accessToken,accessSecret)

class Frame(Tk.Frame):
    
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master, height=500, width=500)
        self.master.title(u'まーれまれ')

        #listbox
        self.twscr = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        self.twscr.grid(row=0, column=1, rowspan=2, columnspan=2, padx=0, pady=0, sticky=Tk.N + Tk.S)        
        self.twlist = Tk.Listbox(self, yscrollcommand=self.twscr.set, width=100)
        self.twlist.grid(row=0, column=0, padx=0, pady=0, sticky=Tk.W + Tk.E + Tk.N + Tk.S)
        self.twscr.config(command=self.twlist.yview)

        self.s1 = Tk.StringVar()
        e1 = Tk.Entry(self, textvariable = self.s1, font=('Helvetica', '10'))
        self.bind_class("Entry", '<Return>', self.twpost)
        self.bind_class("Entry", '<F5>', self.twupdate)
        self.bind_class("twlist", '<F5>', self.twupdate)

        e1.grid(row=1, column=0, padx=0, pady=0, sticky=Tk.W + Tk.E)

        timeline = api.GetHomeTimeline()
        for tw in timeline:
            self.twlist.insert(0, tw.user.screen_name + ':' + tw.text)
        

    def twpost(self, event):
        status = api.PostUpdate(self.s1.get())
        self.s1.set('')

    def twupdate(self, event):
        timeline = api.GetHomeTimeline()
        for tw in timeline:
            self.twlist.insert(0, tw.user.screen_name + ':' + tw.text)
        

        
if __name__ == '__main__':
    f = Frame()
    f.pack()
    f.mainloop()
