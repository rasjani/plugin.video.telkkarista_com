# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin


class User(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.apiBase = "user"

  def login(self):
    payload = None
    email = self._plugin.get_setting('email', unicode)
    password = self._plugin.get_setting('password', unicode);

    if len(email)>0 and len(password)>0:
      payload = self.apiCall('login', {'password':password,'email':email })

    if payload != None:
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



