__author__ = 'rasjani'

from .user import User 
from .streams import Streams
from .epg import Epg
from .vod import Vod


import urllib2
import json

class Client:

  apiEndPoint = ''
  loginService = ''
  clientName = None
  clientVersion = None
  versionString = None
  apiVersion = '1'

  _user = {}
  _streams = {}
  _epg = {}
  _vod = {}
  _cacheServers = {}
  _settings = {}

  _plugin = None

  _sessionId = None
  _xlibversion = 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)'

  def __init__(self, host, plugin):
    self._plugin = plugin
    self._useProxy = plugin.get_setting('use_proxy',bool)
    self.apiEndPoint = 'http://api.%s' % host
    self.loginService = 'http://login.%s' % host
    self.clientName = plugin.addon.getAddonInfo('id')
    # getAddonInfo version doesnt seem to work  ? returns "Unavailable"
    # self.clientVersion = plugin.addon.getAddonInfo('version')
    self.clientVersion = "0.0.1"
    self.versionString = "%s/%s" % (self.clientName, self.clientVersion )
    self.User = User(self, plugin)
    self.Streams = Streams(self, plugin)
    pass

  def setSessionId(self, id):
    print "GOT SESSION!!!!!!!!!", id
    self._sessionId = id

  def request(self, apiMethod, data=None, path=None):
    uri = path
    if not path:
    	uri = "%s/%s/%s" % (self.apiEndPoint, self.apiVersion, apiMethod)

    conn = None
    if data != None:
      payload = json.dumps(data)
      req = urllib2.Request(uri, payload)
      contentLength = len(payload)
      req.add_header('Content-Length', contentLength)
      req.add_header('Content-Type', 'application/json')
    else:
      req = urllib2.Request(uri)

    req.add_header('User-Agent', self.versionString)
    # req.add_header('X-LIBVERSION', self._xlibversion)
    if self._sessionId != None:
      req.add_header('X-SESSION', self._sessionId)

    if self._useProxy:
      proxies = {
        'http': 'http://' + plugin.get_setting('proxy_host',unicode) + ":" + plugin.get_setting('proxy_port', unicode),
        'https': 'http://' + plugin.get_setting('proxy_host', unicode) + ":" + plugin.get_setting('proxy_port', unicode),
      }
      opener = urllib2.build_opener(urllib2.ProxyHandler(proxies, debuglevel=1))
      urllib2.install_opener(opener)
      conn = opener.open(req)
    else:
      opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
      urllib2.install_opener(opener)
      conn = opener.open(req)

    resp = conn.read()
    conn.close()
    return resp
