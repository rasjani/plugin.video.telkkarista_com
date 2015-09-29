# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import urllib2
import json
from .. import utils

from time import sleep

class APIBaseMixin(object):
  _error = False
  last_error = ''
  waitPeriod = 0.4
  lastCall = utils.unixtimestampms() / 1000

  def apiCall(self, method, data=None, path=None, wait=False ):
    requestSuccess = "%s/%s" % (self.apiBase, method)

    if wait == True:
      self.throttleWait()

    response = self._client.request("%s/%s" % (self.apiBase, method), data, path)
    response = json.loads(response)
    if response['status'] == 'ok' and response['method'] in [requestSuccess, method]:
      self._error = False
      return response['payload']
    else:
      self._error = True
      if 'message' in response:
        self.last_error = response['message']
      #else:
      #  print "RESPONSE: ", response
      return None

  def lastCallFailed(self):
    return this.error

  def throttleWait(self):
    diff = utils.unixtimestampms() / 1000 - self.lastCall
    if diff < self.waitPeriod:
      self.lastCall = self.lastCall + diff
      diff = self.waitPeriod - (diff / 1000.0)
      sleep(diff)

