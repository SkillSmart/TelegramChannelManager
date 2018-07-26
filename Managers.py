# This defines the core functionalities we want to run on the Telegram client
import os.path
import time
from connecting import  connect_client
from telethon.tl.functions.channels import GetParticipantRequest, GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChannelParticipantsSearch

# Imports for banning and restricting access
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChannelBannedRights

# Status checking
from telethon.tl.types import UserStatusOffline, UserStatusOnline, UserStatusRecently
# Imports for debugging
import logging
# Caching
import pickle
# Export
import csv

class ChannelManager:
    """
    Provides management functionalities for channels created from this account.

    - Clear join messages from the interface
    - Export a list of all currently registerd users
    -
    """
    def __init__(self, channel=None, client=None):
        if not client:
            self.client = connect_client()
        self.me = self.client.get_me()
        # This stores [offset: length] information for all caches for this dataset
        self.cached = {}
        self.user_dict = None
        self.channel_participants = None
        if channel:
            self.connect(channelName=channel)


    def connect(self, channelName):
        """
        Connects to a given channel so all methods can be called directly upon this channel object,
        :param channelName:
        :return: Null
        """
        self.channel = self.client.get_entity("t.me/{}".format(channelName))


    def search_participant(self, query=''):
        pass

    def retrieve_participants(self, limit=100000, offset=0, force_refetch=False):
        """
        Retrieves a list of n to all members of a given channel.
        Checks if there is a connection to a channel already, if not it connects to it using the connect
        function. It stores the participant list on the object, to make it available to export and access
        functions.
        :return:
        """
        aggressive = False
        if (limit == None or limit > 10000):
            aggressive = True

        if os.path.exists('./bin/{}.Participant-list{}-{}.pkl'.format(limit, self.channel.title, limit)) and not force_refetch:
            with open('./bin/{}.Participant-list{}-{}.pkl'.format(limit, self.channel.title, limit), 'rb') as input:
                self.channel_participants = pickle.load(input)
        else:
            # Cache the Participants to the object
            print("Fetching {} channel participants for {}".format(limit, self.channel.title))
            self.channel_participants = self.client.get_participants(self.channel, aggressive=aggressive)

            with open('./bin/{}.Participant-list{}-{}.pkl'.format(limit, self.channel.title, limit), 'wb') as output:
                pickle.dump(self.channel_participants, output, pickle.HIGHEST_PROTOCOL)

    def create_userdict(self, force_refetch=False):
        """
        Creates a dict of all users in the channel supporting the indexing by id
        Stores the dict on the Object for quick access, additonally caches it to disk
        :return: None
        """
        if not self.channel_participants:
            self.retrieve_participants()

        # Create the dictionary
        if os.path.exists('./bin/{}-participant-dict-{}.pkl'.format(self.channel.title, len(self.channel_participants))) and not force_refetch:
            print("Loading existing Participant Channel dict from cache")
            with open('./bin/{}-participant-dict-{}.pkl'.format(self.channel.title, len(self.channel_participants)), 'rb') as input:
                self.user_dict = pickle.load(input)
        else:
            print("Creating new Userdict from Channel List")
            self.user_dict = { participant.id : participant for participant in self.channel_participants }
            with open('./bin/{}-participant-dict-{}.pkl'.format(self.channel.title, len(self.channel_participants)), 'wb') as output:
                pickle.dump(self.user_dict, output, pickle.HIGHEST_PROTOCOL)

        print("Successfully loaded {} users into the dict".format(len(self.user_dict)))

    def list_participants(self, limit=100, offset=0):
        """
        Either retrieves already cached data from the channel object, or retrieves a new list of channel
        subscribers to work with.

        1. Checks if the data is available in cache, and if the count for that cache is within a reasonable range
        2. Then decides to either read data from cache (object dump), or call subroutine to retrieve the current list of participants
        3. When done reading the data, it dumps object to disk to retrieve later
        :param limit:
        :param offset:
        :return:
        """

        #  1. Check if data is available in cache load it
        if os.path.exists('./bin/{}_participants-{}-{}.pkl'.format(self.channel.title, offset, limit)) and self.cached.get(offset, 0) <= limit:
            print("Loaded cached participant list of {} users for channel {}".format(limit, self.channel.title))
            with open('./bin/{}_participants-{}-{}.pkl'.format(self.channel.title, offset, limit), 'rb') as input:
                self.channel_participants = pickle.load(input)
        # Otherwise retrieve data and store to pickle file
        else:
            print("Starting collection of {} user records from channel {}".format(limit, self.channel.title))
            self.retrieve_participants(limit)
            if not os.path.exists('./bin'):
                os.mkdir('./bin')
            with open('./bin/{}_participants-{}-{}.pkl'.format(self.channel.title, offset, limit), 'wb') as output:
                pickle.dump(self.channel_participants, output, pickle.HIGHEST_PROTOCOL)
            self.cached[offset] = limit


        # 3. Finish the job
        return self.channel_participants

    def restrict_users(self, userlist, type=['bann', 'read-only', 'write-only', 'no-pictures'], offset= None,  limit=None, calls_throttle=29, force_refetch=False):
        if not self.user_dict:
            self.create_userdict(force_refetch=force_refetch)
        n_banned = 0
        for id, userid in enumerate(userlist):

            try:
                user = self.user_dict[userid]
                self.restrict_user(user, type=type)
                print("{}: Restricted {} to {}".format(n_banned, user.username, type))
                # Throttle the requests
                throttle = 60 / calls_throttle
                time.sleep(throttle)
                n_banned += 1
            except:
                if id % 250 == 0: print("So far {} out of {} people additionally banned from the list".format(n_banned, id))



    def restrict_user(self, user, duration=7, type=['bann', 'read-only', 'write-only', 'no-pictures']):
        """
        Manages different ways to restrict the user from accessing the channel.
        - "bann": Totally revokes the users rights on the channel
        - "read-only": Only allows the user to read the channel
        - "write-only": Only allows textual comments. Any other posting is prohibited
        - "no-pictures": Restricts the user from posting pictures on the channel
        :param type:
        :return:
        """
        dict = {
            'bann': {
                'until_date': None,
                'view_messages': True
            },
            'read-only': {
                'until_date': duration,
                'view_messages': None,
                'send_messages': True,
                'send_media': True,
                'send_stickers':True,
                'send_gifs':True,
                'send_games':True,
                'send_inline':True,
                'embed_links':True
            },
            'write-only': {
                'until_date': duration,
                'view_messages': None,
                'send_messages': None,
                'send_media': True,
                'send_stickers': True,
                'send_gifs': True,
                'send_games': True,
                'send_inline': True,
                'embed_links': True
            },
            'no-pictures': {
                'until_date': duration,
                'view_messages': None,
                'send_messages': None,
                'send_media': None,
                'send_stickers': True,
                'send_gifs': True,
            }
        }

        self.client(EditBannedRequest(
            self.channel, user, ChannelBannedRights(**dict[type])
        ))


    def export_userlist(self, type='csv'):
        """
        Creates a dict binding from each user object extracted from the userlist for the channel.
        Then writes the
        :param type:
        :return:
        """
        # Save user to csv
        with open('{}_userlist.csv'.format(self.channel.title), 'w', encoding='utf-8') as output:
            # Transform the user object
            users = [{'id': user.id,
                      'first_name': user.first_name,
                      'last_name': user.last_name,
                      'username': user.username,
                      'phone': user.phone,
                      'lang': user.lang_code,
                      'is_self': int(user.is_self),
                      'contact': int(user.contact),
                      'mutual_contact': int(user.mutual_contact),
                      'deleted': int(user.deleted),
                      'bot': int(user.bot),
                      'bot_chat_history': user.bot_chat_history,
                      'bot_nochats': user.bot_nochats,
                      'verified': int(user.verified),
                      'restricted': int(user.restricted),
                      'min': user.min,
                      'bot_inline_geo': user.bot_inline_geo,
                      'access_hash': user.access_hash,
                      # 'photo_id': user.photo.photo_id,
                      # 'photo_small': user.photo_small,
                      # 'photo_big': user.photo_big,
                      'is_online': int(isinstance(user.status, UserStatusOnline)),
                      'recently_online': int(isinstance(user.status, UserStatusRecently)),
                      'is_offline': int(isinstance(user.status, UserStatusOffline)),
                      'last_online': user.status.was_online if(isinstance(user.status, UserStatusOffline)) else None,
                      'bot_info_version': user.bot_info_version,
                      'restriction_reason': user.restriction_reason,
                      'bot_inline_placeholder': user.bot_inline_placeholder
                      } for user in self.channel_participants]

            # Generate the writer object
            writer = csv.DictWriter(output, list(users[0].keys()), lineterminator='\n')
            writer.writeheader()

            writer.writerows(users)


    def broadcast_message(self, message):
        """
        Takes a message and broadcasts it to a given channel at set intervals
        :param message:
        :return: Boolean (Success Message)
        """
        pass


    # Manage Logging on the channel
    def set_logging(self, level=['debugging', 'warning']):
        """
        Checks the status of logging for the registered channel
        :return: (loggin_active: Boolean, type_loggin: String)
        """
        log_level = {
            'debugging': logging.DEBUG,
            'warning': logging.WARNING
        }

        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('telethon').setLevel(level=level)
        self.logging_status = level


