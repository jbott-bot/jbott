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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from xmlrpclib import Server

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
    
    def __init__(self, irc):
        self.__parent = super(Jira, self)
        self.__parent.__init__(irc)

        server = self.registryValue('server');
        self.log.info('Using server: ' + server)
        self.s = Server(server)
        self.log.info('Jira Login')
        self.auth = self.s.jira1.login(self.registryValue('user'), self.registryValue('password'))
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
            result.append("(")
            for f in issue['components']:
                result.append(encode(f['name']))
            result.append("), ")
        if('assignee' in issue):
            result.append(issue['assignee'])  #should be username ?
        else:
            result.append("Unassigned")
        result.append("] ")
        result.append(self.registryValue('browseurl') + issue['key'])
        irc.reply("".join(result), prefixNick=False)

    jira = wrap(jira, ['text'])


Class = Jira


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
