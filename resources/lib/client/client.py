__author__ = 'rasjani'

from .user import User
from .streams import Streams
from .epg import Epg
from .vod import Vod
from .cache import Cache


import urllib2
import json
import random


class Client:

  apiEndPoint = ''
  loginService = ''
  clientName = None
  clientVersion = None
  versionString = None
  apiVersion = '1'
  streamService = 'proxy1.telkkarista.com'

  _user = {}
  _streams = {}
  _epg = {}
  _vod = {}
  _cacheServers = {}
  _settings = {}

  _plugin = None

  _sessionId = None
  _xlibversion = 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)'

  def __init__(self, host, plugin, xbmcgui):
    self._plugin = plugin
    self._gui = xbmcgui
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
    self.Epg = Epg(self, plugin)
    self.Cache = Cache(self, plugin)
    self.User.login()
    self.Cache.get()

  def setSessionId(self, id):
    self._sessionId = id


  def cacheHostDialog(self):
    dialog = self._gui.Dialog()
    hostList = self.Cache.get()
    ret = dialog.select(
        self._plugin.get_string(30305),
        [u['host'] for u in hostList]
    )
    if ret >= 0:
      self._plugin.set_setting('cachehost', hostList[ret]['host'])

  def LiveTVView(self):
    menu = []
    streamData = self.Streams.get()
    currentlyRecord = self.Epg.current()

    streamData = sorted(streamData, key=lambda k: k['streamOrder'])

    for stream in streamData:
      channelId = stream['name']
      channelName = stream['visibleName']
      plot = ''

      try:
        tmp = currentlyRecord[channelId][0]
        plot  = tmp['title']['fi'] ## Config lang to use ?
      except Exception, e:
        plot = ''

      mediaUrl = 'http://%s/%s/live/%s.m3u8' % (self.streamService, self._sessionId, channelId)
      iconUrl = 'http://%s/%s/live/%s_small.jpg?%i' % (self.streamService, self._sessionId, channelId, random.randint(0,2e9))
      menu.append({
        'label': channelName,
        'thumbnail': iconUrl,
        'icon': iconUrl,
        'path': mediaUrl,
        'info_type': 'video',
        'is_playable': True,
        'info': {
          'plot': plot,
          'plotoutline': plot
        }
      })

    return menu

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
