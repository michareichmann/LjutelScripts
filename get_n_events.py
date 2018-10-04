#! /home/testbeam/miniconda2/bin/python

from argparse import ArgumentParser
from glob import glob
from os.path import join, getsize, basename

p = ArgumentParser()
p.add_argument('dir', nargs='?', default='/home/testbeam/testbeam-sep-2018/proto9/proto9')
p.add_argument('filename', nargs='?', default='trigger_scan.h5')
args = p.parse_args()


files = glob(join(args.dir, '*{}*'.format(args.filename)))
try:
    last_file = sorted(files, key=lambda x: int(basename(x).split('_')[0]))[-1]
except ValueError:
    last_file = max(files)

print getsize(last_file)

