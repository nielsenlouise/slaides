""" This is the framework part of our interactive slide project. It will take a
    string input from the speech-to-text, process it and make a slide object.
    Note: do not use more than one keyword input in a string.

    Commands:
    Commands:
            "today I am here to talk about": creates a new title slide
            "which brings us to": creates a new List slide
            "next slide is about": creates a new List slide
            "point": create a new list element
            "thing is": create a new list element
            "here's an image from wolfram alpha of": adds an image taken from
    the Wolfram Alpha API to the current slide
            "figure one": adds figure1.jpg from the local repository to the
    current slide
            "figure two":adds figure2.jpg from the local repository to the
    current slide
            "figure three":adds figure3.jpg from the local repository to the
    current slide
"""

import view
<<<<<<< HEAD
import string
from multiprocessing import Queue, Process
import sys
import requests
import urllib
import urllib2
import xml.etree.ElementTree as ET
import json
import pycurl
from io import BytesIO
import ast

with open('credentials.json') as credential_file:
    credentials = json.load(credential_file)['credentials']

slide_deck = view.SlideDeck(filename="slide_deck")


# functions for APIs and things
def get_wolframalpha_imagetag(searchterm):
    """ Used to get the first image tag from the Wolfram Alpha API. The return value is a dictionary
    with keys that can go directly into html.
    Takes in:
            searchterm: the term to search with in the Wolfram Alpha API
    """
    base_url = 'http://api.wolframalpha.com/v2/query?'
    app_id = credentials['wolframkey']  # api key
    url_params = {'input': searchterm, 'appid': app_id}
    headers = {'User-Agent': None}
    data = urllib.urlencode(url_params)
    req = urllib2.Request(base_url, data, headers)
    xml = urllib2.urlopen(req).read()
    tree = ET.fromstring(xml)
    for e in tree.findall('pod'):
        for item in [ef for ef in list(e) if ef.tag == 'subpod']:
            for it in [i for i in list(item) if i.tag == 'img']:
                if it.tag == 'img':
                    if float(it.attrib['width']) > 50 and float(it.attrib['height']) > 50:
                        return it.attrib['src']

def get_getty_imagetag(searchterm):
    """ Used to get an image fro the Getty Images API. The return value is an image uri."""
    buf = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, "https://api.gettyimages.com/v3/search/images?phrase=" + searchterm)
    c.setopt(c.HTTPHEADER, ['Api-Key:' + credentials['gettykey']])
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()

    dictionary = json.loads(buf.getvalue())
    return dictionary[u'images'][0][u'display_sizes'][0][u'uri']


# loop continues checking for new strings until user keystrokes
def main(strqueue, keyqueue):
    """ Is called as a process in controller.py. Continues checking for new
    strings until user escapes. When there is a string, it checks for a
    command.
    Takes in:
            strqueue:
            keyqueue:
    """
    global current
    if not strqueue.empty():
        text1 = strqueue.get()
        text = text1.lower()
        print text
        #       the following section is for creating a new slide
        if 'today i am here to talk about' in text:
            current = view.Slide_Title(title=text.split('today i am here to talk about')[1])
        elif 'today i am here to talk to you about' in text:
            current = view.Slide_Title(title=text.split('today i am here to talk to you about')[1])
        elif 'which brings us to' in text:
            current = view.Slide_List(title=text.split('which brings us to')[1])
        elif 'next slide is about' in text:
            current = view.Slide_List(title=text.split('next slide is about')[1])
        elif 'presented by' in text:
            current.add_subtitle(text='presented by' + text.split('presented by')[1])
        elif 'my name is' in text:
            current.add_subtitle(text='presented by' + text.split('my name is')[1])

    #   This section calls slide methods when certain phrases are found in the string
        elif 'point' in text:
            bullet = text.split('point', 1)[1]
            current.update_list([bullet])
        elif "thing is" in text:
            bullet = text.split('thing is', 1)[1]
            current.update_list([bullet])
        elif "first" in text:
            bullet = text.split('first', 1)[1]
            current.update_list([bullet])
        elif "here's an image from wolfram alpha of" in text:
            searchterm = text.split('heres an image from wolfram alpha of')[1]
            current.add_image_to_slide(source=get_wolframalpha_imagetag(searchterm))
        elif "here's an image of" in text:
            searchterm = text.split("here's an image of")[1]
            current.add_image_to_slide(source=get_getty_imagetag(searchterm))
        elif 'figure one' in text:
            current.add_image_to_slide(source='figure1.png')
        elif 'figure two' or 'figure to' or 'figure 2' in text:
            current.add_image_to_slide(source='figure2.jpeg')
        elif 'figure three' in text:
            current.add_image_to_slide(source='figure3.jpeg')

    # if the escape key is pressed, that will be sent to the keystroke queue
    # which will quit the program.
        if not keyqueue.empty():
            if keyqueue.get() == 'esc':
                slide_deck.end()
                sys.quit

if __name__ == '__main__':
    while True:
        main()
