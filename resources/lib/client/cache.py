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
    self.apiBase = "cache"

  def get(self):
    return self.apiCall("get")


  def speedTest(self, server):

    timeout = 15 # seconds
    bytes = 719431
    mbit = 0
    length = 0
    latency = 0
    try:
      speedTestStart = utils.unixtimestampms(utils.now())
      speedTestUrl = 'https://%s/speedtest.jpg?%s' % ( server['host'], speedTestStart)
      self._client.request("", path = speedTestUrl, timeout = timeout )
      speedTestEnd = utils.unixtimestampms(utils.now())
      duration = speedTestEnd - speedTestStart

      latencyTestStart = utils.unixtimestampms(utils.now())
      latencyTestUrl = 'https://%s/check.jpg?%s' % ( server['host'], latencyTestStart)
      self._client.request("", path = latencyTestUrl, timeout = timeout)
      latencyTestEnd = utils.unixtimestampms(utils.now())

      mbit = (((bytes/1024.0)/1024.0)*8.0)/(duration/1000.0)
      length = duration/1000.0
      latency = latencyTestEnd - speedTestStart

    except (urllib2.URLError, socket.timeout) as e:
      pass

    return {
      'mbit': mbit,
      'length': length,
      'latency': latency
    }
