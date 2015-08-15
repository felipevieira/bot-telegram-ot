import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '117251827:AAGOmVJJ42BTiu5gB4J28bMSP7SO2BJ-tXY'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

BOT_USERNAME = 'OFFThreadBot'

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        def hasCommand(text, command):
            text = text.split(' ')[0]
            if '@' in text and BOT_USERNAME != text.split('@')[1]:
                return False
            if command == text.split('@')[0]:
                return True
            return False

        if text.startswith('/'):
            if hasCommand(text, '/start'):
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif hasCommand(text, '/stop'):
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif hasCommand(text, '/image'):
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif hasCommand(text, '/ping'):
                reply('Pong!')

        elif 'who are you' in text:
            reply(BOT_USERNAME + ' criado pela OFFThread utilizando o telebot starter kit, created by yukuku: https://github.com/yukuku/telebot')
        elif 'what time' in text:
            reply('Olhe para o canto direito de cima da sua tela!')
        elif 'amaury medeiros' in text.lower():
            reply('Transao! #google') #Deu pau com o ascii quando escrevi transao com o til. Tem que ver aqui o que foi...
        elif 'arthur souza' in text.lower():
            reply('H2O2! #comendoaline')
        elif 'daniel gondim' in text.lower():
            reply('Infiel! #sextamaluca')
        elif 'danilo freitas' in text.lower():
            reply('Gosto de comida, maconha e amizades! #friendzone')
        elif 'diego maia' in text.lower():
            reply('Quem?! #desconhecido #intruso')
        elif 'felipe vieira' in text.lower():
            reply('Maconheiro! #sextamaluca')
        elif 'filipe costa' in text.lower():
            reply('Rei de auri! #sextamaluca')
        elif 'lenin medeiros' in text.lower():
            reply('Adora comida japonesa! #dominado #benino')
        elif 'matheus brasileiro' in text.lower():
            reply('! #comeuanne')
        elif 'paulo ouriques' in text.lower():
            reply('Husky Cibellyano! #sextamaluca #meusbeninos')
        elif 'silvio leoterio' in text.lower():
            reply('V1d4l0k4! #semanamaluca #minhafacisaminhavida')
        else:
            if getEnabled(chat_id):
                try:
                    resp1 = json.load(urllib2.urlopen('http://www.simsimi.com/requestChat?lc=en&ft=1.0&req=' + urllib.quote_plus(text.encode('utf-8'))))
                    back = resp1.get('res')
                except urllib2.HTTPError, err:
                    logging.error(err)
                    back = str(err)
                if not back:
                    reply('okay...')
                else:
                    reply(back)
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
