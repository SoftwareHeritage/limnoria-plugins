###
# Copyright (c) 2017 Software Heritage Developers
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

import json
import traceback
import urllib.parse

import supybot.httpserver as httpserver
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.world as world
from supybot.i18n import PluginInternationalization
_ = PluginInternationalization('IcingaNotifier')

# Notification type map
NOTIFICATION_TYPES = {
    'PROBLEM': 'orange',
    'RECOVERY': 'green',
    'ACKNOWLEDGEMENT': 'blue',
    'FLAPPINGSTART': 'orange',
    'FLAPPINGSTOP': 'green',
    'FLAPPINGDISABLED': 'orange',
    'DOWNTIMESTART': 'dark grey',
    'DOWNTIMEEND': 'dark grey',
    'DOWNTIMECANCELLED': 'orange',
}

# Alert type map
STATES = {
    'UP': 'green',
    'DOWN': 'red',
    'UNREACHABLE': 'orange',
    'OK': 'green',
    'WARNING': 'yellow',
    'UNKNOWN': 'orange',
    'CRITICAL': 'red',
}



class IcingaCallback(httpserver.SupyHTTPServerCallback):
    name = 'IcingaNotifier'
    defaultResponse = _("""This endpoint only supports POST requests.""")
    errorResponse = _("""Bad request!""")

    def error(self, handler, path, message):
        response = "%s\n\n%s\n" % (self.errorResponse, message)
        response = response.encode('utf-8')
        handler.send_response(400)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    def doPost(self, handler, path, form):
        if not self.headers.get('Content-Type', '').startswith('application/json'):
            return self.error(
                handler, path,
                _('Wrong Content-Type: only application/json supported.'),
            )
        try:
            self.handle_message(path, json.loads(form.decode('utf-8')))
        except Exception:
            return self.error(handler, path, traceback.format_exc())
        else:
            handler.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', '0')
            self.end_headers()

    def handle_message(self, path, data):
        try:
            network, channel = urllib.parse.unquote(path[1:]).split('.', 1)
        except:
            raise ValueError("Must pass network.channel as argument")

        irc = world.getIrc(network)
        if not irc:
            raise ValueError("Unknown IRC network %s" % network)

        if not ircutils.isChannel(channel):
            raise ValueError("Wrong IRC channel name %s" % channel)

        if channel not in irc.state.channels:
            raise ValueError("Bot not joined to channel %s" % channel)

        irc.queueMsg(ircmsgs.privmsg(channel, self.format_msg(data)))

    def format_msg(self, data):
        service = data.get('service')
        if not service:
            tpl = "icinga {notification_type}: host {host} is {state}: {message}"
        else:
            tpl = "icinga {notification_type}: service {service} on {host} is {state}: {message}"

        state = data['state']
        state = ircutils.mircColor(state, STATES[state])
        notif_type = data['notification_type']
        notif_type = ircutils.mircColor(notif_type,
                                        NOTIFICATION_TYPES[notif_type])
        if service:
            service = ircutils.underline(data['service'])

        return tpl.format(
            notification_type=notif_type,
            host=ircutils.mircColor(data['host'], fg='light grey'),
            state=state,
            service=service,
            message=data['message'],
        )


class IcingaNotifier(callbacks.Plugin):
    """Pipe Icinga notifications to your channel"""

    def __init__(self, irc):
        self.__parent = super(IcingaNotifier, self)
        self.__parent.__init__(irc)

        callback = IcingaCallback()
        httpserver.hook('icinga', callback)

    def die(self):
        httpserver.unhook('icinga')

        self.__parent.die()


Class = IcingaNotifier


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
