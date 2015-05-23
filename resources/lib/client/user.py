__author__ = 'rasjani'

import json


class User:
  def __init__(self, client, plugin):
    self._client = client
    self._plugin = plugin

    self.login()
    pass

  def login(self):
    email = self._plugin.get_setting('email', unicode)
    password = self._plugin.get_setting('password', unicode);

    response = json.loads(self._client.request('user/login',  {'password':password,'email':email }))

    if response['code'] == 'login_ok':
      self._client.setSessionId(response['payload'])
    else:
      self._plugin.log.debug("Missing error handling")
