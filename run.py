from app.Managers.ChannelManager import ChannelManager
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently
import pandas as pd

if __name__ == '__main__':



    # Get inputs from the User
    selection = input("What do you want to do?\n1) Bann users from a given channel?\n2) Export Userlist for a given Channel? : ")

    if selection == "1":
        channel = input("What channel do you want to bann users from?"
                        "\n Keep empty to bann from 'DREAMToken'")
        channel = "DREAMToken" if channel == "" else channel
        # Connect the Channel Manager
        mng = ChannelManager(channel)

        # Load the data from the banlist
        banlist = pd.read_csv('./data/Telegram_Channel_banlist.csv')
        banlist = banlist['telegram_id']

        # Call the ban
        reset = input("Do you want to create a new index of current channel users? Y/N : ")
        force_refetch = True if reset == "Y" else False

        mng.restrict_users(banlist, type='bann', force_refetch=force_refetch)

    if selection == "2":
        channel = input("What channel do you want to export the users from?"
                        "\n Keep empty to create Userlist from 'DREAMToken'")
        channel = "DREAMToken" if channel == "" else channel
        print("Creating Channel Userlist as '{}_userlist.csv : ".format(channel))
        # Connect to the channel
        mng = ChannelManager(channel)

        # Export the userset
        mng.export_userlist()













