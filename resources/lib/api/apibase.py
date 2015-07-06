# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import json

class APIBaseMixin(object):
  def api_call(self, method, data=None, path=None):
    request_success = "%s/%s" % (self.api_base, method)

    response = self._client.request("%s/%s" % (self.api_base, method), data, path)
    response = json.loads(response)
    if response['status'] == 'ok' and response['method'] == request_success:
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return None
