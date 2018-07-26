from Managers import ChannelManager
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently
import pandas as pd

# Connect the Channel Manager
mng = ChannelManager("DREAMToken")
# mng.list_participants(limit=150)

# Load the data from the banlist
banlist = pd.read_csv('Telegram_Channel_banlist.csv')
banlist = banlist['telegram_id']


#Call the ban
mng.restrict_users(banlist, 'bann', limit=None, force_refetch=True)


mng.export_userlist()












