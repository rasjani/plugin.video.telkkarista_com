__author__ = 'rasjani'

import .request

from .user import User 
from .streams import Streams
from .epg import Epg
from .vod import Vod

class Client:

  apiEndPoint = ''
  loginService = ''
  versionString = 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)'
  apiVersion = '1'

  _user = {}
  _streams = {}
  _epg = {}
  _vod = {}
  _cacheServers = {}
  _settings = {}

  def __init__(self, host):
    self.apiEndPoint = 'http://api.%s' % host
    self.loginService = 'http://login.%s' % host
    pass


