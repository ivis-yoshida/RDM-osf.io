# -*- coding: utf-8 -*-
import logging
import json
from celery import Celery
import requests

from django.db import models
from django.db.models import Subquery
from django.db.models.signals import post_save
from django.dispatch import receiver

from osf.models import Contributor, RdmAddonOption, AbstractNode
from osf.models.node import Node

from website.settings import CeleryConfig

from . import settings
from . import SHORT_NAME
from addons.base.models import BaseNodeSettings
from website import settings as ws_settings

logger = logging.getLogger(__name__)

class NodeSettings(BaseNodeSettings):
    """
    プロジェクトにアタッチされたアドオンに関するモデルを定義する。
    """
    dmp_id = models.TextField(blank=True, null=True)
    dmr_api_key = models.TextField(blank=True, null=True)

    # 非同期処理のための変数を定義
    app = Celery()
    app.config_from_object(CeleryConfig)

    # def get_dmr_api_key(self):
    #     return settings.DMR_API_KEY

    def set_dmr_api_key(self, dmr_api_key):
        self.dmr_api_key = dmr_api_key
        self.save()

    def get_dmr_api_key(self):
        return self.dmr_api_key

    def set_dmp_id(self, dmp_id):
        self.dmp_id = dmp_id
        self.save()

    def get_dmp_id(self):
        return self.dmp_id

    def has_dmr_api_key(self):
        if (settings.DMR_API_KEY != "") & (settings.DMR_API_KEY != None):
            return True

        return False

    @receiver(post_save, sender=Node)
    def add_niirdccore_addon(sender, instance, created, **kwargs):
        if SHORT_NAME not in ws_settings.ADDONS_AVAILABLE_DICT:
            return

        if instance.has_addon(SHORT_NAME):
            # add済みの場合は終了
            return
        # 所属機関によるアドオン追加判定は、adminコンテナの起動が可能になるまでコメントアウトする
        # inst_ids = instance.affiliated_institutions.values('id')
        # addon_option = RdmAddonOption.objects.filter(
        #     provider=SHORT_NAME,
        #     institution_id__in=Subquery(inst_ids),
        #     management_node__isnull=False,
        #     is_allowed=True
        # ).first()
        # if addon_option is None:
        #     return
        # if addon_option.organizational_node is not None and \
        #         not addon_option.organizational_node.is_contributor(instance.creator):
        #     return

        instance.add_addon(SHORT_NAME, auth=None, log=False)

    #! DMP情報モニタリング
    @receiver(post_save, sender=Node)
    def node_monitoring(sender, instance, created, **kwargs):
        # アドオン情報、ノード情報を収集

        # DMP更新タスク発行
        NodeSettings.dmp_update(node=instance)

    #! DMPの非同期更新処理
    @app.task
    def dmp_update(node):
        addon = node.get_addon(SHORT_NAME)
        node_data = Node.objects.filter(guids___id=node._id)

        # DMP更新リクエスト
        dmp_id = addon.get_dmp_id()
        # dmr_url = settings.DMR_URL + 'v1/dmp' + str(dmp_id)
        dummy_url = 'http://127.0.0.1:5000/api/v1/project/k8cgb/niirdccore/DMR_DUMMY'
        access_token = 'ZNZ3KyWH81SoqSzCvyerIIufHDi9VkQy2DeTNAK0c4xmHNxsqU90GhmQSbtyjEFXX0iZIr'
        headers = {'Authorization': 'Bearer ' + access_token}
        dmp_update = requests.put(dummy_url, headers=headers)


class AddonList(BaseNodeSettings):
    """
    送信先アドオンリストに関するモデルを定義する。
    """
    owner    = models.ForeignKey("NodeSettings", null=True, blank=True, related_name="node")
    node_id = models.CharField(max_length=100, blank=True)
    dmp_id = models.TextField(blank=True, null=True)
    addon_id = models.CharField(max_length=50, blank=True)
    callback = models.CharField(max_length=100, blank=True)

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner
        self.save()

    def get_node_id(self):
        return node_id

    def set_node_id(self, node_id):
        self.node_id = node_id
        self.save()

    def get_dmp_id(self):
        return self.dmp_id

    def set_dmp_id(self, dmp_id):
        self.dmp_id = dmp_id
        self.save()

    def get_addon_id(self):
        return self.addon_id

    def set_addon_id(self, addon_id):
        self.addon_id = addon_id
        self.save()

    def get_callback(self):
        return self.callback

    def set_callback(self, callback):
        self.callback = callback
        self.save()
