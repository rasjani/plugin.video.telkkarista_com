# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import datetime
import dateutil.tz
import dateutil.parser
import htmlentitydefs
import re

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
  date = date.astimezone(dateutil.tz.gettz('Europe/Helsinki'))
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
  return datetime.datetime.now(dateutil.tz.tzlocal()).astimezone(dateutil.tz.gettz('Europe/Helsinki'))

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

