# -*- coding: utf-8 -*-

__author__ = 'rasjani'

import datetime
import dateutil.tz
import dateutil.parser
import time
import htmlentitydefs
import re

def unescape(text):
  def fixup(res):
    text = res.group(0)
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
  return re.sub(r"&#?\w+;", fixup, text)

def parse_date(date):
  date = dateutil.parser.parse(date)
  date = date.astimezone(dateutil.tz.gettz('Europe/Helsinki'))
  return date

def format_start_time(date, is_movie):
  if is_movie:
    return "%02d.%02d %02d:%02d" % (date.day, date.month, date.hour, date.minute)
  else:
    return "%02d:%02d" % (date.hour, date.minute)

def start_of_the_day(current):
  date = current
  if date.hour < 4:
    date = date - datetime.timedelta(days=1)
  date = date.replace(hour=3, minute=0, second=0)
  return date

def end_of_the_day(current):
  date = current
  date = date + datetime.timedelta(days=1)
  date = date.replace(hour=2, minute=59, second=0)
  return date

def now():
  return datetime.datetime.now(dateutil.tz.tzlocal()).astimezone(dateutil.tz.gettz('Europe/Helsinki'))

def generate_time_range(time_scope):
  current_time = now()
  time_scope = int(time_scope)
  if time_scope == 0:
    to_time = current_time
    from_time = start_of_the_day(current_time)
  elif time_scope == 1:
    from_time = start_of_the_day(current_time - datetime.timedelta(days=1))
    to_time = end_of_the_day(from_time)
  elif time_scope == 2:
    to_time = current_time
    from_time = start_of_the_day(start_of_the_day(to_time - datetime.timedelta(days=7)))
  elif time_scope == 4:
    to_time = current_time
    from_time = start_of_the_day(current_time - datetime.timedelta(days=14))
  else:
    to_time = current_time
    from_time = current_time - datetime.timedelta(days=1)

  return [from_time.isoformat(), to_time.isoformat()]


def unixtimestamp_in_ms(datet=None):
  if datet == None:
    datet = now()

  return int(time.mktime(datet.timetuple())*1e3+datet.microsecond/1e3)

def unixtimestamp(datet=None):
  if datet != None:
    return int(time.mktime(datet.timetuple()))
  else:
    return int(time.mktime(now()))

