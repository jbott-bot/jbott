# Richard Darst, July 2009
#
# Minimal meetingLocalConfig.py
#
# This file is released into the public domain, or released under the
# supybot license in areas where releasing into the public domain is
# not possible.
#

import subprocess
import supybot.conf as conf
import supybot.registry as registry

class Config(object):
    
    # These, you might want to change:
    #MeetBotInfoURL = 'http://wiki.debian.org/MeetBot'
    #filenamePattern = '%(network)s/%(channel)s/%%Y/%(channel)s.%%F-%%H.%%M'
    def save_hook(self, realtime_update):
        if(not realtime_update):
            try:
                script = conf.supybot.plugins.MeetBot.syncscript()
                if script:
                    print ("save_hook, calling " + script)
                    subprocess.call([script],shell=True)
            except registry.NonExistentRegistryEntry:
                print("No supybot found - not doing save hook")
                return



