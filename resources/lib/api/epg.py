# -*- coding: utf-8 -*-
__author__ = 'rasjani'
from .apibase import APIBaseMixin

class Epg(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.api_base = "epg"

  def current(self):
    return self.api_call("current")

  def search(self, data):
    return self.api_call("search", data)

  def search_movies(self):
    return self.search({"search":"elokuva"})

  def info(self, pid):
    return self.api_call("info", {"pid": pid})

  def range(self, data):
    return self.api_call("range", data)

  def titles(self):
    return self.api_call("titles")

  def title_search(self, title):
    return self.api_call("titleSearch", {"search": title})
