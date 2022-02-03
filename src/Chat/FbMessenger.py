import random
from flask import Flask, request
from pymessenger.bot import Bot
from time import sleep


import PartTwo.Helpers.SPHelper as sph

app = Flask(__name__)
ACCESS_TOKEN = 'EAAKW2aZA6DXYBANXdMmzcBmf5BTL0pOIfpQAVrC15ZB3WfQjHPyZCr0wSgnbCTXsUueA9O1yFTP0tHUITRBw3WbfP3Nf7FsCXmuwLNdLrmAgpjZBXAKXPk3RkaKqtqNvJCqN6blDbE03Jdow4hBHvxgpcEZCAl5WSxZCUHoL4PVQpCa3x95ogY'
VERIFY_TOKEN = 'ThisIsTheVerifyToken'
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
       output = request.get_json()  # get whatever message a user sent the bot
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                recipient_id = message['sender']['id'] #Facebook Messenger ID for user so we know where to send response back to
                if message['message'].get('text'):
                    user_message = message['message'].get('text')
                    sph.insertIntoConversation(user_message, recipient_id, True)
                #if user sends us a GIF, photo,video, or any other non-text item
                elif message['message'].get('attachments'):
                    sph.insertIntoConversation("", recipient_id, True)
                    response_sent_nontext = "Sorry I cannot understand messages that are not text"
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        val = request.args.get("hub.challenge")
        return val
    return 'Invalid verification token'


#uses PyMessenger to send response to user
def send_message(recipient_id, message):
    sph.insertIntoConversation(message, recipient_id, False)
    bot.send_text_message(recipient_id, message)
    return "success"


def input_func(prompt):
    recipient_id = sph.get_last_user_id()
    send_message(recipient_id, prompt)
    last_responce = sph.get_last_message(recipient_id)
    new_last_response = last_responce
    #wait here till next message recieved then return
    while last_responce == new_last_response:
        sleep(1)
        new_last_response = sph.get_last_message(recipient_id)
    return new_last_response


if __name__ == "__main__":
    app.run()