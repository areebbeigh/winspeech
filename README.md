# winspeech
Speech recognition and synthesis library for Windows - Python 2 and 3.

This is a simple Python library based on the abandoned <a href="https://github.com/michaelgundlach/pyspeech">PySpeech library</a> for Python 2.

**PyPI:** https://pypi.python.org/pypi/winspeech<br>
**Doc:** https://pythonhosted.org/winspeech/

##Example

```
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

```

##Contributing
Feel free to fork the repo and any improvements/additions. I love pull requests.

##Additional Info
**Developer:** Areeb Beigh <areebbeigh@gmail.com><br>
**GitHub Repo:** https://github.com/areebbeigh/winspeech
