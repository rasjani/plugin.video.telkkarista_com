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

  api_end_point = ''
  login_service = ''
  client_name = None
  client_version = None
  version_string = None
  api_version = '1'
  stream_service = ''
  debug = False


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

  items_per_page = {
      0: 10,
      1: 20,
      2: 30
  }

  _streams = {}
  _epg = {}
  _vod = {}
  _cache_servers = {}
  _settings = {}

  _plugin = None
  _session_id = None

  _xlibversion = 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)'

  def __init__(self, host, plugin, xbmcgui, xbmc):
    self._plugin = plugin
    self._use_proxy = plugin.get_setting('use_proxy', bool)
    # self.debug = plugin.get_setting('debug',bool)
    if self.debug:
      self._debugLevel = 1
    else:
      self._debugLevel = 0
    self.api_end_point = 'https://api.%s' % host
    self.login_service = 'https://login.%s' % host
    self.client_name = plugin.addon.getAddonInfo('id')
    # getAddonInfo version doesnt seem to work  ? returns "Unavailable"
    # self.client_version = plugin.addon.getAddonInfo('version')
    self.client_version = "0.0.1"
    self.version_string = "%s/%s" %(self.client_name, self.client_version)
    self.User = User(self, plugin)
    self.Streams = Streams(self, plugin)
    self.Epg = Epg(self, plugin)
    self.Vod = Vod(self, plugin)
    self.Cache = Cache(self, plugin)

    self.ui = Ui(plugin, xbmcgui, xbmc, self)

    self._session_id = plugin.get_setting('sessionId', unicode)
    self.stream_service = plugin.get_setting('cachehost', unicode)

    self.handle_login()

  def get_url(self, path):
    url = "https://%s/%s/%s" %(self.stream_service, self._session_id, path)
    return url

  def populate_program_info_cache(self, programs):
    amount = 50
    pids_to_fetch = []
    for program in programs:
      if not program in self._epg:
        pids_to_fetch.append(program)

    while len(pids_to_fetch) > 0:
      fetch = pids_to_fetch[0:amount]
      to_be_stored = self.Epg.info(fetch)
      del pids_to_fetch[0:amount]

      for program_info in to_be_stored:
        pid = program_info['_id']
        self._epg[pid] = program_info

    self._epg.sync()

  def get_program_info(self, pid):
    if pid in self._epg:
      return self._epg[pid]
    else:
      sleep(0.4) # Telkkarista backend server seems to throttle request
      program_info = self.Epg.info(pid)
      if program_info != None:
        self._epg[pid] = program_info
        self._epg.sync() # TODO: fix later, dont call sync after every fetch!

      return program_info


  def check_cache_server(self):
    host_list = self._cache_servers['payload']

    if not self.stream_service in [u['host'] for u in host_list if u['status'] == 'up']:
      return False
    else:
      return True


  def pid_info(self, item, is_movie):
    if 'record' in item and item['record'] == 'storage':
      program_info = self.get_program_info(item['pid'])
      if len(program_info) > 0:
        quality = self._plugin.get_setting('streamQuality', int)
        start_time = None
        media_url = 'https://%s/%s/vod%s%s.m3u8' % (self.stream_service, self._session_id, program_info['recordpath'], self.quality[quality])
        plot = ''
        full_title = ''
        epg_language = self.lang[self._plugin.get_setting('epglang', int)]
        try:
          if epg_language in program_info['sub-title']:
            plot = program_info['sub-title'][epg_language]
          else:
            plot = program_info['sub-title']['fi'] # fall-back to fi
        except:
          pass

        plot = utils.unescape(plot)

        try:
          start_time = utils.parse_date(program_info['start'])
        except:
          start_time = utils.now()

        try:
          end_time = utils.parse_date(program_info['stop'])
        except:
          end_time = utils.now()

        try:
          if epg_language in program_info['title']:
            full_title = program_info['title'][epg_language]
          else:
            full_title = program_info['title']['fi']
        except:
          pass

        title = utils.unescape(full_title.replace('Elokuva: ', '').replace('Kotikatsomo: ', ''))

        if is_movie:
          # FOX's leffamaailma doesnt show title correctly.
          if title == "Leffamaailma" and len(plot) > 0:
            match = re.compile(ur'^(.*?)\s{0,}[-.]{1}\s{0,}(.*)$')
            result = re.search(match, plot)
            title = result.group(1)
            plot = result.group(2)


        full_label = "%s %s" %(utils.format_start_time(start_time, is_movie), title)
        full_plot = "%s - %s [%s]\n%s\n" % (program_info['title']['fi'],
            utils.format_start_time(start_time, True),
            program_info['channel'].upper(), plot)
        return {
          'label': full_label,
          'path': media_url,
          'info_type': 'video',
          'is_playable': True,
          'info': {
            'Channel': program_info['channel'],
            'Plot': full_plot,
            'PlotOutline': plot,
            'StartTime': start_time.strftime("%H:%M"),
            'EndTime': end_time.strftime("%H:%M"),
            'Date': start_time.strftime("%d.%m.%Y"),
            'Duration': (end_time-start_time).seconds
          }
        }

  def populate_cache(self, invalidate=False):
    self._streams = self._plugin.get_storage('streams')
    self._cache_servers = self._plugin.get_storage('cacheServers')
    if len(self._streams.items()) == 0 or invalidate == True:
      self._streams.update({"payload": self.Streams.get()})
      self._streams.sync()

    if len(self._cache_servers.items()) == 0 or invalidate == True:
      ret = self.Cache.get()
      self._cache_servers.update({"payload":ret})
      self._cache_servers.sync()

    self._epg = self._plugin.get_storage('epgdata', TTL=20160)

  def login(self):
    ret = self.User.login()
    if ret == True:
      settings = self.User.settings()
      if settings != None:
        for item in settings:
          if 'setting' in item and 'value' in item:
            self._settings[item['setting']] = item['value']


  def handle_login(self):
    invalidate_cache = False
    if self._session_id != None:
      if self.User.check_session() == False:
        invalidate_cache = True
        self.login()
    else:
      self.login()
      invalidate_cache = True

    self.populate_cache(invalidate_cache)

    if not self.check_cache_server():
      self.ui.cachehost_dialog()

  def set_session_id(self, sess_id):
    self._plugin.set_setting("sessionId", sess_id)
    self._session_id = sess_id

  def request(self, api_method, data=None, path=None, timeout=60):
    uri = path
    if not path:
      uri = "%s/%s/%s" % (self.api_end_point, self.api_version, api_method)

    conn = None
    if data != None:
      payload = json.dumps(data)
      req = urllib2.Request(uri, payload)
      content_length = len(payload)
      req.add_header('Content-Length', content_length)
      req.add_header('Content-Type', 'application/json')
    else:
      req = urllib2.Request(uri)

    req.add_header('User-Agent', self.version_string)
    # req.add_header('X-LIBVERSION', self._xlibversion)
    if self._session_id != None:
      req.add_header('X-SESSION', self._session_id)

    if self._use_proxy:
      proxies = {
        'http': 'http://' + self._plugin.get_setting('proxy_host', unicode) + ":" + self._plugin.get_setting('proxy_port', unicode),
        'https': 'http://' + self._plugin.get_setting('proxy_host', unicode) + ":" + self._plugin.get_setting('proxy_port', unicode),
      }
      opener = urllib2.build_opener(urllib2.ProxyHandler(proxies, debuglevel=self._debugLevel))
      urllib2.install_opener(opener)
      conn = opener.open(req, timeout=timeout)
    else:
      opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=self._debugLevel))
      urllib2.install_opener(opener)
      conn = opener.open(req, timeout=timeout)

    resp = conn.read()
    conn.close()
    return resp
