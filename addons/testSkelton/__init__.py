# -*- coding: utf-8 -*-
"""
本パッケージによりロードすべき `AddonAppConfig`を定義する。
"""

# 本アドオンの識別名
SHORT_NAME = 'testSkelton'

# `apps.py`に定義した`AddonAppConfig`クラス名の指定
# 特別な理由がなければ、 `addons.アドオン名.apps.AddonAppConfig`
default_app_config = 'addons.{}.apps.AddonAppConfig'.format(SHORT_NAME)
