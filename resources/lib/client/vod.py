# -*- coding: utf-8 -*-
__author__ = 'rasjani'


class Vod:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin

  def info(self, pid):
    response = self._client.request('vod/info', { "pid": pid})
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'info':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return None
