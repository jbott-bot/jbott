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

from supybot.test import *

class JiraTestCase(PluginTestCase):
    plugins = ('Jira',)

    def setUp(self):
        # Set conf variables appropriately.
        conf.supybot.plugins.Jira.server.setValue('https://issues.jboss.org/rpc/xmlrpc')
        conf.supybot.plugins.Jira.user.setValue('') #when testing set these to something real
        conf.supybot.plugins.Jira.password.setValue('') # yes, its a hack but not found a good way to externalize it
        conf.supybot.plugins.Jira.browseurl.setValue('https://issues.jboss.org/browse/')
        PluginTestCase.setUp(self)
        
    def testJira(self):
        self.assertHelp('jira')
        self.assertResponse('jira JBIDE-1', 'Feature Request: [JBIDE-1] Create Jave Server Faces designer plugin [Closed, Major, (JSF), Unassigned] https://issues.jboss.org/browse/JBIDE-1')

    def testMulticomponent(self):
        self.assertHelp('jira')
        self.assertResponse('jira JBIDE-7775', 'Task: [JBIDE-7775] Provide documentation URL link for the latest release  [Open, Minor, (Build/Releng, Help), mcaspers] https://issues.jboss.org/browse/JBIDE-7775')

    def testNonExistingJira(self):
        self.assertNoResponse('jira wonka-issue')

    def testNonExistingVsWorking(self):
        self.assertNoResponse('jira whatever')
        self.assertResponse('jira JBIDE-1', 'Feature Request: [JBIDE-1] Create Jave Server Faces designer plugin [Closed, Major, (JSF), Unassigned] https://issues.jboss.org/browse/JBIDE-1')

    def testDontReplyTwice(self):
        self.assertResponse('jira JBIDE-1', 'Feature Request: [JBIDE-1] Create Jave Server Faces designer plugin [Closed, Major, (JSF), Unassigned] https://issues.jboss.org/browse/JBIDE-1')
        self.assertNoResponse('jira JBIDE-1')
            
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
