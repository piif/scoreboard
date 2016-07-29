from sys import argv
from os.path import abspath, dirname

from gevent import monkey, queue; monkey.patch_all()
from hashlib import md5
from time import time
from bottle import route, request, response
import bottle # for static_file, redirect, run
import json

root_dir = abspath(dirname(argv[0]))
static_dir = root_dir + "/static/"
content_dir = root_dir + "/content/"

# TODO : read a json file with user:password list
users = {
    'rsc' : 'wasquehal',
    'pif' : 'paf'
}

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
    if getSession(request) is None: bottle.abort(401, "Sorry, access denied.") 
    # how to send data from other functions ?
    while True:
        print "polling ..."
        item = eventQueue.get()
        print "polling sent", item
        yield json.dumps(item)


@route('/scoreboard/static/<path:path>')
def static(path):
    print "static", path
    # send it (method handles file check
    return bottle.static_file(path, root = static_dir)    


@route('/scoreboard/<action>/<value>')
def action(action, value):
    if getSession(request) is None: return bottle.abort(401, "Sorry, access denied.")
    print "action", action, value
    # todo : handle action
    # todo : if fail, enqueue error message
    eventQueue.put({action: value})


@route('/<any>')
def default(any):
    # every other url -> redirect to main page
    bottle.redirect("/scoreboard")


def main():
    bottle.run(port=9090, server="gevent", debug=True)

if __name__ == '__main__':
    main()
