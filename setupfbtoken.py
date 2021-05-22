# Write a long-lived Facebook token to a file and setup cron job to maintain it
import facepy
from crontab import CronTab
import datetime

APP_ID = '1234567890' # Replace with yours
APP_SECRET = 'abcdef123456' # Replace with yours

try:
  with open("fbtoken.txt", "r") as f:
    old_token = f.read()
except IOError:
  old_token = ''
if '' == old_token:
  # Need to get old_token from https://developers.facebook.com/tools/explorer
  old_token = 'FooBarBaz' # Replace with yours

new_token, expires_on = facepy.utils.get_extended_access_token(old_token, APP_ID, APP_SECRET)

with open("fbtoken.txt", "w") as f:
  f.write(new_token)

cron = CronTab() # get crontab for the current user
for oldjob in cron.find_comment("fbtokenrenew"):
  cron.remove(oldjob)
renew_date = expires_on - datetime.timedelta(1)
job.minute.on(0)
job.hour.on(1) # 1:00am
job.dom.on(renew_date.day)
job.month.on(renew_date.month) # on the day before it's meant to expire
cron.write()
