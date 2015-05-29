__author__ = "rasjani"
import random

class Ui:
  def __init__(self, plugin, xbmcgui, client):
    self._plugin = plugin
    self._gui = xbmcgui
    self._client = client

  def cacheHostDialog(self):
    dialog = self._gui.Dialog()
    hostList = self._client._cacheServers['payload']
    ret = dialog.select( self._plugin.get_string(30305), [u['host'] for u in hostList if u['status']=='up' ])
    if isinstance( ret, ( int, long ) ) and ret >= 0: ## cli xbmc returns non-int
      self._plugin.set_setting('cachehost', hostList[ret]['host'])

  def LiveTVView(self):
    menu = []
    streamData = self._client._streams['payload']
    currentlyRecord = self._client.Epg.current()

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

      mediaUrl = 'http://%s/%s/live/%s.m3u8' % (self._client.streamService, self._client._sessionId, channelId) ## TODO: fix later
      iconUrl = 'http://%s/%s/live/%s_small.jpg?%i' % (self._client.streamService, self._client._sessionId, channelId, random.randint(0,2e9)) ## TODO: fix later
      menu.append({
        'label': channelName,
        'thumbnail': iconUrl,
        'icon': iconUrl,
        'path': mediaUrl,
        'info_type': 'video',
        'is_playable': True,
        'info': {
          'Plot': plot,
          'PlotOutline': plot
        }
      })

    return menu
