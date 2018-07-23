from Managers import ChannelManager
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently
import csv

# Connect the Channel Manager
mng = ChannelManager("DREAMToken")

# Test
print(mng.client.get_me())
print(mng.me)

participants = mng.list_participants(limit=100000)

mng.export_userlist()












