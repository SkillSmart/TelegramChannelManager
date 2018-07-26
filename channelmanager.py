from Managers import ChannelManager
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently
import pandas as pd

# Connect the Channel Manager
mng = ChannelManager("DREAMToken")

# Load the data from the banlist
banlist = pd.read_csv('Telegram_Channel_banlist.csv')
banlist = banlist['telegram_id']

#Call the ban
mng.restrict_users(banlist, type='bann', force_refetch=True)













