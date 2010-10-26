#!/usr/bin/python

import sys, re, os

START_HEADING = chr(1)
START_TEXT = chr(2)
END_TEXT = chr(3)

def process_article(title, text):
    fpath = os.path.join(wikidir, title)
    if os.path.exists(fpath):
        fc = open(fpath).read()
        fc = re.sub('^\n+', '', fc)
        fc = re.sub('\n+$', '', fc)
        text = fc
    sys.stdout.write(START_HEADING + '\n')
    sys.stdout.write(title + '\n')
    sys.stdout.write("%s\n" % len(text))
    sys.stdout.write(START_TEXT + '\n')
    sys.stdout.write(text + '\n')
    sys.stdout.write(END_TEXT + '\n')
    
buf = ''
mode = 'title'
wikidir = sys.argv[1]

while True:
    b = sys.stdin.read(1)
    if not b:
        break
    if b == START_HEADING:
        pass
    elif b == START_TEXT:
        buf = re.sub('^\n+', '', buf)
        title = buf.split('\n')[0]
        bytes = buf.split('\n')[1]
        buf = ''
    elif b == END_TEXT:
        buf = re.sub('^\n+', '', buf)
        buf = re.sub('\n+$', '', buf)
        process_article(title, buf)
        buf = ''
        title = ''
    else:
        buf += b

