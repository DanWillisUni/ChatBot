import random

import Engine as e

def get_message(user_message):
    sample_responses = ["Dan", "Charlie", "Brandon"]
    return sample_responses[random.randint(0, 2)]

if __name__ == "__main__":
    user_message = input("This is just to get the users first message ")
    while True:
        bot_message = get_message(user_message)
        user_message = input(bot_message)