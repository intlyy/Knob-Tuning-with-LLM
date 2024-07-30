# -*- coding: utf-8 -*-

import configparser
import json


class myParser(configparser.ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d


def parse_args():
    parser = myParser()
    parser.read("config.ini", encoding="utf-8")
    return parser.as_dict()


def get_ssh_config():
    return parse_args()['ssh']


def get_predictor_config():
    return parse_args()['predictor']


def get_database_config():
    return parse_args()['database_tune']


def get_knob_config():
    knobs = []
    with open('knob_19.json', 'r') as f:
        d = json.load(f)
        for i in d:
            knobs.append(i)
    return knobs


global w


def set_workload(i):
    global w
    w = 'workload/workload_test_{}.txt'.format(i)


def get_workload():
    # file_path = get_database_config()['workload_file_path']
    file_path = w
    workload = []
    try:
        with open(file_path, 'r') as f:
            result = f.read().splitlines()
            for i in result:
                if i:
                    workload.append(i)
            f.close()
    except Exception as error:
        print(str(error))
    return workload


def fun():
    knobs = get_knob_config()
    for index, knob in enumerate(knobs):
        s = ""
        s = s + str(index + 1) + ". "
        s = s + knob['name'] + ". " + str(knob['short_desc']) + " " + str(knob['max_val']) + ", " + str(
            knob['min_val']) + ', ' + str(knob['boot_val'])
        print(s)

# fun()
