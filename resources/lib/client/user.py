# -*- coding: utf-8 -*-
__author__ = 'rasjani'

import json


class User:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin

  def login(self):
    email = self._plugin.get_setting('email', unicode)
    password = self._plugin.get_setting('password', unicode);

    response = json.loads(self._client.request('user/login',  {'password':password,'email':email }))

    if response['status'] == 'ok' and response['code'] == 'login_ok':
      self._client.setSessionId(response['payload'])
    else:
      self._plugin.log.debug("Missing error handling")

  def checkSession(self):
    response = json.loads(self._client.request('user/checkSession'))
    if response['status'] == 'ok' and response['code'] == 'checkSession':
    	return True
    else:
    	return False

  def info(self):
    response = json.loads(self._client.request('user/info'))
    if response['status'] == 'ok' and response['code'] == 'info':
    	return response['payload']
    else:
    	return None

  def settings(self):
    response = json.loads(self._client.request('user/settings'))
    if response['status'] == 'ok' and response['code'] == 'settings':
    	return response['payload']
    else:
    	return None



