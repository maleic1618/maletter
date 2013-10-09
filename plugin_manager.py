#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import inspect

class PluginManager(object):

    def __init__(self, target_dir, required_funcs):
        """
        target_dir:pluginフォルダの指定．相対パスでもよい．
        required_funcs:ロードするクラスが持っているべき関数名のリスト．
        ['on_status', 'connected', ...etc]

        target_dirフォルダ内のモジュールにある全てのクラスをチェックし，
        required_funcsを満たしているクラスだけを取り出し，
        そのインスタンスを内部に持つ．
        """
        self.required_funcs = required_funcs

        #ロードされたプラグインの辞書．
        # ['modole_name' : ['func_name' : func_object, 'func2' : func2_object, ...], ...]
        self.plugin_dict = {}

        self.plugin_dir_path = None

        self.set_plugin_dir(target_dir)
        self.load_plugins()

    def set_plugin_dir(self, path):
        """
        path:pluginのディレクトリパス
        パスを正規化してself.plugin_dir_pathにセット．
        プラグインディレクトリとして登録．
        """

        if path == None or len(path) == 0:
            return
        base = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir_path = os.path.normpath(os.path.join(base, path))

        if self.plugin_dir_path not in sys.path:
            sys.path.append(self.plugin_dir_path)


    def load_plugins(self):
        """
        plugin_dir_path内をモジュールをロードし，import_pluginに引き渡す．
        """

        self.plugin_dict = {}
        for item in os.listdir(self.plugin_dir_path):
            #os.path.isfileの挙動がよく分からないのでコメントアウト
            #target_dirの中にモジュール以外のファイルを入れないようにすること．
            #
            #if os.path.isfile(item) != True:
            #    continue

            mod_name = inspect.getmodulename(item)
            self.import_plugin(mod_name)

    def import_plugin(self, mod_name):
        """
        mod_name:モジュール名
        モジュールを受け取ってそのクラスをclass_checkerに引き渡す.
        class_checkerによりrequired_funcsを持つクラスだけが
        self.plugin_dictに追加される．
        """

        if mod_name == None or len(mod_name) == 0:
            return None

        #mod_nameをインポートする
        try:
            mod = __import__(mod_name)
        except:
            print 'error on importing "{module}"'.format(module = mod_name)
            return None

        #modの中からclassだけを取り出す
        class_list = inspect.getmembers(mod, inspect.isclass)
        if class_list == None or len(class_list) == 0:
            return None

        for class_name, class_obj in class_list:
            sourcefile = inspect.getsourcefile(class_obj)
            if inspect.getmodulename(sourcefile) != mod_name:
                continue
            self.class_checker(class_name, class_obj)

    def class_checker(self, class_name, class_obj):
        """
        classがrequired_funcsの条件を満たしているとき
        self.plugin_dictに追加
        """
        func_list = inspect.getmembers(class_obj, inspect.ismethod)
        func_name_list = [item[0] for item in func_list]
        for fname in self.required_funcs:
            if fname not in func_name_list:
                return

        self.plugin_dict[class_name] = class_obj

    def get_plugin_count(self):
        return len(self.plugin_dict)

    def get_plugin_names(self):
        if len(self.plugin_dict) == 0:
            return {}
        return self.plugin_dict.keys()