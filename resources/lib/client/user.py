# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin


class User(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "user"

  def login(self):
    email = self._plugin.get_setting('email', unicode)
    password = self._plugin.get_setting('password', unicode);

    payload = self.apiCall('login', {'password':password,'email':email }, requestSuccess='login_ok')

    if payload:
      self._client.setSessionId(payload)
      return True
    else:
      return False

  def checkSession(self):
    payload = self.apiCall("checkSession")
    return payload != None

  def info(self):
    return self.apiCall("info")

  def settings(self):
    return self.apiCall("settings")



