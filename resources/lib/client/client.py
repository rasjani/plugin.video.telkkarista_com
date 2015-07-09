# -*- coding: utf-8 -*-

__author__ = 'rasjani'

from ..api import User
from ..api import Streams
from ..api import Epg
from ..api import Vod
from ..api import Cache
from .ui import Ui


from .. import utils

import urllib2
import json
import re
from time import sleep


class Client():

  apiEndPoint = ''
  loginService = ''
  clientName = None
  clientVersion = None
  versionString = None
  apiVersion = '1'
  streamService = ''
  debug = False
  user_logged_in = False


  quality = {
    0: 'lowest',
    1: 'low',
    2: 'med',
    3: 'hi',
    4: 'highest',
    5: '720p',
    6: '1080p',
    7: 'master'
  }

  lang = {
    0: 'fi',
    1: 'se',
  }

  itemsPerPage = {
      0: 10,
      1: 20,
      2: 30
  }

  _streams = {}
  _epg = {}
  _vod = {}
  _cacheServers = {}
  _settings = {}

  _plugin = None
  _sessionId = None

  _xlibversion = 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)'

  def __init__(self, host, plugin, xbmcgui, xbmc):
    self._plugin = plugin
    self._useProxy = plugin.get_setting('use_proxy',bool)
    # self.debug = plugin.get_setting('debug',bool)
    if self.debug:
      self._debugLevel = 1
    else:
      self._debugLevel = 0
    self.apiEndPoint = 'https://api.%s' % host
    self.loginService = 'https://login.%s' % host
    self.clientName = plugin.addon.getAddonInfo('id')
    # getAddonInfo version doesnt seem to work  ? returns "Unavailable"
    # self.clientVersion = plugin.addon.getAddonInfo('version')
    self.clientVersion = "0.0.1"
    self.versionString = "%s/%s" % (self.clientName, self.clientVersion )
    self.User = User(self, plugin)
    self.Streams = Streams(self, plugin)
    self.Epg = Epg(self, plugin)
    self.Vod = Epg(self, plugin)
    self.Cache = Cache(self, plugin)

    self.ui = Ui(plugin, xbmcgui, xbmc, self)

    self._sessionId = plugin.get_setting('sessionId', unicode)
    self.streamService = plugin.get_setting('cachehost', unicode)

    self.handleLogin()

  def getUrl(self,path):
    url = "https://%s/%s/%s" & (self.streamService, self_sessionId , path )
    return url

  def populateProgramInfoCache(self, programs):
    amount = 50
    pidsToFetch = []
    for program in programs:
      if not program in self._epg:
        pidsToFetch.append(program)

    while len(pidsToFetch)>0:
      fetch = pidsToFetch[0:amount]
      toBeStored = self.Epg.info(fetch)
      del pidsToFetch[0:amount]

      for programInfo in toBeStored:
        pid = programInfo['_id']
        self._epg[pid] = programInfo

    self._epg.sync()

  def getProgramInfo(self, pid):
    if pid in self._epg:
      return self._epg[pid]
    else:
      sleep(0.4) # Telkkarista backend server seems to throttle request
      programInfo = self.Epg.info(pid)
      if programInfo != None:
        self._epg[pid] = programInfo
        self._epg.sync() # TODO: fix later, dont call sync after every fetch!

      return programInfo


  def checkCacheServer(self):
    hostList = self._cacheServers['payload']

    if not self.streamService in [u['host'] for u in hostList if u['status']=='up' ]:
      return False
    else:
      return True


  def pidInfo(self, item, isMovie):
    if 'record' in item and item ['record'] == 'storage':
      programInfo =  self.getProgramInfo(item['pid'])
      if len(programInfo)>0:
        quality = self._plugin.get_setting('streamQuality', int)
        startTime = None
        mediaUrl = 'https://%s/%s/vod%s%s.m3u8' % (self.streamService, self._sessionId, programInfo['recordpath'], self.quality[quality])
        plot = ''
        full_title = ''
        epg_language = self.lang[self._plugin.get_setting('epglang',int)]
        try:
          if epg_language in programInfo['sub-title']:
            plot = programInfo['sub-title'][epg_language]
          else:
            plot = programInfo['sub-title']['fi'] # fall-back to fi
        except:
          pass

        plot = utils.unescape(plot)

        try:
          startTime = utils.parseDate(programInfo['start'])
        except:
          startTime = utils.now()
          pass
        try:
          endTime = utils.parseDate(programInfo['stop'])
        except:
          endTime = utils.now()

        try:
          if epg_language in programInfo['title']:
            full_title = programInfo['title'][epg_language]
          else:
            full_title = programInfo['title']['fi']
        except:
          pass

        title = utils.unescape(full_title.replace('Elokuva: ', '').replace('Kotikatsomo: ', ''))

        if isMovie:
          # FOX's leffamaailma doesnt show title correctly.
          if title == "Leffamaailma" and len(plot)>0:
            match = re.compile(ur'^(.*?)\s{0,}[-.]{1}\s{0,}(.*)$')
            result = re.search(match, plot)
            title = result.group(1)
            plot = result.group(2)


        fullLabel = "%s %s" % ( utils.formatStartTime(startTime, isMovie), title )
        fullPlot = "%s - %s [%s]\n%s\n" % (programInfo['title']['fi'],
            utils.formatStartTime(startTime, True),
            programInfo['channel'].upper(),plot)
        return {
          'label': fullLabel,
          'path': mediaUrl,
          'info_type': 'video',
          'is_playable': True,
          'info': {
            'Channel': programInfo['channel'],
            'Plot': fullPlot,
            'PlotOutline': plot,
            'StartTime': startTime.strftime("%H:%M"),
            'EndTime': endTime.strftime("%H:%M"),
            'Date': startTime.strftime("%d.%m.%Y"),
            'Duration': (endTime-startTime).seconds
          }
        }

  def populateCache(self, invalidate = False):
    self._streams = self._plugin.get_storage('streams')
    self._cacheServers = self._plugin.get_storage('cacheServers')
    if len(self._streams.items())==0 or invalidate == True:
      self._streams.update( {"payload": self.Streams.get() })
      self._streams.sync()

    if len(self._cacheServers.items())==0 or invalidate == True:
      ret = self.Cache.get()
      self._cacheServers.update({"payload": ret })
      self._cacheServers.sync()

    self._epg = self._plugin.get_storage('epgdata', TTL=20160)

  def login(self):
    ret = self.User.login()
    if ret == True:
      settings = self.User.settings()
      if settings != None:
        for item in settings:
          if 'setting' in item and 'value' in item:
            self._settings[item['setting']] = item['value']

    return ret



  def handleLogin(self):
    invalidateCache = False
    login_success = False
    if self._sessionId != None:
      if self.User.checkSession() == False:
        invalidateCache = True
        login_success = self.login()
    else:
      login_success = self.login()
      invalidateCache = True

    self.user_logged_in = login_success

    if login_success:
      self.populateCache(invalidateCache)
      if not self.checkCacheServer():
        self.ui.cacheHostDialog()


  def setSessionId(self, id):
    self._plugin.set_setting("sessionId", id)
    self._sessionId = id

  def request(self, apiMethod, data=None, path=None, timeout = 60):
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
      opener = urllib2.build_opener(urllib2.ProxyHandler(proxies, debuglevel=self._debugLevel))
      urllib2.install_opener(opener)
      conn = opener.open(req, timeout = timeout)
    else:
      opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=self._debugLevel))
      urllib2.install_opener(opener)
      conn = opener.open(req, timeout = timeout)

    resp = conn.read()
    conn.close()
    return resp
