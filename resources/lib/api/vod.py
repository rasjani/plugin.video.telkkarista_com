# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin

class Vod(APIBaseMixin):

  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.api_base = "vod"

  def info(self, pid):
    return self.api_call("info", {"pid": pid})
