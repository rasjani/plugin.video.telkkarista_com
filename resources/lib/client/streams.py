# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin

class Streams(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "streams"

  def get(self):
    return self.apiCall("get")
