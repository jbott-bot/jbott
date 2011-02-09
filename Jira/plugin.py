###
# Copyright (c) 2011, Max Rydahl Andersen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import traceback
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import pickle
import os.path

from datetime import datetime, timedelta

from xmlrpclib import Server, Fault

import collections

class Cache(dict):
    def __init__(self, n, *args, **kwds):
        self.n = n
        self.queue = collections.deque()
        dict.__init__(self, *args, **kwds)

    def __setitem__(self, k, v):
        self.queue.append(k)
        dict.__setitem__(self, k, v)
        if len(self) > self.n:
            oldk = self.queue.popleft()
            del self[oldk]
            
def getName(id, fields):
    if id == None:
        return "None"
    if fields == None:
        return id
    for i, v in enumerate(fields):
        val = v['id']
        if val and val.lower() == id.lower():
            return v['name']
    return id.title()


def encode(s):
    '''Handle utf-8 encodings'''
    if s == None:
        return "None"
    if type(s) == unicode:
        s = s.encode("utf-8")
    return str(s)
    
class Jira(callbacks.Plugin):
    """Add the help for "@plugin help Jira" here
    This should describe *how* to use this plugin."""
    threaded = True

    s = ""
    auth = ""
    jiradata = dict()
    recent = Cache(10)
    
    def _auth(self):
        server = self.registryValue('server');
        self.s = Server(server)
        self.log.info('Authenticaing on server: ' + server + ' with ' + self.registryValue('user'))
        self.auth = self.s.jira1.login(self.registryValue('user'), self.registryValue('password'))

    def __init__(self, irc):
        self.__parent = super(Jira, self)
        self.__parent.__init__(irc)

        self._auth()
        
        jiracache = "jiracache.pck"
        if(os.path.exists(jiracache)):
            file = open(jiracache, "r") # read mode
            self.log.info("Reading cached jiradata from " + str(file))
            self.jiradata = pickle.load(file)
            file.close()
        else:
            self.log.info('Jira Get Issue Types')
            self.jiradata['types'] = self.s.jira1.getIssueTypes(self.auth)
            self.log.info('Jira Get Issue Subtask Types')
            self.jiradata['subtypes'] = self.s.jira1.getSubTaskIssueTypes(self.auth)
            self.log.info('Jira Get Statuses')
            self.jiradata['statuses'] = self.s.jira1.getStatuses(self.auth)
            self.log.info('Jira Get Priorities')  
            self.jiradata['priorities'] = self.s.jira1.getPriorities(self.auth)
            self.log.info('Jira Get Resolutions')  
            self.jiradata['resolutions'] = self.s.jira1.getResolutions(self.auth)
            file = open(jiracache, "w") # write mode
            self.log.info("Writing jiradata to " + str(file))
            pickle.dump(self.jiradata, file)
            file.close()
        
    
    def jira(self, irc, msg, args, text):
        """<text>

        Returns the arguments given it.  Uses our standard substitute on the
        string(s) given to it; $nick (or $who), $randomNick, $randomInt,
        $botnick, $channel, $user, $host, $today, $now, and $randomDate are all
        handled appropriately.
        """
        text = ircutils.standardSubstitute(irc, msg, text)
        result = []
        self.log.info('Looking up: ' + text)

        if(text in self.recent):
            last = self.recent[text]
            now = datetime.now()
            self.log.info('last seen at ' + str(last) + ' now is ' + str(now) + ' ' + str(now-last))
            if ((now - last) < timedelta (seconds = 10)):
                irc.noReply()
                return
        else:
            self.log.info('new lookup')
            
        self.recent[text] = datetime.now()

        try:
            issue = self.s.jira1.getIssue(self.auth, text)

            #for k,v in sorted(issue.items()):
            #	irc.reply(k, prefixNick=True)

            #irc.reply(issue['description'], prefixNick=True)
            result.append(getName(issue['type'], self.jiradata['types']) + ": ")
            result.append("[" + issue['key'] + "]")
            result.append(" " + issue['summary'])
            result.append(" [")
            result.append(getName(issue['status'], self.jiradata['statuses']) + ", ")
            result.append(getName(issue['priority'], self.jiradata['priorities']) + ", ")

            if('components' in issue):
                components = []
                for f in issue['components']:
                    components.append(encode(f['name']))
                if(components):
                    result.append("(")
                    result.append(", ".join(str(x) for x in components))
                    result.append("), ")
            if('assignee' in issue):
                result.append(issue['assignee'])  #should be username ?
            else:
                result.append("Unassigned")
            result.append("] ")
            result.append(self.registryValue('browseurl') + issue['key'])
            irc.reply("".join(result), prefixNick=False)
        except Fault, f:
            self.log.info("Fault when looking up " + text)
            self.log.info(str(Fault))
            irc.noReply()
            self._auth()
    jira = wrap(jira, ['text'])


Class = Jira


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
