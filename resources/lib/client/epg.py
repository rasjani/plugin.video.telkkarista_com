# -*- coding: utf-8 -*-
__author__ = 'rasjani'
import json

class Epg:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin

  def current(self):
    response = self._client.request('epg/current')
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'current':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []

  def search(self, data):
    response = self._client.request('epg/search', data)
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'search':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []

  def searchMovies(self):
    return self.search( {"search":"elokuva"} )

  def info(self, pid):
    response = self._client.request('epg/info', { "pid": pid})
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'info':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return None

  def range(self, data):
    response = self._client.request('epg/range', data)
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'range':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []

  def titles(self):
    response = self._client.request('epg/titles')
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'titles':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return []

  def titleSearch(self, title):
    response = self._client.request('epg/titleSearch', { "search": title})
    response = json.loads(response)
    if response['status'] == 'ok' and response['code'] == 'titlesearch':
      return response['payload']
    else:
      self._plugin.log.debug("Missing error handling")
      return None
