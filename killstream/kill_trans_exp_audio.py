"""
Kill Plex video transcoding streams only. All audio streams are left alone.

PlexPy > Settings > Notification Agents > Scripts > Bell icon:
        [X] Notify on playback start

PlexPy > Settings > Notification Agents > Scripts > Gear icon:
        Playback Start: kill_trans_exp_audio.py

"""
import ConfigParser
import io
import os.path
import requests
from plexapi.server import PlexServer

## EDIT THESE SETTINGS IF NOT USING THE CONFIG ##
PLEX_TOKEN = 'xxxxxx'
PLEX_URL = 'http://localhost:32400'

## DO NOT EDIT
config_exists = os.path.exists("../config.ini")
if config_exists:
    # Load the configuration file
    with open("../config.ini") as f:
        real_config = f.read()
        config = ConfigParser.RawConfigParser(allow_no_value=False)
        config.readfp(io.BytesIO(real_config))

        PLEX_TOKEN=config.get('plex-data', 'PLEX_TOKEN')
        PLEX_URL=config.get('plex-data', 'PLEX_URL')
##/DO NOT EDIT

DEFAULT_REASON = 'This stream has ended due to requiring video transcoding. ' \
         'Please raise your Remote Quality to Original to play this content.'

# Find platforms that have history in PlexPy in Play count by platform and stream type Graph
DEVICES = {'Android': 'Andriod message',
           'Chrome': 'Chrome message',
           'Plex Media Player': 'PMP message',
           'Chromecast': 'Chromecast message'}

USER_IGNORE = ('') # ('Username','User2')
##/EDIT THESE SETTINGS ##

sess = requests.Session()
sess.verify = False
plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)


def kill_session():
    for session in plex.sessions():
        user = session.usernames[0]
        media_type = session.type
        if user in USER_IGNORE or media_type == 'track':
            print('Ignoring {}\'s {} stream.'.format(user, media_type))
            pass
        try:
            trans_dec = session.transcodeSessions[0].videoDecision
            if trans_dec == 'transcode':
                platform = session.players[0].platform
                MESSAGE = DEVICES.get(platform, DEFAULT_REASON)
                # print(MESSAGE)
                print('Killing {user}\'s stream for transcoding video on {plat}.'.format(user=user, plat=platform))
                session.stop(reason=MESSAGE)
        except IndexError:
            # print('{} not transcoding.'.format(user))
            pass


if __name__ == '__main__':
    kill_session()
