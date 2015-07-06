# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin


class Time(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.api_base = "Time"

  def get(self):
    return self.api_call("get")
