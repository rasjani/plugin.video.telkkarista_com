# -*- coding: utf-8 -*-
__author__ = "rasjani"
import random
from .. import utils

class Ui:
  def __init__(self, plugin, xbmcgui, xbmc, client):
    self._plugin = plugin
    self._gui = xbmcgui
    self._client = client
    self._xbmc = xbmc


  def _image_url(self, channel_id):
    return 'special://home/addons/%s/resources/media/%s.png' %(self._client.client_name, channel_id)

  def programs_channel_list(self):
    menu = []
    stream_data = sorted(self._client._streams['payload'], key=lambda k: k['streamOrder'])
    for stream in stream_data:
      channel_id = stream['name']
      channel_name = stream['visibleName']
      menu.append({
        'label': channel_name,
        'thumbnail': self._image_url(channel_id),
        'path': self._plugin.url_for('programs_showchannellist', chanid=channel_id)
      })
    return menu


  def timescope_selection(self, chanid):
    return [
        {'label': self._plugin.get_string(30500), 'path': self._plugin.url_for('programs_showprogramlist', chanid=chanid, timescope=0, page=0), 'is_playable': False},
        {'label': self._plugin.get_string(30501), 'path': self._plugin.url_for('programs_showprogramlist', chanid=chanid, timescope=1, page=0), 'is_playable': False},
        {'label': self._plugin.get_string(30502), 'path': self._plugin.url_for('programs_showprogramlist', chanid=chanid, timescope=2, page=0), 'is_playable': False},
        {'label': self._plugin.get_string(30503), 'path': self._plugin.url_for('programs_showprogramlist', chanid=chanid, timescope=3, page=0), 'is_playable': False},
    ]

  def program_selection(self, chanid, timescope, page=0):
    time_ranges = utils.generate_time_range(timescope)
    tmp = self._client.Epg.range({"from":time_ranges[0], "to":time_ranges[1], "streams":[chanid]})

    program_list = sorted(tmp[chanid], key=lambda k: k['start'])
    return self.program_list(program_list, False)

  def program_list(self, program_list, full_date):
    menu = []
    for program in program_list:
      menu_entry = self._client.pid_info(program, full_date)
      if menu_entry != None:
        menu.append(menu_entry)

    return menu

  def  main_menu(self):
    return [
      {'label': self._plugin.get_string(30001), 'path': self._plugin.url_for('live'), 'is_playable': False, 'thumbnail': self._image_url('live')},
      {'label': self._plugin.get_string(30002), 'path': self._plugin.url_for('programs'), 'is_playable': False, 'thumbnail': self._image_url('programs')},
      {'label': self._plugin.get_string(30005), 'path': self._plugin.url_for('movies', page=0), 'is_playable': False, 'thumbnail': self._image_url('movies')},
      {'label': self._plugin.get_string(30003), 'path': self._plugin.url_for('search'), 'is_playable': False, 'thumbnail': self._image_url('search')},
    ]


  def speedtest_dialog(self, hostlist):
    dialog = self._gui.DialogProgress()
    dialog.create(self._plugin.get_string(30308))

    for ix, server in enumerate(hostlist):
      progress = ix * 100 / len(hostlist)
      dialog.update(progress, server['country'], server['host'])
      if server['status'] == 'up':
        results = self._client.Cache.speed_test(server)
        hostlist[ix]['speedtest'] = results

      if dialog.iscanceled():
        break

    dialog.close()
    return hostlist

  def cachehost_dialog(self):

    host_list = self.speedtest_dialog(self._client._cache_servers['payload'])
    dialog = self._gui.Dialog()

    selection = []
    for u in host_list:
      if 'speedtest' in u:
        if u['speedtest']['mbit'] == 0:
          u['status'] = 'error'

        line = "%s [%s] (%.2f mbits/s latency: %dms)" % (u['host'], u['status'].upper(), u['speedtest']['mbit'], u['speedtest']['latency'])
        selection.append(line)

    ret = dialog.select(self._plugin.get_string(30305), selection)
    if isinstance(ret, (int, long)) and ret >= 0: ## cli xbmc returns non-int
      self._plugin.set_setting('cachehost', host_list[ret]['host'])

  def live_tv_view(self):
    menu = []
    stream_data = self._client._streams['payload']
    currently_record = self._client.Epg.current()

    stream_data = sorted(stream_data, key=lambda k: k['streamOrder'])

    for stream in stream_data:
      channel_id = stream['name']
      channel_name = stream['visibleName']
      plot = ''

      try:
        tmp = currently_record[channel_id][0]
        plot = tmp['title']['fi'] ## Config lang to use ?
      except Exception, e:
        plot = ''

      quality = self._plugin.get_setting('streamQuality', int)
      media_url = ''
      if quality == 6: # autodetect
        media_url = 'https://%s/%s/live/%s.m3u8' %(self._client.stream_service, self._client._session_id, channel_id) ## TODO: fix later
      else:
        media_url = 'https://%s/%s/live/%s_%s.m3u8' %(self._client.stream_service, self._client._session_id, channel_id, self._client.quality[quality]) ## TODO: fix later

      fanart_url = 'https://%s/%s/live/%s_large.jpg?%i' %(self._client.stream_service, self._client._session_id, channel_id, random.randint(0, 2e9)) ## TODO: fix later
      menu.append({
        'label': channel_name,
        'thumbnail': self._image_url(channel_id),
        'path': media_url,
        'info_type': 'video',
        'is_playable': True,
        'properties': {
          'Fanart_Image': fanart_url
        },
        'info': {
          'ActualIcon': self._image_url(channel_id),
          'Plot': plot,
          'PlotOutline': plot
        }
      })

    return menu


  def get_movie_list(self):
    movie_list = self._plugin.get_storage('moviecache', TTL=30)
    if len(movie_list.items()) == 0:
      tmp = self._client.Epg.search_movies()
      for item in tmp:
        pid = item['pid']
        item['start'] = utils.parse_date(item['start'])
        item['stop'] = utils.parse_date(item['stop'])
        movie_list[pid] = item

      movie_list.sync()

    return movie_list

  def movies_view(self, page):
    menu = []
    temporary_array = []

    page = int(page)
    items_per_page = self._client.items_per_page[self._plugin.get_setting('itemsperpage', int)]

    tmp = self.get_movie_list()
    self._client.populate_program_info_cache(tmp)

    for movie in tmp:
      temporary_array.append(tmp[movie])

    temporary_array = sorted(temporary_array, key=lambda k: k['start'])

    start_index = page * items_per_page
    end_index = start_index + items_per_page

    if end_index > len(temporary_array):
      end_index = len(temporary_array) - 1

    for idx in range(start_index, end_index):
      movie = temporary_array[idx]
      menu_entry = self._client.pid_info(movie, True)
      if menu_entry != None:
        menu.append(menu_entry)

    if end_index < len(temporary_array)-1:
      menu.append({'label':self._plugin.get_string(30006), 'path':self._plugin.url_for('movies', page=page+1), 'is_playable':False})

    return menu



  def add_search_keyword(self, keyword):
    old_searches = self._plugin.get_storage('searches')
    old_searches[utils.now()] = keyword
    old_searches.sync()

  def search(self, search_keyword):
    search_results = self._client.Epg.search({"search":search_keyword})
    return self.program_list(search_results, True)


  def search_dialog(self):
    keyboard = self._xbmc.Keyboard()
    keyboard.doModal()
    search_entry = keyboard.getText()
    if keyboard.isConfirmed() and search_entry != '':
      return search_entry
    else:
      return None

  def search_view(self):
    old_searches = self._plugin.get_storage('searches')
    menu = []
    menu.append({'label':self._plugin.get_string(30702), 'path':self._plugin.url_for('new_search_by_keyword'), 'is_playable':False})

    for search_entry in old_searches:
      token = old_searches[search_entry]
      menu.append({'label':token, 'path':self._plugin.url_for('search_by_keyword', token=token), 'is_playable':False})

    return menu
