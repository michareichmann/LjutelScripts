#! /home/f9pc001/miniconda2/bin/python

from mouse import Mouse
from keys import Keys
from time import sleep
from ConfigParser import ConfigParser
from json import loads
from commands import getstatusoutput
from subprocess import call
from os.path import expanduser, join
from datetime import datetime
import clipboard
from argparse import ArgumentParser
from re import split

GREEN = '\033[92m'
ENDC = '\033[0m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'


def get_t_str():
    return datetime.now().strftime('%H:%M:%S')


def info(msg, overlay=False, prnt=True):
    if prnt:
        print '{ov}{head} {t} --> {msg}'.format(t=get_t_str(), msg=msg, head='{}INFO:{}'.format(GREEN, ENDC), ov='\033[1A\r' if overlay else '')


class Run(Mouse, Keys):

    def __init__(self, config_file='config.ini'):
        Keys.__init__(self)
        Mouse.__init__(self)
        self.ConfigFileName = config_file

    def get_from_config(self, section, option):
        p = ConfigParser()
        p.read(self.ConfigFileName)
        return p.get(section, option)

    def idle_mouse(self):
        x, y = self.get_mouse_position()
        self.move_to(x + (1 if x < 500 else -1), y)

    def switch_ext_trigger(self):
        self.click(*loads(self.get_from_config('KARTEL', 'external trigger')))

    def switch_write_tel(self):
        self.click(*loads(self.get_from_config('KARTEL', 'write file')))

    def reset_counters(self):
        for i in xrange(3):
            self.press(*loads(self.get_from_config('KARTEL', 'reset counters')))
            sleep(.2)
            self.release(*loads(self.get_from_config('KARTEL', 'reset counters')))
            sleep(.1)

    def drs_trigger_stop(self):
        self.click(*loads(self.get_from_config('DRS', 'trigger')))

    def drs_trigger_start(self):
        self.click(*loads(self.get_from_config('DRS', 'trigger')))

    def drs_finish_run(self):
        self.click(*loads(self.get_from_config('DRS', 'close/save')))

    def drs_save_old(self):
        self.click(*loads(self.get_from_config('DRS', 'close/save')))
        sleep(.5)
        self.press_tab()
        sleep(.2)
        self.press_down(2)
        sleep(.2)
        self.press_enter()
        sleep(.2)
        self.press_shift_tab(3)
        sleep(.2)
        self.press_end_key()
        sleep(.2)
        self.press_home_key()
        sleep(.2)
        self.press_tab(2)
        sleep(.2)
        self.press_ctrl_and('c')
        sleep(.2)
        run_nr = int(clipboard.paste().strip('run.dat')) + 1
        run_nr = 'run{}.dat'.format(run_nr)
        sleep(.1)
        self.type(run_nr)
        sleep(.1)
        self.press_enter()
        sleep(.5)
        self.press_ctrl_and('a')
        sleep(.1)
        self.type('1000000')
        sleep(.1)
        self.press_enter()

    def drs_save(self):
        self.click(*loads(self.get_from_config('DRS', 'close/save')))
        sleep(.5)
        old_run_nr = self.get_last_drs_run_number()
        self.type(join(self.get_from_config('DRS', 'save directory'), 'run{}.dat'.format(old_run_nr + 1)))
        sleep(.2)
        self.press_enter()
        sleep(.5)
        self.press_ctrl_and('a')
        sleep(.1)
        self.type('1000000')
        sleep(.1)
        self.press_enter()

    def start_drs(self):
        self.drs_save()
        sleep(.5)
        self.drs_trigger_start()
        sleep(.1)
        self.goto_neutral()

    def stop_drs(self):
        self.drs_trigger_stop()
        sleep(.5)
        self.drs_finish_run()
        sleep(.1)
        self.goto_neutral()
        sleep(.5)

    def goto_neutral(self):
        self.click(*loads(self.get_from_config('TERMINALS', 'neutral')))

    def stop_telescope(self):
        self.switch_ext_trigger()
        sleep(.2)
        self.switch_write_tel()
        self.reset_counters()
        sleep(.2)
        self.goto_neutral()

    def start_telescope(self):
        self.switch_write_tel()
        sleep(1)
        self.switch_ext_trigger()
        sleep(.2)
        self.goto_neutral()

    def stop_dut(self, name):
        self.click(*loads(self.get_from_config('TERMINALS', name)))
        sleep(.5)
        self.press_ctrl_and('c')
        sleep(.1)

    def stop_duts(self):
        self.stop_dut('fei4 3D')
        self.stop_dut('fei4 proto')
        self.stop_dut('cms')

    def start_dut(self, name):
        self.click(*loads(self.get_from_config('TERMINALS', name)))
        sleep(.5)
        self.press_up()
        sleep(.2)
        self.press_enter()
        sleep(.1)

    def start_duts(self):
        self.start_dut('cms')
        self.start_dut('fei4 3D')
        self.start_dut('fei4 proto')

    def goto_bottom_left_desktop(self):
        self.press_ctrl_alt_down()
        sleep(.1)
        self.press_ctrl_alt_left()
        sleep(.1)

    def goto_bottom_right_desktop(self):
        self.press_ctrl_alt_down()
        sleep(.1)
        self.press_ctrl_alt_right()
        sleep(.1)

    def start_stop(self, with_drs=False):
        if with_drs:
            self.goto_bottom_left_desktop()
            sleep(1)
            self.stop_drs()
            sleep(1)
        self.goto_bottom_right_desktop()
        sleep(1)
        self.stop_telescope()
        sleep(.5)
        self.press_ctrl_alt_up()
        sleep(1)
        self.stop_duts()
        sleep(10)
        self.start_duts()
        sleep(5)
        self.press_ctrl_alt_down()
        sleep(1)
        self.start_telescope()
        sleep(1)
        if with_drs:
            self.press_ctrl_alt_left()
            sleep(1)
            self.start_drs()

    def run(self, with_drs):
        i, j = 0, 0
        t_wait = 5
        while True:
            if self.check_file() or i > 2 * 60 * 60:
                call([expanduser('~/Downloads/LjutelScripts/say.py')])
                self.start_stop(with_drs)
                i = 0
            if j > 60 * 5:
                self.idle_mouse()
                j = 0
            sleep(t_wait)
            i += t_wait
            j += t_wait
            info('already waiting for {} '.format(datetime.fromtimestamp(i).strftime('%M:%S')), overlay=True)

    def check_file(self):
        try:
            size_limit = int(self.get_from_config('KARTEL', 'file size'))
            return int(getstatusoutput('ssh data /home/testbeam/Downloads/get_n_events.py')[-1]) > size_limit  # ~ 200k events in FEI4 anchor module
        except Exception as err:
            print err
            return False

    def get_last_drs_run_number(self):
        status = getstatusoutput('ssh -tY data ls {}'.format(self.get_from_config('DRS', 'save directory')))[-1]
        run = max(split('[ \t]', status.split('\n')[0].strip('\r')))
        return int(run.strip('run.dat'))


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--test', '-t', action='store_true')
    parser.add_argument('-drs', action='store_true')
    args = parser.parse_args()

    z = Run()
    if not args.test:
        z.run(args.drs)
