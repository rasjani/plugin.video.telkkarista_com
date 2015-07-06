# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin
from .. import utils

import urllib2
import socket

class Cache(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.api_base = "cache"

  def get(self):
    return self.api_call("get")


  def speed_test(self, server):

    timeout = 15 # seconds
    incoming_bytes = 719431
    mbit = 0
    length = 0
    latency = 0
    try:
      speed_test_start = utils.unixtimestamp_in_ms(utils.now())
      speed_test_url = 'https://%s/speedtest.jpg?%s' %(server['host'], speed_test_start)
      self._client.request("", path=speed_test_url, timeout=timeout)
      speed_test_end = utils.unixtimestamp_in_ms(utils.now())
      duration = speed_test_end - speed_test_start

      latency_test_start = utils.unixtimestamp_in_ms(utils.now())
      latency_test_url = 'https://%s/check.jpg?%s' %(server['host'], latency_test_start)
      self._client.request("", path=latency_test_url, timeout=timeout)
      latency_test_end = utils.unixtimestamp_in_ms(utils.now())

      mbit = (((incoming_bytes/1024.0)/1024.0)*8.0)/(duration/1000.0)
      length = duration/1000.0
      latency = latency_test_end - speed_test_start

    except (urllib2.URLError, socket.timeout) as excpt:
      pass

    return {
      'mbit': mbit,
      'length': length,
      'latency': latency
    }
