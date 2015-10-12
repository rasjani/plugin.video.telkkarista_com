# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import datetime
import dateutil.tz
import dateutil.parser
import time
import htmlentitydefs
import re
from pytz import timezone


FinlandTZ = timezone('Europe/Helsinki')

_error_msg_lookup = {
  'invalid_password': 30800,
  'unknown_error': 30801,
  'user_not_found': 30802
}

def unescape(text):
  def fixup(m):
    text = m.group(0)
    if text[:2] == "&#":
      # character reference
      try:
        if text[:3] == "&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    return text # leave as is
  return re.sub("&#?\w+;", fixup, text)

def parseDate(date):
  date =  dateutil.parser.parse(date)
  if FinlandTZ != None:
    date = date.astimezone(FinlandTZ)
  return date

def formatStartTime(date, isMovie):
  if isMovie:
    return "%02d.%02d %02d:%02d" % (date.day, date.month, date.hour, date.minute)
  else:
    return "%02d:%02d" % (date.hour, date.minute)

def startOfTheDay(current):
  date = current
  if date.hour < 4:
    date = date - datetime.timedelta(days=1)
  date = date.replace(hour=3, minute=0, second=0)
  return date

def endOfTheDay(current):
  date = current
  date = date + datetime.timedelta(days=1)
  date = date.replace(hour=2, minute=59, second=0)
  return date

def now():
  date = datetime.datetime.now(dateutil.tz.tzlocal())
  if FinlandTZ != None:
    date = date.astimezone(FinlandTZ)

  return date

def generateTimeRange(timeScope):
  currentTime = now()
  timeScope = int(timeScope)
  if timeScope == 0:
    toTime = currentTime
    fromTime = startOfTheDay(currentTime)
  elif timeScope == 1:
    fromTime = startOfTheDay(currentTime - datetime.timedelta(days=1))
    toTime = endOfTheDay(fromTime)
  elif timeScope == 2:
    toTime = currentTime
    fromTime = startOfTheDay(startOfTheDay(toTime - datetime.timedelta(days=7)))
  elif timeScope == 4:
    toTime = currentTime
    fromTime = startOfTheDay(currentTime - datetime.timedelta(days=14))
  else:
    toTime = currentTime
    fromTime = currentTime - datetime.timedelta(days=1)

  return [fromTime.isoformat(), toTime.isoformat()]


def unixtimestampms(dt = None):
  if dt == None:
    dt = now()

  return int( time.mktime(dt.timetuple())*1e3 + dt.microsecond/1e3)

def unixtimestamp(dt = None):
  if dt != None:
    return int(time.mktime(dt.timetuple()))
  else:
    return int(time.mktime(now()))

def error_message_lookup(error_msg):
  if error_msg in _error_msg_lookup:
    return _error_msg_lookup[error_msg]
  else:
    return _error_msg_lookup['unknown_error']
