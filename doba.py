# This Python file uses the following encoding: utf-8
import os
import glob
import codecs
import hashlib
import datetime
import optparse

import cherrypy
import pystache

import profane

parser = optparse.OptionParser()
parser.add_option("-p", "--port", type="int", dest="port", help="port on which  to run the server", default="8080")
(options, args) = parser.parse_args()

cherrypy.config.update({"server.socket_host": '127.0.0.1', # IPv6 binding shenanigans
                        "tools.encode.on": True,
                        "tools.encode.encoding": "utf8",
                        "server.environment": "production",
                        "server.socket_queue_size": 5,
                        "server.log_to_screen": True,
                        "server.socket_timeout": 500,
                        "server.socket_port": options.port})

# Load the templates at server start time - will need to restart to pick up changes
page_template = file("templates/index.template").read()
entry_template = file("templates/entry.template").read()

entries_path = 'entries/'

def entry_from_file(entry, is_last=False):
    return {'entry_date': datetime.datetime.fromtimestamp(os.path.getmtime(entry)).strftime("%a, %d %b %Y %H:%M:%S UTC"),
            'filename': entry,
            'content': profane.unswear(codecs.open(entry, 'r', 'utf-8').read()),
            'twitter_id': 'lampholder',
            'hashtag': hashlib.md5(os.path.splitext(entry)[0][8:]).digest().encode("base64")[0:8],
            'is_last': is_last}

class DobaServer(object):
    @cherrypy.expose
    def index(self):
        global page_template, entry_template, path
        entries = glob.glob(os.path.join(entries_path, '*.entry'))
        entries.sort(key = lambda x: os.path.getmtime(x), reverse = True)
        content = u""
        for entry in entries:
            content = content + pystache.render(entry_template, entry_from_file(entry, entry == entries[-1]))
        return pystache.render(page_template, {'content': content})

    @cherrypy.expose
    def entries(self, entry):
        global page_template, entry_template, path
        content = pystache.render(entry_template, entry_from_file(os.path.join(entries_path, entry), True))
        return pystache.render(page_template, {'content': content})

cherrypy.quickstart(DobaServer())
