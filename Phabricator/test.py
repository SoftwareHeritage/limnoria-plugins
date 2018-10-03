###
# Copyright (c) 2018 Software Heritage Developers
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

import supybot.conf as conf
from supybot.test import *

ENTRY1 = {
		'authorPHID': 'PHID-USER-fozivtfr457sc7smrhtv',
		'chronologicalKey': '6607424649221995233',
		'class': 'PhabricatorApplicationTransactionFeedStory',
		'data': {'objectPHID': 'PHID-TASK-lwuvnwjjnenqsyan73om',
				 'transactionPHIDs': {'PHID-XACT-TASK-cgdt45mjjymbxpk': 'PHID-XACT-TASK-cgdt45mjjymbxpk'}},
		'epoch': 1538410933}

ENTRY2 = {
		'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
		'chronologicalKey': '6607410428317095759',
		'class': 'PhabricatorApplicationTransactionFeedStory',
		'data': {'objectPHID': 'PHID-DREV-jaamseb4cyq2glp3ekmr',
				 'transactionPHIDs': {'PHID-XACT-DREV-lo5bwt2qii6dbud': 'PHID-XACT-DREV-lo5bwt2qii6dbud',
									  'PHID-XACT-DREV-q4kayyycsd4izyj': 'PHID-XACT-DREV-q4kayyycsd4izyj'}},
		'epoch': 1538407622}

ENTRY3 = {
        'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
        'chronologicalKey': '6607737853965443787',
        'class': 'PhabricatorApplicationTransactionFeedStory',
        'data': {'objectPHID': 'PHID-DREV-ypvg646gtojpnfcszoiv',
                 'transactionPHIDs': {'PHID-XACT-DREV-5wapkzlcy3bhup4': 'PHID-XACT-DREV-5wapkzlcy3bhup4',
                                      'PHID-XACT-DREV-b7dsk7hobiqoxn6': 'PHID-XACT-DREV-b7dsk7hobiqoxn6'}},
        'epoch': 1538483857}

FEED1 = {
 'phid-stry-zuicf6fhi4esag22cmw2': ENTRY2,
 }

FEED2 = {
 'phid-stry-zuafozdksyhxqixmqej3': ENTRY1,
 'phid-stry-zuicf6fhi4esag22cmw2': ENTRY2,
 }

FEED3 = {
 'phid-stry-zuafozdksyhxqixmqej3': ENTRY1,
 'phid-stry-zuicf6fhi4esag22cmw2': ENTRY2,
 'phid-stry-zzphs53tpt6j7equbkp7': ENTRY3,
 }

QUERY_PHID = {
'PHID-DREV-jaamseb4cyq2glp3ekmr': {'fullName': 'D454: Provide Sphinx targets '
                                                'in docs/images/ (see D453).',
                                    'name': 'D454',
                                    'phid': 'PHID-DREV-jaamseb4cyq2glp3ekmr',
                                    'status': 'open',
                                    'type': 'DREV',
                                    'typeName': 'Differential Revision',
                                    'uri':
                                    'https://forge.softwareheritage.org/D454'},
'PHID-TASK-lwuvnwjjnenqsyan73om': {'fullName': 'T611: support for external '
                                                'definitions in the '
                                                'svn/subversion loader',
                                    'name': 'T611',
                                    'phid': 'PHID-TASK-lwuvnwjjnenqsyan73om',
                                    'status': 'open',
                                    'type': 'TASK',
                                    'typeName': 'Maniphest Task',
                                    'uri':
                                    'https://forge.softwareheritage.org/T611'},
'PHID-USER-fozivtfr457sc7smrhtv': {'fullName': 'ardumont (Antoine R. Dumont)',
                                    'name': 'ardumont',
                                    'phid': 'PHID-USER-fozivtfr457sc7smrhtv',
                                    'status': 'open',
                                    'type': 'USER',
                                    'typeName': 'User',
                                    'uri':
                                    'https://forge.softwareheritage.org/p/ardumont/'},
'PHID-DREV-ypvg646gtojpnfcszoiv': {'fullName': "D453: Make 'make' in "
                                                "swh-*/docs/ should run 'make' "
                                                'in swh-*/docs/images/',
                                    'name': 'D453',
                                    'phid': 'PHID-DREV-ypvg646gtojpnfcszoiv',
                                    'status': 'open',
                                    'type': 'DREV',
                                    'typeName': 'Differential Revision',
                                    'uri':
                                    'https://forge.softwareheritage.org/D453'},
'PHID-USER-jyszzzys2aaakr2q2ijx': {'fullName': 'vlorentz (vlorentz)',
                                    'name': 'vlorentz',
                                    'phid': 'PHID-USER-jyszzzys2aaakr2q2ijx',
                                    'status': 'open',
                                    'type': 'USER',
                                    'typeName': 'User',
                                    'uri':
                                    'https://forge.softwareheritage.org/p/vlorentz/'},
}

SEARCH_TRANSACTION = {
	('PHID-TASK-lwuvnwjjnenqsyan73om', ('PHID-XACT-TASK-cgdt45mjjymbxpk',)):
		{'cursor': {'after': None, 'before': None, 'limit': 100},
		 'data': [{'authorPHID': 'PHID-USER-fozivtfr457sc7smrhtv',
				   'comments': [{'authorPHID': 'PHID-USER-fozivtfr457sc7smrhtv',
								 'content': {'raw': 'foobar1\nspam\negg'},
								 'dateCreated': 1538410933,
								 'dateModified': 1538410933,
								 'id': 2413,
								 'phid': 'PHID-XCMT-6sqdj7jbbgpituemximf',
								 'removed': False,
								 'version': 1}],
				   'dateCreated': 1538410933,
				   'dateModified': 1538410933,
				   'fields': {},
				   'id': 22700,
				   'objectPHID': 'PHID-TASK-lwuvnwjjnenqsyan73om',
				   'phid': 'PHID-XACT-TASK-cgdt45mjjymbxpk',
				   'type': 'comment'}]},
    ('PHID-DREV-ypvg646gtojpnfcszoiv', ('PHID-XACT-DREV-5wapkzlcy3bhup4',
        'PHID-XACT-DREV-b7dsk7hobiqoxn6')):
{'cursor': {'after': None, 'before': None, 'limit': 100},
 'data': [{'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
           'comments': [{'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
                         'content': {'raw': ''},
                         'dateCreated': 1538483876,
                         'dateModified': 1538483876,
                         'id': 2255,
                         'phid': 'PHID-XCMT-gvlxm7ka3qse5ycpvh5n',
                         'removed': True,
                         'version': 2},
                        {'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
                         'content': {'raw': ''},
                         'dateCreated': 1538483857,
                         'dateModified': 1538483857,
                         'id': 2254,
                         'phid': 'PHID-XCMT-gsnm5pxmy4tb7mpr3vcg',
                         'removed': False,
                         'version': 1}],
           'dateCreated': 1538483857,
           'dateModified': 1538483876,
           'fields': {},
           'id': 8824,
           'objectPHID': 'PHID-DREV-ypvg646gtojpnfcszoiv',
           'phid': 'PHID-XACT-DREV-5wapkzlcy3bhup4',
           'type': 'comment'},
          {'authorPHID': 'PHID-USER-jyszzzys2aaakr2q2ijx',
           'comments': [],
           'dateCreated': 1538483857,
           'dateModified': 1538483857,
           'fields': {'commitPHIDs': [],
                      'new': 'PHID-DIFF-qdape3nidx5nk3tq6vw5',
                      'old': 'PHID-DIFF-ymevkypj7damk72gisvq'},
           'id': 8823,
           'objectPHID': 'PHID-DREV-ypvg646gtojpnfcszoiv',
           'phid': 'PHID-XACT-DREV-b7dsk7hobiqoxn6',
           'type': 'update'}]}
    }

class BaseMockConduit:
    class phid:
        @classmethod
        def query(cls, *, phids):
            return {phid: QUERY_PHID[phid] for phid in phids}

    class transaction:
        @classmethod
        def search(cls, *, objectIdentifier, constraints):
            assert set(constraints) == {'phids'}, constraints
            return SEARCH_TRANSACTION[objectIdentifier,
                tuple(sorted(constraints['phids']))]

class PhabricatorTestCase(ChannelPluginTestCase):
    plugins = ('Phabricator',)
    config = {
            'supybot.plugins.Phabricator.announce.interval': 1,
            }

    def testAnnounce(self):
        nb_mock_calls = 0

        class MockConduit(BaseMockConduit):
            class feed:
                @classmethod
                def query(cls, *, view):
                    nonlocal nb_mock_calls
                    nb_mock_calls += 1
                    self.assertEqual(view, 'data')
                    return current_feed

        def mock_get_conduit(*args):
            return MockConduit
        self.irc.getCallback('Phabricator').conduit_for_host_token = \
                mock_get_conduit

        try:
            # Check there are no announce the first time.
            current_feed = FEED1
            self.assertNotError('config channel plugins.Phabricator.announce True')
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 1, m)
            self.assertIs(m, None)
            time.sleep(1.1)
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 2, m)
            self.assertIs(m, None)

            # A new story, that should be announced only after the time interval.
            current_feed = FEED2
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 2, m)
            self.assertIs(m, None)
            time.sleep(1.1)
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 3, m)
            self.assertIsNot(m, None)
            self.assertEqual(m.args[1],
                    'comment from ardumont; on T611: support for external '
                    'definitions in the svn/subversion loader '
                    '<https://forge.softwareheritage.org/T611>', m)

            # Another new story.
            current_feed = FEED3
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 3, m)
            self.assertIs(m, None)
            time.sleep(1.1)
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 4, m)
            self.assertIsNot(m, None)
            self.assertIn(m.args[1],
                    "comment+update from vlorentz; on D453: Make 'make' in "
                    "swh-*/docs/ should run 'make' in swh-*/docs/images/ "
                    "<https://forge.softwareheritage.org/D453>",
                    m)
        finally:
            self.assertNotError('config channel plugins.Phabricator.announce False')

    def testAnnounceBlacklist(self):
        nb_mock_calls = 0

        class MockConduit(BaseMockConduit):
            class feed:
                @classmethod
                def query(cls, *, view):
                    nonlocal nb_mock_calls
                    nb_mock_calls += 1
                    self.assertEqual(view, 'data')
                    return current_feed

        def mock_get_conduit(*args):
            return MockConduit
        self.irc.getCallback('Phabricator').conduit_for_host_token = \
                mock_get_conduit


        try:
            # Check there are no announce the first time.
            current_feed = FEED1
            self.assertNotError('config channel plugins.Phabricator.announce True')
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 1, m)
            self.assertIs(m, None)
            time.sleep(1.1)
            m = self.getMsg(' ', timeout=0.1)
            self.assertEqual(nb_mock_calls, 2, m)
            self.assertIs(m, None)

            # A new story, from a blacklisted username
            bl_conf = conf.supybot.plugins.Phabricator.announce.usernameBlacklist
            with bl_conf.context({'ardumont'}):
                current_feed = FEED2
                m = self.getMsg(' ', timeout=0.1)
                self.assertEqual(nb_mock_calls, 2, m)
                self.assertIs(m, None)
                time.sleep(1.1)
                m = self.getMsg(' ', timeout=0.1)
                self.assertEqual(nb_mock_calls, 3, m)
                self.assertIs(m, None)
        finally:
            self.assertNotError('config channel plugins.Phabricator.announce False')




# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
