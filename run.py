#! /home/f9pc001/miniconda2/bin/python

from mouse import Mouse
from keys import Keys
from time import sleep
from ConfigParser import ConfigParser
from json import loads
from commands import getstatusoutput
from subprocess import call
from os.path import expanduser
from datetime import datetime
import clipboard

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
        self.Config = self.load_config(config_file)

    @staticmethod
    def load_config(filename):
        p = ConfigParser()
        p.read(filename)
        return p

    def switch_ext_trigger(self):
        self.click(*loads(self.Config.get('KARTEL', 'external trigger')))

    def switch_write_tel(self):
        self.click(*loads(self.Config.get('KARTEL', 'write file')))

    def reset_counters(self):
        for i in xrange(3):
            self.press(*loads(self.Config.get('KARTEL', 'reset counters')))
            sleep(.2)
            self.release(*loads(self.Config.get('KARTEL', 'reset counters')))
            sleep(.1)

    def drs_trigger_stop(self):
        self.click(*loads(self.Config.get('DRS', 'trigger')))

    def drs_trigger_start(self):
        self.click(*loads(self.Config.get('DRS', 'trigger')))

    def drs_finish_run(self):
        self.click(*loads(self.Config.get('DRS', 'close/save')))

    def drs_save(self):
        self.click(*loads(self.Config.get('DRS', 'close/save')))
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
        self.click(*loads(self.Config.get('TERMINALS', 'neutral')))

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
        self.click(*loads(self.Config.get('TERMINALS', name)))
        sleep(.5)
        self.press_ctrl_and('c')
        sleep(.1)

    def stop_duts(self):
        self.stop_dut('fei4 3D')
        self.stop_dut('fei4 proto')
        self.stop_dut('cms')

    def start_dut(self, name):
        self.click(*loads(self.Config.get('TERMINALS', name)))
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

    def start_stop(self):
        self.goto_bottom_left_desktop()
        sleep(1)
        self.stop_drs()
        sleep(1)
        self.press_ctrl_alt_right()
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
        self.press_ctrl_alt_left()
        sleep(1)
        self.start_drs()

    def run(self):
        i = 0
        while True:
            if self.check_file() or i > 2 * 60 * 60:
                call([expanduser('~/Downloads/LjutelScripts/say.py')])
                self.start_stop()
                i = 0
            sleep(5)
            i += 5
            info('already waiting for {} '.format(datetime.fromtimestamp(i).strftime('%M:%S')), overlay=True)

    @staticmethod
    def check_file():
        try:
            return int(getstatusoutput('ssh data /home/testbeam/Downloads/get_n_events.py')[-1]) > 8783860  # ~ 200k events in FEI4 anchor module
        except Exception as err:
            print err
            return False


if __name__ == '__main__':
    z = Run()
    z.run()
