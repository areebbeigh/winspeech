"""
Speech recognition and synthesis library for Windows - Python 2 and 3.
Based on the abandoned Python 2 library https://github.com/michaelgundlach/pyspeech.

This module adds contains a few more features, the important one being the ability to create
in-process speech recognizers.

Author: Areeb Beigh <areebbeigh@gmail.com>
GitHub: https://github.com/areebbeigh/winspeech

License:
    Copyright 2016 Areeb Beigh

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from win32com.client import constants as _constants
import win32com.client
import pythoncom
import time
import sys

if sys.version_info.major == 3:
    import _thread
else:
    # Python 2
    import thread as _thread

# Make sure that we've got our COM wrappers generated.
from win32com.client import gencache

__author__ = "Areeb Beigh [areebbeigh@gmail.com]"

INPROC_RECOGNIZER = "SAPI.SpInprocRecognizer"
SHARED_RECOGNIZER = "SAPI.SpSharedRecognizer"

gencache.EnsureModule('{C866CA3A-32F7-11D2-9602-00C04F8EE628}', 0, 5, 0)

_voice = win32com.client.Dispatch("SAPI.SpVoice")
_recognizer = win32com.client.Dispatch("SAPI.SpInProcRecognizer")
_recognizer.AudioInputStream = win32com.client.Dispatch("SAPI.SpMMAudioIn")
_ListenerBase = win32com.client.getevents("SAPI.SpInProcRecoContext")
_listeners = []
_handlerqueue = []
_event_thread = None


def initialize_recognizer(recognizer):
    """
    Initializes the speech recognizer

    Parameters:
         recognizer: The type of recognizer to initialize_recognizer. winspeech.INPROC_RECOGNIZER for in process
         and winspeech.SHARED_RECOGNIZER for shared recognizer.
    """
    global _recognizer, _ListenerBase

    if recognizer == INPROC_RECOGNIZER:
        _recognizer = win32com.client.Dispatch("SAPI.SpInProcRecognizer")
        _recognizer.AudioInputStream = win32com.client.Dispatch("SAPI.SpMMAudioIn")
        _ListenerBase = win32com.client.getevents("SAPI.SpInProcRecoContext")
        return

    if recognizer == SHARED_RECOGNIZER:
        _recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
        _ListenerBase = win32com.client.getevents("SAPI.SpSharedRecoContext")
        return

    raise ValueError(recognizer + " is not a valid recognizer")


class Listener(object):
    """ Listens for speech and calls a callback on a separate thread. """

    _all = set()

    def __init__(self, context, grammar, callback):
        """
        This should never be called directly; use speech.listen_for()
        and speech.listen_for_anything() to create Listener objects.
        """
        self._grammar = grammar
        Listener._all.add(self)

        # Tell event thread to create an event handler to call our callback
        # upon hearing speech events
        _handlerqueue.append((context, self, callback))
        _ensure_event_thread()

    def is_listening(self):
        """ True if this Listener is listening for speech. """
        return self in Listener._all

    def stop_listening(self):
        """ Stop listening for speech.  Returns True if we were listening. """

        try:
            Listener._all.remove(self)
        except KeyError:
            return False

        # This removes all refs to _grammar so the event handler can die
        self._grammar = None

        if not Listener._all:
            global _event_thread
            _event_thread = None  # Stop the eventthread if it exists

        return True


class _ListenerCallback(_ListenerBase):
    """
    Created to fire events upon speech recognition.  Instances of this
    class automatically die when their listener loses a reference to
    its grammar.  TODO: we may need to call self.close() to release the
    COM object, and we should probably make goaway() a method of self
    instead of letting people do it for us.
    """

    def __init__(self, oobj, listener, callback):
        _ListenerBase.__init__(self, oobj)
        self._listener = listener
        self._callback = callback

    def OnRecognition(self, _1, _2, _3, Result):
        # When our listener stops listening, it's supposed to kill this
        # object.  But COM can be funky, and we may have to call close()
        # before the object will die.
        if self._listener and not self._listener.is_listening():
            self.close()
            self._listener = None

        if self._callback and self._listener:
            new_result = win32com.client.Dispatch(Result)
            phrase = new_result.PhraseInfo.GetText()
            self._callback(phrase, self._listener)


def say(phrase):
    """ Say the given phrase out loud. This will run on a separate thread. """
    _voice.Speak(phrase, 1)


def say_wait(phrase):
    """ Say the given phrase out load. This will run on the current thread. """
    _voice.Speak(phrase)


def stop_talking():
    """ Stop the current utterance. """
    _voice.Speak("", 3)


"""
def input(prompt=None, phrase_list=None):
    '''
    Print the prompt if it is not None, then listen for a string in phrase_list
    (or anything, if phrase_list is None.)  Returns the string response that is
    heard.  Note that this will block the thread until a response is heard or
    Ctrl-C is pressed.
    '''

    def response(phrase, listener):
        if not hasattr(listener, '_phrase'):
            listener._phrase = phrase  # so outside caller can find it
        listener.stop_listening()

    if prompt:
        print(prompt)

    if phrase_list:
        listener = listen_for(phrase_list, response)
    else:
        listener = listen_for_anything(response)

    while listener.is_listening():
        time.sleep(.1)

    return listener._phrase  # hacky way to pass back a response...
"""


def stop_listening():
    """
    Cause all Listeners to stop listening.  Returns True if at least one
    Listener was listening.
    """
    listeners = set(Listener._all)  # clone so stop_listening can pop()
    returns = [l.stop_listening() for l in listeners]
    return any(returns)  # was at least one listening?


def is_listening():
    """True if any Listeners are listening."""
    return not not Listener._all


def listen_for_anything(callback):
    """
    When anything resembling English is heard, callback(spoken_text, listener)
    is executed.  Returns a Listener object.

    The first argument to callback will be the string of text heard.
    The second argument will be the same listener object returned by
    listen_for_anything().

    Execution takes place on a single thread shared by all listener callbacks.
    """
    return _start_listening(None, callback)


def listen_for(phrase_list, callback):
    """
    If any of the phrases in the given list are heard,
    callback(spoken_text, listener) is executed.  Returns a Listener object.

    The first argument to callback will be the string of text heard.
    The second argument will be the same listener object returned by
    listen_for().

    Execution takes place on a single thread shared by all listener callbacks.
    """
    return _start_listening(phrase_list, callback)


def _start_listening(phrase_list, callback):
    """
    Starts listening in Command-and-Control mode if phrase_list is
    not None, or dictation mode if phrase_list is None.  When a phrase is
    heard, callback(phrase_text, listener) is executed.  Returns a
    Listener object.

    The first argument to callback will be the string of text heard.
    The second argument will be the same listener object returned by
    listen_for().

    Execution takes place on a single thread shared by all listener callbacks.
    """
    # Make a command-and-control grammar        
    context = _recognizer.CreateRecoContext()
    grammar = context.CreateGrammar()

    if phrase_list:
        grammar.DictationSetState(0)
        # dunno why we pass the constants that we do here
        rule = grammar.Rules.Add("rule",
                                 _constants.SRATopLevel + _constants.SRADynamic, 0)
        rule.Clear()

        for phrase in phrase_list:
            rule.InitialState.AddWordTransition(None, phrase)

        # not sure if this is needed - was here before but dupe is below
        grammar.Rules.Commit()

        # Commit the changes to the grammar
        grammar.CmdSetRuleState("rule", 1)  # active
        grammar.Rules.Commit()
    else:
        grammar.DictationSetState(1)

    return Listener(context, grammar, callback)


def _ensure_event_thread():
    """
    Make sure the event thread is running, which checks the handlerqueue
    for new event handlers to create, and runs the message pump.
    """
    global _event_thread
    if not _event_thread:
        def loop():
            while _event_thread:
                pythoncom.PumpWaitingMessages()
                if _handlerqueue:
                    (context, listener, callback) = _handlerqueue.pop()
                    # Just creating a _ListenerCallback object makes events
                    # fire till listener loses reference to its grammar object
                    _ListenerCallback(context, listener, callback)
                time.sleep(.5)

        _event_thread = 1  # so loop doesn't terminate immediately
        _event_thread = _thread.start_new_thread(loop, ())
