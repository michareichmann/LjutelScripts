#! /home/testbeam/miniconda2/bin/python

from glob import glob
from datetime import datetime, timedelta
from os.path import getctime, join
from ROOT import TFile
from argparse import ArgumentParser
from collections import OrderedDict
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep, time
from sys import stdout

p = ArgumentParser()
p.add_argument('start', nargs='?', default=0, type=int)
p.add_argument('-l', nargs='?', default='/home/testbeam/dev/pxar/data/Tel4/data')
args = p.parse_args()

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1t-MXNW0eN9tkGZSakfPdmnd_wcq4cX14Nw0bQ2ma_OQ').sheet1


def get_file_names():
    files = glob(join(args.l, 'ljutel*.root'))
    files = sorted([(int(f.strip('.root').split('_')[-1]), f) for f in files])[:-1]
    return OrderedDict(sorted([t for t in files if t[0] >= args.start]))


def get_file_info(files, nr):
    f = files[nr]
    a = TFile(f)
    return datetime.fromtimestamp(getctime(f)).strftime('%H:%M'), int(a.Get('Event').GetEntries())


col2num = lambda col: reduce(lambda x, y: x*26 + y, [ord(c.upper()) - ord('A') + 1 for c in col])


def get_sheet_info():
    cols = sheet.col_values(2)
    return len(cols), int(cols[-1])


def update_sheet():
    files = get_file_names()
    try:
        n_cols, run_nr = get_sheet_info()
        if run_nr in files:
            t, n = get_file_info(files, run_nr)
            sheet.update_cell(n_cols, col2num('AG'), t)
            sheet.update_cell(n_cols, col2num('AI'), 'green')
            sheet.update_cell(n_cols, col2num('AJ'), n)
            print 'updated for run {}, end time: {}, nr of events: {}'.format(run_nr, t, n)
    except Exception as err:
        print err


if __name__ == '__main__':
    start = time()
    while True:
        update_sheet()
        sleep(5)
        now = datetime.fromtimestamp(time() - start) - timedelta(hours=1)
        print '\rRunning for {}'.format(now.strftime('%H:%M:%S')),
        stdout.flush()
