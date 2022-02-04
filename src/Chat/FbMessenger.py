from flask import Flask, request
from pymessenger.bot import Bot
from time import sleep

import PartTwo.Helpers.SPHelper as sph

app = Flask(__name__)
ACCESS_TOKEN = 'EAAKW2aZA6DXYBANXdMmzcBmf5BTL0pOIfpQAVrC15ZB3WfQjHPyZCr0wSgnbCTXsUueA9O1yFTP0tHUITRBw3WbfP3Nf7FsCXmuwLNdLrmAgpjZBXAKXPk3RkaKqtqNvJCqN6blDbE03Jdow4hBHvxgpcEZCAl5WSxZCUHoL4PVQpCa3x95ogY'  # this is the app access token for the chatbots facebook page
VERIFY_TOKEN = 'ThisIsTheVerifyToken'  # this is the verification token which can be anything and set when the callback url is defined on facebook
bot = Bot(ACCESS_TOKEN)  # creates instance of a bot

@app.route("/", methods=['GET', 'POST'])#We will receive messages that Facebook sends our bot here
def receive_message():
    '''
    Receive and process message from the user

    Return "Message Process" when its successful
    '''
    if request.method == 'GET':  # if the method is GET
        token_sent = request.args.get("hub.verify_token")  # get the token that facebook sent
        return verify_fb_token(token_sent)  # verify that the token was correct
    else:  # if the request was not get, it must be POST and we can just proceed
       output = request.get_json()  # get whatever message a user sent the bot
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                recipient_id = message['sender']['id'] #Facebook Messenger ID for user so we know where to send response back to
                if message['message'].get('text'):  # if the message was text
                    user_message = message['message'].get('text')  # get message from the user
                    sph.insert_into_conversation(user_message, recipient_id, True)  # log the message from the user in the DB
                else: #else user must have sent us a GIF, photo,video, or any other non-text item
                    sph.insert_into_conversation("", recipient_id, True)  # log in the database
                    response_sent_nontext = "Sorry I cannot understand messages that are not text"  # have a default response
                    send_message(recipient_id, response_sent_nontext)  # send the response for non text items
    return "Message Processed"

def verify_fb_token(token_sent):
    """
    Verify that it is facebook sending us the request

    :param token_sent:
    Token sent to app by Facebook

    :return:
    True if correct, False if not
    """
    if token_sent == VERIFY_TOKEN:  # if the topken facebook sent is the same as the one we have
        val = request.args.get("hub.challenge")  # get the code facebook sent us
        return val  # return the code
    return 'Invalid verification token'  # return invalid


def send_message(recipient_id, message):
    """
    Sends message to the user of

    :param recipient_id:
    ID of the user
    :param message:
    Message to send to the user

    :return:
    success if it worked
    """
    sph.insert_into_conversation(message, recipient_id, False)  # logs the bots message
    bot.send_text_message(recipient_id, message)  # sends the message using PyMessenger
    return "success"


def input_func(prompt):
    """
    Equivilent of pythons input function but for facebook messenger

    :param prompt:
    Message/question to send to the user

    :return:
    Response from the user
    """
    recipient_id = sph.get_last_user_id()  # get the recipient_id
    last_responce = sph.get_last_message(recipient_id)  # gets the last message from the user
    send_message(recipient_id, prompt)  # sends the prompt to the user
    new_last_response = last_responce  # set the responses equal
    while last_responce == new_last_response:  # while the last response is the same as the last time
        sleep(1)  # sleep 1 second
        new_last_response = sph.get_last_message(recipient_id)  # get the last message the user sent
    return new_last_response  # return the response to the prompt from the user


if __name__ == "__main__":
    app.run()