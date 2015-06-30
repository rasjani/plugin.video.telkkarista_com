# -*- coding: utf-8 -*-
__author__ = 'rasjani'
from .apibase import APIBaseMixin

class News(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "news"

  def get(self):
    return self.apiCall("get")

  def add(self, data):
    # data format:
    # {'title': 'Title of news', 'author': 'Name of author',
    # 'content': 'Content of news'}}
    return self.apiCall("add", data )

