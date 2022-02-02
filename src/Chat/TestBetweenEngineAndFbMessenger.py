import random

import Engine as e


def get_message(user_message):  # this function needs to return the message from the engine given a user message
    sample_responses = ["Dan", "Charlie", "Brandon"]
    return sample_responses[random.randint(0, 2)]


if __name__ == "__main__":
    user_message = input("This is just to get the users first message ")  # this is so that the user messages first and ideally this will just be a "hello"
    while True:
        bot_message = get_message(user_message)
        user_message = input(bot_message)