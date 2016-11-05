# Say anything you type, and write anything you say.
# Stops when you say "turn off" or type "turn off".

import winspeech
import sys

# Start an in-process recognizer. Don't want the shared one with built-in windows commands.
winspeech.initialize_recognizer(winspeech.INPROC_RECOGNIZER)


def callback(phrase, listener):
    print(": %s" % phrase)
    if phrase == "turn off":
        winspeech.say("Goodbye.")
        listener.stop_listening()
        sys.exit()


print("Anything you type, speech will say back.")
print("Anything you say, speech will print out.")
print("Say or type 'turn off' to quit.")

listener = winspeech.listen_for_anything(callback)

while listener.is_listening():
    if sys.version_info.major == 3:
        text = input("> ")
    else:
        text = raw_input("> ")
    if text == "turn off":
        listener.stop_listening()
        sys.exit()
    else:
        winspeech.say(text)
