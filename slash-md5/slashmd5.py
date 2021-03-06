#!/usr/bin/env python
import bottle   # pip install bottle
import requests
import socket
import json
from datetime import datetime, timedelta
import hashlib
import config

app = application = bottle.Bottle()
lastaction = datetime.now() - timedelta(hours=1)


@app.route('/', method='POST')
def slack_post():
    body = bottle.request.body.read()

    token = bottle.request.forms.get('token')
    team_id = bottle.request.forms.get('team_id')
    team_domain = bottle.request.forms.get('team_domain')
    service_id = bottle.request.forms.get('service_id')
    channel_id = bottle.request.forms.get('channel_id')
    channel_name = bottle.request.forms.get('channel_name')
    timestamp = bottle.request.forms.get('timestamp')
    user_id = bottle.request.forms.get('user_id')
    user_name = bottle.request.forms.get('user_name')
    text = bottle.request.forms.get('text')
    trigger_words = bottle.request.forms.get('trigger_words')

    if token != config.slack_token:  # integration token
        print "INVALID REQUEST RECEIVED! --> %s" % body
        return "LOL NOPE"

    thisaction = datetime.now()
    if (thisaction - lastaction) > timedelta(seconds=config.cooldown_sec):
        pass
    else:
        return "%s cooling down! Please wait..." % botname

    global lastaction
    lastaction = datetime.now()
    parseArguments(text, user_name, channel_name)


def parseArguments(args, user_name, channel_name):
        #args = "encrypt password"
    argList = args.split()
    numargs = len(argList)
    if numargs != 2:
        message = "Wrong number of arguments! Need 2, you sent %s" % numargs
        sendToUser(message, user_name)
    func = argList[0]

    if func == "encrypt":
        plaintext = argList[1]
        encrypt(plaintext, user_name, channel_name)
    elif func == "decrypt":
        dehash = argList[1]
        if len(dehash) != 32:
            message = "Not a valid 32 digit hash: %s" % dehash
            sendToUser(message, user_name)
            return "Not valid hash"
        decrypt(dehash, user_name, channel_name)
    else:
        message = "Command not valid: %s" % argList[0] + "\n"
        message = message + "Please use `encrypt <string>` or `decrypt <hash>`."
        sendToUser(message, user_name)


def encrypt(plaintext, user_name, channel_name):
    md5 = hashlib.md5()
    md5.update(plaintext)
    ciphertext = md5.hexdigest()
    message = "MD5 Hash generated by %s" % user_name + "\n"
    message = message + "String:\t`%s`" % plaintext + "\n"
    message = message + "Hash:\t`%s`" % ciphertext + "\n"
    sendToSlack(message, channel_name)


def decrypt(dehash, user_name, channel_name):
    url = "http://md5.gromweb.com/query/"
    url = url + dehash
    r = requests.get(url)
    plaintext = r.text
    if plaintext:
        message = "MD5 Decrypted by %s" % user_name + "\n"
        message = message + "Hash:\t`%s`" % dehash + "\n"
        message = message + "Plaintext:\t`%s`" % plaintext + "\n"
        sendToSlack(message, channel_name)
    else:
        message = "Sorry, %s, MD5 `%s` Unable to be decrypted!" % (
            user_name, dehash)
        sendToSlack(message, channel_name)


def sendToSlack(message, channel_name):
    slackChan = "#" + channel_name
    url = config.slack_url
    data = {"username": botname, "channel": slackChan, "text": message}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.status_code
    print r.content
    print "\n"


def sendToUser(message, user_name):
    slackChan = "@" + user_name
    url = config.slack_url
    data = {"username": botname, "channel": slackChan, "text": message}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print r.status_code
    print r.content
    print "\n"

if __name__ == '__main__':
    bottle.run(app, host='0.0.0.0', port=config.listen_port)
