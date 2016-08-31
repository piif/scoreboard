#!/usr/bin/env python

from sys import argv
import argparse

from os.path import abspath, dirname
from time import time,sleep

from gevent import monkey, queue, getcurrent, GreenletExit; monkey.patch_all()
from bottle import route, request, response
import bottle # for static_file, redirect, run

import json, re
from __builtin__ import True
import subprocess

def LOG(*args):
    if cmdArgs.verbose:
        print ' '.join(str(a) for a in args) 

# parse command line arguments

parser = argparse.ArgumentParser()
parser.add_argument('--fake', dest = 'fake', action='store_const',
                    const = True, default = False, help = "fake mode")
parser.add_argument('--port', type = int, dest = 'listenPort',
                    default = 9090, help = "listen port")
parser.add_argument('--verbose', dest = 'verbose', action='store_const',
                    const = True, default = False, help = "log more")
# TODO : add config_dir, static_dir, content_dir
cmdArgs = parser.parse_args()

# set some "constants"
defaultBuzzDuration = 0.2

# set some directories
root_dir = abspath(dirname(argv[0]))
config_dir = dirname(root_dir) + "/config/"
static_dir = root_dir + "/static/"
content_dir = root_dir + "/content/"

if cmdArgs.fake:
    # in fake mode don't write password in /
    system_dir = dirname(root_dir) + "/system/etc/"
else:
    # in "real" mode write directly into /etc
    system_dir = "/etc/"


def shutdown():
    sb.blank()
    subprocess.call("/usr/sbin/halt -p", shell=True)
    exit(0)


def changePassword(old, new):
    r = re.compile(r'^wpa_passphrase=(.*)$', re.M)
    with open(system_dir + "hostapd/hostapd.conf", "r") as hostfile:
        content = hostfile.read()

    m = r.search(content)
    if m is None:
        return "password config not found"
    if old != m.group(1):
        return "old password doesn't match"
    
    content = r.sub("wpa_passphrase=" + new, content)
    with open(system_dir + "hostapd/hostapd.conf", "w") as hostfile:
        hostfile.write(content)
  
    return "Password changed"


# handle an event queue to maintain long polling on client until there's something to send
eventQueue = None

def enQueue(data):
    global eventQueue

    if eventQueue is not None:
        eventQueue.put(data)

def initQueue():
    global eventQueue

    # if queue exists, sending None into it will close pending request 
    enQueue(None)
    # now we can initialize a new one
    eventQueue = queue.Queue()


# scoreboard implementation will call this function every chrono tick
def updateChrono():
    enQueue({
        'Minutes': sb.data["Minutes"], 'Seconds': sb.data["Seconds"]
    })


# import ScoreBoard implementation depending of fake mode or not
if cmdArgs.fake:
    LOG("Fake ScoreBoard")
    ScoreBoardFake = __import__("ScoreBoardFake")
    sb = ScoreBoardFake.ScoreBoardFake(onModifiedCallback = updateChrono)
else:
    ScoreBoardImpl = __import__("ScoreBoardImpl2")
    sb = ScoreBoardImpl.ScoreBoardImpl(onModifiedCallback = updateChrono)

# current state of mute/unmute
buzzer = True

# current state of timeout chrono
timeoutRunning = False
# if timeout running, store main chrono value
savedChrono = None

def playpauseTimeout():
    global timeoutRunning, savedChrono

    if timeoutRunning:
        # stop it and restore main chrono
        sb.stopChrono()
        sb.set(Minutes = int(savedChrono / 60), Seconds = savedChrono % 60)
        timeoutRunning = False
    else:
        # save main chrono and set to timeout duration
        sb.stopChrono()
        savedChrono = sb.data['Minutes'] * 60 + sb.data['Seconds']
        sb.set(Minutes = 1, Seconds = 0)
        timeoutRunning = True

    enQueue({
        'Minutes': sb.data["Minutes"],
        'Seconds': sb.data["Seconds"],
        'timeout': timeoutRunning
    })


def currentState():
    return {
        'Minutes': sb.data["Minutes"], 'Seconds': sb.data["Seconds"],
        'BL': sb.data["BL"], 'FL': sb.data["FL"],
        'BV': sb.data["BV"], 'FV': sb.data["FV"],
        'buzzer': buzzer, 'timeout': timeoutRunning
    }

#
# beginning of routing functions
#

@route('/')
def main_page():
    return bottle.static_file("main.html", root = content_dir)


@route('/poll')
def poll():
    LOG("polling")
    initQueue()
    item = eventQueue.get()

    LOG("polling sent", item)
    return item


@route('/static/<path:path>')
def static(path):
    LOG("static", path)
    # send it (method handles file check)
    return bottle.static_file(path, root = static_dir)    
 

@route('/<action>')
def action(action):
    LOG("action", action)
    if action == 'refresh':
        enQueue(currentState())
    elif action == 'pause':
        sb.stopChrono()
    elif action == 'play':
        sb.restartChrono()
    elif action == 'test':
        sb.test()
    elif action == 'buzz':
        sb.buzz()
    elif action == 'blank':
        sb.blank()
    elif action == 'reset':
        sb.reset()
        enQueue(currentState())
    elif action == 'timeout':
        playpauseTimeout()
    elif action == 'shutdown':
        shutdown()
    elif action == 'upgrade':
        # TODO : http://bottlepy.org/docs/dev/tutorial.html#file-uploads
        print "Upgrade : TODO ..."
    elif action == 'chronos':
        return bottle.static_file('chronos.json', root = config_dir)    
    else:
        bottle.redirect("/")


@route('/<action>/<value>')
def action(action, value):
    LOG("action", action, value)

    if action in ('Minutes', 'Seconds', 'BL', 'FL', 'BV', 'FV'):
        sb.set(**{action: value})
        enQueue({action: value})
    elif action == "buzzer":
        if value == "on":
            buzzer = True
            sb.buzzDuration = defaultBuzzDuration
        else:
            buzzer = False
            sb.buzzDuration = 0
        enQueue({action: buzzer})
#     elif action == "start":
#         sb.startChrono(int(int(value) / 60), int(value) % 60)
    elif action == "setchrono":
        sb.set(Minutes = int(int(value) / 60), Seconds = int(value) % 60)
        enQueue({
            'Minutes': sb.data["Minutes"],
            'Seconds': sb.data["Seconds"],
        })
    elif action == 'password':
        print "Set password : TODO ..."
        (old, new) = value.split(':')
        result = changePassword(old, new)
        enQueue( { 'error' : result } )
    else:
        bottle.redirect("/")


@route('/<any:path>')
def default(any):
    # every other url -> redirect to main page
    bottle.redirect("/")


#
# end of routing functions
#

bottle.run(host='0.0.0.0', port=cmdArgs.listenPort, server="gevent",
           quiet=not cmdArgs.verbose, debug=cmdArgs.verbose)
