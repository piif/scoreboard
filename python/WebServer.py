#!/usr/bin/env python
# TODO
# ajouter readme sur dir des icones
# revoir config portail captif, notamment gerer un dns fake ?
# jQuery light pour mobile ?
#  voir deja si ca demarre avec la version slim ?
# comment debugger le probleme des cookies ?

from sys import argv
from os.path import abspath, dirname

from gevent import monkey, queue; monkey.patch_all()
from time import time,sleep
from bottle import route, request, response
import bottle # for static_file, redirect, run
import json

import argparse
from symbol import argument

parser = argparse.ArgumentParser()
parser.add_argument('--fake', dest = 'fake', action='store_const',
                    const = True, default = False, help = "fake mode")
parser.add_argument('--port', type = int, dest = 'listenPort',
                    default = 9090, help = "listen port")
parser.add_argument('--verbose', dest = 'verbose', action='store_const',
                    const = True, default = False, help = "log more")
# TODO : add config_dir, static_dir, content_dir
cmdArgs = parser.parse_args()

def LOG(*args):
    if cmdArgs.verbose:
        print args

root_dir = abspath(dirname(argv[0]))
config_dir = dirname(root_dir) + "/config/"
static_dir = root_dir + "/static/"
content_dir = root_dir + "/content/"

# TODO : read a json file with user:password list
with open(config_dir + "users.json") as json_data:
    users = json.load(json_data)
# with open(config_dir + "chronos.json") as json_data:
#     chronos = json.load(json_data)

eventQueue = queue.Queue()

def updateChrono():
    eventQueue.put({
        'Minutes': sb.data["Minutes"], 'Seconds': sb.data["Seconds"]
    })


#from ScoreBoard import ScoreBoard
if cmdArgs.fake:
    LOG("Fake ScoreBoard")
    ScoreBoardFake = __import__("ScoreBoardFake")
    sb = ScoreBoardFake.ScoreBoardFake(onModifiedCallback = updateChrono)
else:
    ScoreBoardImpl = __import__("ScoreBoardImpl")
    sb = ScoreBoardImpl.ScoreBoardImpl(14, 15, onModifiedCallback = updateChrono)

def sendAll():
    eventQueue.put({
        'Minutes': sb.data["Minutes"], 'Seconds': sb.data["Seconds"],
        'BL': sb.data["BL"], 'FL': sb.data["FL"],
        'BV': sb.data["BV"], 'FV': sb.data["FV"],
        'Buzzer': sb.data["Buzzer"]
    })

@route('/')
def main_page():
    return bottle.static_file("main.html", root = content_dir)


@route('/poll')
def poll():
    LOG("polling ...")
    item = eventQueue.get()
    LOG("polling sent", item)
    return json.dumps(item)


@route('/static/<path:path>')
def static(path):
    LOG("static", path)
    # send it (method handles file check)
    return bottle.static_file(path, root = static_dir)    
 

@route('/<action>')
def action(action):
    LOG("action", action)
    if action == 'refresh':
        sendAll()
    elif action == 'pause':
        sb.stopChrono()
    elif action == 'play':
        sb.restartChrono()
    elif action == 'test':
        sb.test()
    elif action == 'blank':
        sb.blank()
    elif action == 'reset':
        sb.reset()
        sendAll()
    elif action == 'chronos':
        return bottle.static_file('chronos.json', root = config_dir)    
    else:
        bottle.redirect("/")


@route('/<action>/<value>')
def action(action, value):
    LOG("action", action, value)
    if action in ('Minutes', 'Seconds', 'BL', 'FL', 'BV', 'FV', 'Buzzer'):
        sb.set(**{action: value})
        eventQueue.put({action: value})
    elif action == "start":
        sb.startChrono(int(int(value) / 60), int(value) % 60)
    else:
        bottle.redirect("/")

@route('/<any:path>')
def default(any):
    # every other url -> redirect to main page
    bottle.redirect("/")


def main():
    bottle.run(host='0.0.0.0', port=cmdArgs.listenPort, server="gevent", debug=cmdArgs.verbose)

if __name__ == '__main__':
    main()
