# -*- coding: utf-8 -*-
__author__ = 'rasjani'
import json

class Cache:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin

  def get(self):
    response = self._client.request('cache/get')
    response = json.loads(response)

    if response['status'] == 'ok' and response['code'] == 'get':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []
