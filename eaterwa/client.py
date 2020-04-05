import requests
import json
import os
import shutil
import re
import urllib

def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].isLogin:
            return func(*args, **kwargs)
        else:
            print('You want to call the function, you must login to Whatsapp')
    return checkLogin

class EaterWa(object):

    isLogin = False

    def __init__(self, json_auth):

        self.host = 'https://wa.boteater.us/api'
        self._session = requests.session()

        if isinstance(json_auth, dict):
            self.headers = json_auth
        else:
            raise Exception('Invalid Authentication !!!')

    def login(self):
        self.getClient()
        qr = self.getQr().json()
        try:
            print('Scan this QR : ', qr['result']['qr-callback'])
        except:
            print('Trying to login...')

        callback = self.getContent(qr['result']['callback'])

        if callback.json()['result'] == 'LoggedIn':
            self.isLogin = True
            print('Login success :', self.getMe().json()['id']['_serialized'])
            return True
        else:
            self.isLogin = False
            print(callback.json()['result'])
            return False

    def urlEncode(self, url, path, params=[]):
        return url + path + '?' + urllib.parse.urlencode(params)

    def getContent(self, url, headers=None):
        if headers is None:
            headers = self.headers
        return self._session.get(url, headers=headers, stream=True)

    def postContent(self, url, data=None, files=None, headers=None):
        if headers is None:
            headers = self.headers
        return self._session.post(url, headers=headers, data=data, files=files)

    def downloadFileWithURL(self, url, filename):
        files = open(filename, 'wb')
        resp  = requests.get(url, stream=True)
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, files)
        return filename

    def getClient(self):
        url = self.host + '/client'
        a = self.getContent(url)
        return a

    def getQr(self):
        url = self.host + '/login'
        a = self.getContent(url)
        return a

    @loggedIn
    def getMe(self):
        url = self.host + '/getMe'
        a = self.getContent(url)
        return a

    @loggedIn
    def getUnread(self, me=True, notif=True):
        data = {
            'include_me': me,
            'include_notifications': notif
        }
        req = self.postContent(self.host + '/unread', data=data)
        return req

    @loggedIn
    def sendMessage(self, to, text):
        url = self.host + '/sendMessage'
        data = {
            'chat_id': to,
            'message': text
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def sendMessageV2(self, to, text, metadata={}):
        url = self.host + '/sendMessageV2'
        data = {
            'chat_id': to,
            'message': text,
            'metadata': str(metadata)
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def sendMention(self, to, text, userids=[]):
        url = self.host + '/sendMention'
        data = {
            'chat_id': to,
            'message': text,
            'user_ids': userids
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def sendMedia(self, to, path, caption='', metadata={}, mentionedJidList=[]):
        url = self.host + '/sendMedia'

        msgMetaData = {}
        if metadata:
            msgMetaData.update(metadata)
        if mentionedJidList:
            msgMetaData.update({'mentionedJidList': mentionedJidList})
        data = {
            'chat_id': to,
            'caption': caption,
            'metadata': str(metadata)
        }
        files ={'files': open(path,'rb')}
        req = self.postContent(url, data=data, files=files)
        return req

    @loggedIn
    def sendMediaWithURL(self, to, url, filename, caption='', metadata={}):
        path = self.downloadFileWithURL(url, filename)
        r = self.sendMedia(to, path, caption, metadata)
        os.remove(path)
        return r

    @loggedIn
    def sendSeen(self, to):
        url = self.host + '/sendSeen'
        data = {
            'chat_id': to
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def sendReply(self, message_id, text):
        url = self.host + '/sendReply'
        data = {
            'message_id': message_id,
            'message': text
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def getBatteryLevel(self):
        url = self.host + '/getBatteryLevel'
        req = self.getContent(url)
        return req

    @loggedIn
    def getGroupParticipantsIds(self, to):
        url = self.host + '/getGroupParticipantsIds'
        data = {
            'group_id': to
        }
        req = self.postContent(url, data=data)
        return req

    @loggedIn
    def revoke(self):
        url = self.host + '/revoke'
        req = self.getContent(url)
        return req

    @loggedIn
    def mentionAll(self, message):
        to = message['chatId']
        if message['chat']['isGroup']:
            result = '╭───「 Mention Members 」\n'
            no = 0
            members = self.getGroupParticipantsIds(message['chatId']).json()['result']
            if myId in members:
                members.remove(myId)
            for member in members:
                no += 1
                result += '│ %i. @%s\n' % (no, member.replace('@c.us',''))
            result += '╰───「 Hello World 」\n'
            self.sendMention(to, result, members)
        else:
            self.sendMessage(to, 'Group only!')
