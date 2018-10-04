#! /home/testbeam/miniconda2/bin/python

from glob import glob
from datetime import datetime
from os.path import getctime
from ROOT import TFile
from argparse import ArgumentParser
from collections import OrderedDict

p = ArgumentParser()
p.add_argument('start', nargs='?', default=0, type=int)
args = p.parse_args()

files = glob('ljutel*.root')
files = sorted([(int(f.strip('.root').split('_')[-1]), f) for f in files])[:-1]
files = OrderedDict(sorted([t for t in files if t[0] >= args.start]))

print 'starting from', args.start
for n, f in files.iteritems():
    a = TFile(f)
    print '{}\t\t\t{}'.format(datetime.fromtimestamp(getctime(f)).strftime('%H:%M'), a.Get('Event').GetEntries())