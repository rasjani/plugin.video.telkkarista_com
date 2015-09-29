# -*- coding: utf-8 -*-
__author__ = 'rasjani'
from .apibase import APIBaseMixin

class Epg(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "epg"

  def current(self):
    return self.apiCall("current")

  def search(self, data):
    return self.apiCall("search", data )

  def searchMovies(self):
    return self.search( {"search":"elokuva"} )

  def info(self, pid):
    return self.apiCall("info", { "pid": pid}, wait=True)

  def range(self, data):
    return self.apiCall("range", data )

  def titles(self):
    return self.apiCall("titles")

  def titleSearch(self, title):
    return self.apiCall("titleSearch", { "search": title})
