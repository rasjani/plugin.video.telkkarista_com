__author__ = 'rasjani'
import json

class Epg:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    pass

  def current(self):
    response = self._client.request('epg/current')
    print response
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'current':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []

