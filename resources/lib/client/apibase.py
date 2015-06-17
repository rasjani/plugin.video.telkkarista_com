# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import urllib2
import json

class APIBaseMixin(object):
  def apiCall(self, method, data=None, path=None):
    requestSuccess = "%s/%s" % (self.apiBase, method)

    response = self._client.request("%s/%s" % (self.apiBase, method), data, path)
    response = json.loads(response)
    if response['status'] == 'ok' and response['method'] == requestSuccess:
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return None
