# -*- coding: utf-8 -*-
__author__ = 'rasjani'

from .apibase import APIBaseMixin


class User(APIBaseMixin):
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin
    self.api_base = "user"

  def login(self):
    email = self._plugin.get_setting('email', unicode)
    password = self._plugin.get_setting('password', unicode);

    payload = self.api_call('login', {'password':password, 'email':email})

    if payload:
      self._client.set_session_id(payload)
      return True
    else:
      return False

  def check_session(self):
    payload = self.api_call("checkSession")
    return payload != None

  def info(self):
    return self.api_call("info")

  def settings(self):
    return self.api_call("settings")



