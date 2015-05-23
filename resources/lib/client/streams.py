__author__ = 'rasjani'


class Streams:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    pass

  def get(self):
    response = json.loads(self._client.request('streams/get'))

    if response['status'] == 'ok' and response['code'] == 'streams':
    	return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
    	return []
