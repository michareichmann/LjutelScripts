#!/usr/bin/env python
# --------------------------------------------------------
#       small script to call the ubuntu speech dispatcher
# created on September 29th 2018 by M. Reichmann (remichae@phys.ethz.ch)
# --------------------------------------------------------

from subprocess import call
from argparse import ArgumentParser
from gtts import gTTS
from os import devnull
from random import randint
from os.path import dirname, realpath, join

FNULL = open(devnull, 'w')


parser = ArgumentParser()
parser.add_argument('txt', nargs='?', default='')
parser.add_argument('-l', nargs='?', default='en')

args = parser.parse_args()

d = dirname(realpath(__file__))
f = open(join(d, 'haikus.txt'))
lines = [line.strip('\n,') for line in f.readlines() if line != '\n']
haikus = [', '.join(lines[i:i + 3]) for i in xrange(0, len(lines), 3)]

def say():
    txt = args.txt if args.txt else haikus[randint(0, len(haikus) - 1)]
    tts = gTTS(text=txt.decode('utf-8'), lang=args.l)
    tts.save('good.mp3')
    call(['mpg321', 'good.mp3'], stdout=FNULL)

say()
