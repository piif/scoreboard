from sys import argv
from os.path import abspath, dirname

from gevent import monkey, queue; monkey.patch_all()
from hashlib import md5
from time import time,sleep
from bottle import route, request, response
import bottle # for static_file, redirect, run
import json

from ScoreBoardFake import ScoreBoard

root_dir = abspath(dirname(argv[0]))
config_dir = dirname(root_dir) + "/config/"
static_dir = root_dir + "/static/"
content_dir = root_dir + "/content/"

# TODO : read a json file with user:password list
with open(config_dir + "users.json") as json_data:
    users = json.load(json_data)
with open(config_dir + "chronos.json") as json_data:
    chronos = json.load(json_data)

sb = ScoreBoard(14, 15)

def sendAll():
    eventQueue.put({
        'Minutes': sb.Minutes, 'Seconds': sb.Seconds,
        'BL': sb.BL, 'FL': sb.FL,
        'BV': sb.BV, 'FV': sb.FV,
        'Buzzer': sb.Buzzer
    })

class Session:
    id = None
    lastSeen = None
    data = {}

    def __init__(self):
        self.id = "ScoreBoardSession" + md5(str(time())).hexdigest()
        self.lastSeen = time()


sessions = {}

def getSession(request):
    id = request.cookies.get('session', None)
    if id is None:
        return None
    if sessions.has_key(id):
        return sessions[id]
    return None

def checkSession(request):
    if getSession(request) is None:
        throw("No valid sessions")

## TODO : thread to call this function every minute
def clearSessions():
    # TODO iterate on sessions and delete ones with lastSeen + ttl > now
    pass


@route('/scoreboard')
def main_page():
    # if valid cookie, redirect to main page
    # else redirect to login page 
    session = getSession(request)
    if session is None:
        bottle.redirect("/scoreboard/static/login.html")
    else:
        sendAll()
        return bottle.static_file("main.html", root = content_dir)


@route('/scoreboard/login', method='POST')
def do_login():
    login = request.forms.get('login')
    password = request.forms.get('password')
    if users.has_key(login) and users[login] == password:
        session = Session()
        sessions[session.id] = session
        response.set_cookie("session", session.id)
        bottle.redirect("/scoreboard")
    else:
        bottle.redirect("/scoreboard/static/login.html?login_wrong")


eventQueue = queue.Queue()

@route('/scoreboard/poll')
def poll():
    if getSession(request) is None: return bottle.abort(401, "Sorry, access denied.") 
    print "polling ..."
    item = eventQueue.get()
    print "polling sent", item
    return json.dumps(item)


@route('/scoreboard/static/<path:path>')
def static(path):
    print "static", path
    # send it (method handles file check
    return bottle.static_file(path, root = static_dir)    


@route('/scoreboard/<action>/<value>')
def action(action, value):
    if getSession(request) is None: return bottle.abort(401, "Sorry, access denied.")
    print "action", action, value
    if action in ('Minutes', 'Seconds', 'BL', 'FL', 'BV', 'FV', 'Buzzer'):
        sb.set(**{action: value})
        eventQueue.put({action: value})
    else:
        eventQueue.put({error: "Unknown action"})
 

@route('/scoreboard/<action>')
def action(action):
    if getSession(request) is None: return bottle.abort(401, "Sorry, access denied.")
    print "action", action
    if action == 'refresh':
        sendAll()
    elif action == 'test':
        sb.test()
    elif action == 'blank':
        sb.blank()
    elif action == 'chronos':
        bottle.static_file('chronos.json', root = config_dir)    
    else:
        eventQueue.put({error: "Unknown action"})


@route('/<any>')
def default(any):
    # every other url -> redirect to main page
    bottle.redirect("/scoreboard")


def main():
    bottle.run(port=9090, server="gevent", debug=True)

if __name__ == '__main__':
    main()
