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

import re
import time
import operator
import threading
from collections import defaultdict, namedtuple

import phabricator

import supybot.utils as utils
from supybot.commands import *
import supybot.world as world
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Phabricator')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

feed_announce = namedtuple('feed_announce', 'fetch_time max_epoch')
cache_entry = namedtuple('phid_cache_entry', 'data expiry')

class Phabricator(callbacks.PluginRegexp):
    """Integration with the Phabricator development collaboration tools"""
    threaded = True
    flags = re.VERBOSE
    regexps = [
        'phabricator_object_from_regexp',
        'phabricator_commit_from_regexp',
    ]
    phid_cache_expiry = 24 * 3600

    def __init__(self, irc):
        super().__init__(irc)

        self.default_conduit = None
        self._conduits = {}
        self._last_feed_announces = defaultdict(
                lambda: feed_announce(0, None))
        self._phid_object_cache = defaultdict(
                lambda: cache_entry(None, 0))
        self._phid_transaction_cache = defaultdict(
                lambda: cache_entry(None, 0))
        host = self.registryValue('phabricatorURI')
        token = self.registryValue('phabricatorConduitToken')
        if host and token:
            self.default_conduit = self.conduit_for_host_token(host, token)

    def wrapped_message(self, sender, message, **kwargs):
        line_length = 300
        wrapped = ircutils.wrap(message, line_length)
        for msg in wrapped:
            sender(msg, **kwargs)

    def conduit_for_host_token(self, host, token):
        if (host, token) in self._conduits:
            return self._conduits[host, token]

        conduit = phabricator.Phabricator(
            host=host,
            token=token,
        )
        conduit.update_interfaces()
        self._conduits[host, token] = conduit
        return conduit

    def conduit(self, recipient):
        host = self.registryValue(
            'phabricatorURI', channel=recipient
        )
        token = self.registryValue(
            'phabricatorConduitToken', channel=recipient
        )
        return self.conduit_for_host_token(host, token)

    def get_object_by_phid(self, recipient, phid,
                           skip_cache=False, object_fragment=None):
        objs = self.get_objects_by_phid(recipient, [phid], skip_cache)
        obj = objs.get(phid)
        if obj and object_fragment is not None:
            url = obj['uri']
            obj['uri'] = '%s%s' % (url, object_fragment)
        return obj

    def get_objects_by_phid(self, recipient, phids, skip_cache=False):
        objects = {}
        if not skip_cache:
            for phid in phids:
                obj, timeout = self._phid_object_cache[recipient, phid]
                if timeout > time.time():
                    objects[phid] = obj
        if set(objects) == set(phids):
            # If we already got all the phids we need in the cache,
            # no need to make a query
            return objects

        # Else, make a single request for all the objects
        # (even those in the cache; there's no harm in refreshing them)
        r = self.conduit(recipient).phid.query(phids=phids)
        for (phid, obj) in r.items():
            self._phid_object_cache[recipient, phid] = cache_entry(
                obj,
                time.time() + self.phid_cache_expiry
            )
        return dict(r)

    def get_transactions_by_phid(self, recipient, transactions_phids,
            object_phid, skip_cache=False):
        transactions = {}
        if not skip_cache:
            for phid in transactions_phids:
                trans, timeout = self._phid_transaction_cache[recipient,
                        object_phid, phid]
                if timeout > time.time():
                    transactions[phid] = trans
        if set(transactions) == set(transactions_phids):
            # If we already got all the phids we need in the cache,
            # no need to make a query
            return transactions

        # Else, make a single request for all the transactions
        # (even those in the cache; there's no harm in refreshing them)
        r = self.conduit(recipient).transaction.search(
                objectIdentifier=object_phid,
                constraints={'phids': transactions_phids})
        for trans in r['data']:
            self._phid_transaction_cache[recipient, object_phid, trans['phid']] = cache_entry(
                trans,
                time.time() + self.phid_cache_expiry
            )
            transactions[trans['phid']] = trans
        return dict(r)

    def get_commit_author_info(self, recipient, commit, type='author'):
        if not commit['%sPHID' % type]:
            return commit['%sName' % type]
        return self.get_user_by_phid(recipient, commit['%sPHID' % type])

    def get_user_by_phid(self, recipient, phid):
        author = self.get_object_by_phid(recipient, phid)
        return author['name']

    def get_repo(self, recipient, repo):
        conduit = self.conduit(recipient)
        res = conduit.diffusion.repository.search(
            constraints={'phids': [repo]}
        )
        if res.response['data']:
            return res.response['data'][0]

    def get_buildable(self, recipient, phid):
        conduit = self.conduit(recipient)
        res = conduit.harbormaster.querybuildables(phids=[phid])
        if not res.response['data']:
            return

        data = res.response['data'][0].copy()
        buildable = self.get_object_by_phid(recipient,
                                            data['buildablePHID'])
        data['buildable'] = buildable
        if buildable['type'] == 'DIFF':
            buildable = self.get_object_by_phid(recipient,
                                                data['containerPHID'])
            data['buildable'] = buildable

        return data

    def get_repo_name(self, repo):
        if not repo:
            return '<unknown repository>'
        for field in ('shortName', 'callsign', 'name'):
            if field in repo['fields'] and repo['fields'][field]:
                return repo['fields'][field]
        return repo['phid']

    def task_status_theme(self, status):
        return status

    def build_status_theme(self, status):
        return status

    def task_priority_theme(self, priority):
        return priority

    def diff_status_theme(self, status):
        return status

    def phabricator_object_from_regexp(self, irc, msg, match):
        r"""
        (?:
          ^         # start of line
         |(?<![:])\b # word boundary, not preceded by ":"
        )
        ([a-zA-Z])             # object type
        (\d+)                  # object id
        (\#\d+[-A-Za-z0-9]*)?  # optional comment link (as fragment)
        (?:
          $         # end of line
         |\b        # word boundary
        )
        """
        for recipient in msg.args[0].split(','):
            object_type = match.group(1).upper()
            lookup = {
                'B': self.conduit(recipient).harbormaster.build.search,
                'D': self.conduit(recipient).differential.revision.search,
                'P': self.conduit(recipient).paste.search,
                'T': self.conduit(recipient).maniphest.search,
            }
            if object_type not in lookup:
                return

            object_id = int(match.group(2))
            object_fragment = match.group(3)  # Or None as this is optional

            lookup_args = {
                'constraints': {
                    'ids': [object_id],
                },
            }

            query = lookup[object_type](**lookup_args)
            r = query.response
            if not r['data']:
                return

            object = r['data'][0]

            formatter = {
                'B': self.build_formatter,
                'D': self.diff_formatter,
                'P': self.paste_formatter,
                'T': self.task_formatter,
            }

            self.wrapped_message(
                irc.reply,
                formatter[object_type](recipient, object, object_fragment),
                notice=True,
                prefixNick=False,
                to=recipient,
            )

    def build_formatter(self, recipient, build, object_fragment=None):
        full_build = self.get_object_by_phid(recipient, build['phid'], True)
        buildable = self.get_buildable(recipient,
                                       build['fields']['buildablePHID'])
        details = []
        status = build['fields']['buildStatus']['name']
        details.append('status: %s' % self.build_status_theme(status))

        return "{id} for {buildable} ({details}): {title} <{url}>".format(
            id=ircutils.bold('B%s' % build['id']),
            buildable=buildable['buildable']['fullName'],
            title=build['fields']['name'],
            details=', '.join(details),
            url=full_build['uri'],
        )

    def diff_formatter(self, recipient, diff, object_fragment=None):
        full_diff = self.get_object_by_phid(recipient, diff['phid'], True,
                                            object_fragment=object_fragment)
        repo = self.get_repo(recipient, diff['fields']['repositoryPHID'])
        details = []
        details.append(
            'author: %s' % self.get_user_by_phid(
                recipient, diff['fields']['authorPHID']
            )
        )
        status = diff['fields']['status']['name']
        details.append(self.diff_status_theme(status))

        return "{id} ({details}) on {repo}: {title} <{url}>".format(
            id=ircutils.bold('D%s' % diff['id']),
            repo=ircutils.bold(self.get_repo_name(repo)),
            title=diff['fields']['title'],
            details=', '.join(details),
            url=full_diff['uri'],
        )

    def paste_formatter(self, recipient, paste, object_fragment=None):
        full_paste = self.get_object_by_phid(recipient, paste['phid'], True,
                                             object_fragment=object_fragment)
        details = []
        details.append(
            'author: %s' % self.get_user_by_phid(
                recipient, paste['fields']['authorPHID']
            )
        )

        return "{id} ({details}): {title} <{url}>".format(
            id=ircutils.bold('P%s' % paste['id']),
            title=paste['fields']['title'],
            details=', '.join(details),
            url=full_paste['uri'],
        )

    def task_formatter(self, recipient, task, object_fragment=None):
        full_task = self.get_object_by_phid(recipient, task['phid'], True,
                                            object_fragment=object_fragment)
        details = []
        details.append(
            'submitter: %s' % self.get_user_by_phid(
                recipient, task['fields']['authorPHID']
            )
        )
        if task['fields']['ownerPHID']:
            details.append(
                'owner: %s' % self.get_user_by_phid(
                    recipient, task['fields']['ownerPHID']
                )
            )
        priority = task['fields']['priority']['name']
        if priority != 'Normal':
            details.append('priority %s' % self.task_priority_theme(priority))
        status = task['fields']['status']['name']
        details.append('status: %s' % self.task_status_theme(status))

        return "{id} ({details}): {title} <{url}>".format(
            id=ircutils.bold('T%s' % task['id']),
            title=task['fields']['name'],
            details=', '.join(details),
            url=full_task['uri'],
        )

    def commit_formatter(self, recipient, commit, skip_details=None):
        if not skip_details:
            skip_details = []

        details = []
        if 'author' not in skip_details:
            author_info = self.get_commit_author_info(recipient, commit,
                                                      'author')
            details.append("author: %s" % author_info)
            committer_info = self.get_commit_author_info(recipient, commit,
                                                         'committer')
            if committer_info != author_info:
                details.append("committer: %s" % committer_info)

        repo_str = ''
        if 'repo' not in skip_details:
            repo = self.get_repo(recipient, commit['repositoryPHID'])
            repo_str = "%s/" % self.get_repo_name(repo)

        if details:
            details_str = ' (%s)' % ', '.join(details)
        else:
            details_str = ''

        return "{repo}{commit_id}{details} {summary} <{url}>".format(
            repo=repo_str,
            commit_id=ircutils.bold(commit['identifier'][:10]),
            summary=commit['summary'],
            details=details_str,
            url=str(commit['uri'])[:-30],
        )

    def phabricator_commit_from_regexp(self, irc, msg, match):
        r"""
        (?:
          ^          # start of line
         |(?!<[:])\b  # word boundary, not preceded by ":"
        )
        (r[A-Z]+)?([0-9a-f]{7,})
        (?:
          $          # end of line
         |\b         # word boundary
        )
        """
        for recipient in msg.args[0].split(','):
            commit_id = match.group(2)
            repo_id = match.group(1)
            query_params = {
                'names': [commit_id],
            }

            if repo_id:
                r = self.conduit(recipient).diffusion.repository.search(
                    constraints={'callsigns': [repo_id[1:]]},
                )
                if not r.response['data']:
                    return
                repo_phid = r.response['data'][0]['phid']
                query_params['repositoryPHID'] = repo_phid

            r = self.conduit(recipient).diffusion.querycommits(**query_params)
            if not r.response['identifierMap']:
                return

            commit_phid = r.response['identifierMap'][commit_id]
            commit = r.response['data'][commit_phid]

            self.wrapped_message(
                irc.reply,
                self.commit_formatter(recipient, commit),
                notice=True,
                prefixNick=False,
                to=recipient,
            )

    def __call__(self, irc, msg):
        super().__call__(irc, msg)
        threading.Thread(target=self._update_feeds).start()

    def _update_feeds(self):
        """Goes through all channels, and trigger an update on the ones
        which have an associated feed."""
        for irc in world.ircs:
            for channel in irc.state.channels:
                if self.registryValue('announce', channel):
                    self._update_feed_if_needed(irc, channel)

    def _update_feed_if_needed(self, irc, channel):
        """Triggers an update if the channel's feed should be updated."""
        recipient_key = (irc.network, channel)
        previous_announce = self._last_feed_announces[recipient_key]
        current_time = time.time()
        interval = self.registryValue('announce.interval', channel)
        if previous_announce.fetch_time + interval < current_time:
            max_epoch = self._update_feed(irc, channel,
                    previous_announce.max_epoch)
            self._last_feed_announces[recipient_key] = feed_announce(
                    fetch_time=current_time,
                    max_epoch=max_epoch)

    def _update_feed(self, irc, channel, after_epoch):
        """Send updates of a feed to a channel, and returns its max epoch."""
        conduit = self.conduit(channel)
        stories = conduit.feed.query(view='data')

        stories = sorted(stories.values(),
                key=operator.itemgetter('epoch'))

        objects = self.get_objects_by_phid(channel,
                [story['data']['objectPHID'] for story in stories])

        after_epoch = after_epoch or 0
        for story in stories:
            if (after_epoch > 0 and # Don't announce on the first run
                    story['epoch'] > after_epoch):
                self._announce_story(irc, channel, story,
                        objects[story['data']['objectPHID']])
        max_epoch = max(story['epoch'] for story in stories)
        return max(after_epoch, max_epoch)

    def _announce_story(self, irc, channel, story, obj):
        """Send a story to a channel."""
        username_blacklist = self.registryValue('announce.usernameBlacklist',
                    channel)
        transactions = self.get_transactions_by_phid(channel,
                list(story['data']['transactionPHIDs']), obj['phid'])
        actions = defaultdict(lambda: [])
        for trans in transactions['data']:
            actions[self.get_user_by_phid(channel, trans['authorPHID'])] \
                    .append(trans['type'])

        parts = []
        for (author, author_actions) in actions.items():
            if author in username_blacklist:
                continue
            parts.append('{} from {}'.format('+'.join(author_actions), author))
        msg = format('%s; on %s %u',
                ', '.join(parts),
                obj['fullName'],
                obj['uri'],
            )
        if parts:
            irc.queueMsg(ircmsgs.privmsg(channel, msg))



Class = Phabricator


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
