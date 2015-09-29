# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin
from .. import utils


class Time(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "Time"

  def get(self):
    return self.apiCall("get")
