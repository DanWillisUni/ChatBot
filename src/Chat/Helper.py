import appSettings

import Chat.FbMessenger as fbm
import PartTwo.Helpers.SPHelper as sph

def helper_print(message):
    if appSettings.get_API() == "fb":
        user_id = sph.get_last_user_id()
        fbm.send_message(user_id,message)
    #elif appSettings.get_API() == "api":

    elif appSettings.get_API() == "console":
        print(message)

def helper_input(prompt):
    if appSettings.get_API() == "fb":
        return fbm.input_func(prompt)
    #elif appSettings.get_API() == "api":

    elif appSettings.get_API() == "console":
        return input(prompt)

