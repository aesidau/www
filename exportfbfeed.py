from facepy import GraphAPI
import urlparse
import dateutil.parser
from crontab import CronTab
import imaplib
import time

# How many status updates to back in time (first time, and between runs)
MAX_ITEMS = 5000
# How many items to ask for each time
REQUEST_ITEMS = 25
# Default recipient
DEFAULT_TO = "my_gmail_acct@aes.id.au" # Replace with yours
# Suffix to turn Facebook message IDs into email IDs
ID_SUFFIX = "@exportfbfeed.facebook.com"
# Gmail account
GMAIL_USER = "my_gmail_acct@gmail.com" # Replace with yours
# and its secret
GMAIL_PASS = "S3CR3TC0D3" # Replace with yours
# Gmail folder to use (create if necessary)
GMAIL_FOLDER = "Facebook"

def lookupkey(the_list, the_key, the_default):
  try:
    return the_list[the_key]
  except KeyError:
    return the_default

def getusername(id, friendlist):
  uname = lookupkey(friendlist, id, '')
  if '' == uname:
    uname = lookupkey(graph.get(str(id)), 'username', id)
    friendlist[id] = uname # Add the entry to the dictionary for next time
  return uname

def getnormaldate(funnydate):
  dt = dateutil.parser.parse(funnydate)
  tz = long(dt.utcoffset().total_seconds()) / 60
  tzHH = str(tz / 60).zfill(2)
  if 0 <= tz:
    tzHH = '+' + tzHH
  tzMM = str(tz % 60).zfill(2)
  return dt.strftime("%a, %d %b %Y %I:%M:%S") + ' ' + tzHH + tzMM

def getpagingpart(urlstring, part):
  url = urlparse.urlsplit(urlstring)
  qs = urlparse.parse_qs(url.query)
  return qs[part][0]

def message2str(fromname, fromaddr, toname, toaddr, date, subj1, subj2, msgid, msg1, msg2, inreplyto=''):
  if '' == inreplyto:
    header = ''
  else:
    header = 'In-Reply-To: <' + inreplyto + '>\n'
  utcdate = dateutil.parser.parse(date).astimezone(dateutil.tz.tzutc()).strftime("%a %b %d %I:%M:%S %Y")
  return "From nobody {}\nFrom: {} <{}>\nTo: {} <{}>\nDate: {}\nSubject: {} - {}\nMessage-ID: <{}>\n{}Content-Type: text/html\n\n<p>{}{}</p>".format(utcdate, fromname, fromaddr, toname, toaddr, date, subj1, subj2, msgid, header, msg1, msg2)

def printdata(data, friendlist, replytoid='', replytosub='', max=MAX_ITEMS, conn=None):
  c = 0
  for d in data:
    id = lookupkey(d, 'id', '') # get the id of the post
    msgid = id + ID_SUFFIX
    try: # get the name (and id) of the friend who posted it
      f = d['from']
      n = f['name'].encode("ascii", "ignore")
      fid = f['id']
      uname = getusername(fid, friendlist) + "@facebook.com"
    except KeyError:
      n = ''
      fid = ''
      uname = ''
    try: # get the recipient (eg. if a wall post)
      dest = d['to']
      destn = dest['name']
      destid = dest['id']
      destname = getusername(destid, friendlist) + "@facebook.com"
    except KeyError:
      destn = ''
      destid = ''
      destname = DEFAULT_TO
    t = lookupkey(d, 'type', '') # get the type of this post
    try:
      st = d['status_type']
      t += " " + st
    except KeyError:
      pass
    try: # get the message they posted
      msg = d['message'].encode("ascii", "ignore")
    except KeyError:
      msg = ''
    try: # there may also be a description
      desc = d['description'].encode("ascii", "ignore")
      if '' == msg:
        msg = desc
      else:
        msg = msg + "<br />\n" + desc
    except KeyError:
      pass
    try: # get an associated image
      img = d['picture']
      msg = msg + '<br />\n<img src="' + img + '" />'
    except KeyError:
      img = ''
    try: # get link details if they exist
      ln = d['link']
      ln = '<br />\n<a href="' + ln + '">link</a>'
    except KeyError:
      ln = ''
    try: # get the date
      date = d['created_time']
      date = getnormaldate(date)
    except KeyError:
        date = ''
    if '' == msg:
      continue
    if '' == replytoid:
      email = message2str(n, uname, destn, destname, date, t, id, msgid, msg, ln)
    else:
      email = message2str(n, uname, destn, destname, date, 'Re: ' + replytosub, replytoid, msgid, msg, ln, replytoid + ID_SUFFIX)
    if conn:
      conn.append(GMAIL_FOLDER, "", time.time(), email)
    else:
      print email
      print "----------"
    try: # process comments if there are any
      comments = d['comments']
      commentdata = comments['data']
      printdata(commentdata, friendlist, replytoid=id, replytosub=t, conn=conn)
    except KeyError:
      pass
    c += 1
    if c == max:
      break
  return c

# Initialise the Graph API with a valid access token
try:
  with open("fbtoken.txt", "r") as f:
    oauth_access_token = f.read()
except IOError:
  print 'Run setupfbtoken.py first'
  exit(-1)

# See https://developers.facebook.com/docs/reference/api/user/
graph = GraphAPI(oauth_access_token)

# Setup mail connection
mailconnection = imaplib.IMAP4_SSL('imap.gmail.com')
mailconnection.login(GMAIL_USER, GMAIL_PASS)
mailconnection.create(GMAIL_FOLDER)

friendlist = {}

countdown = MAX_ITEMS
try:
  with open("fbtimestamp.txt", "r") as f:
    since = '&since=' + f.read()
except IOError:
  since = ''

stream = graph.get('me/home?limit=' + str(REQUEST_ITEMS) + since)
newsince = ''
while stream and 0 < countdown:
  streamdata = stream['data']
  numitems = printdata(streamdata, friendlist, max=countdown, conn=mailconnection)
  if 0 == numitems:
    break;
  countdown -= numitems
  try: # get the link to ask for next (going back in time another step)
    p = stream['paging']
    next = p['next']
    if '' == newsince:
      try:
        prev = p['previous']
        newsince = getpagingpart(prev, 'since')
      except KeyError:
        pass
  except KeyError:
    break
  until = '&until=' + getpagingpart(next, 'until')
  stream = graph.get('me/home?limit=' + str(REQUEST_ITEMS) + since + until)

if '' != newsince:
  with open("fbtimestamp.txt", "w") as f:
    f.write(newsince) # Record the new timestamp for next time

mailconnection.logout()

cron = CronTab() # get crontab for the current user
if [] == cron.find_comment("exportfbfeed"):
  job = cron.new(command="python ~/exportfbfeed.py", comment="exportfbfeed")
  job.minute.on(0) # run this script @hourly, on the hour
  cron.write()

exit()
