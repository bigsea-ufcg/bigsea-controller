# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from datetime import datetime
import time
import texttable

global_enabled = False


class Log:
    def __init__(self, name, output_file_path):
        self.logger = logging.getLogger(name)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            handler = logging.FileHandler(output_file_path)
            self.logger.addHandler(handler)

    def log(self, text):
        if global_enabled:
            self.logger.info(text)


class ScalingLog:
    def __init__(self, name, output_file_path, application_id):
        self.application_id = application_id
        self.logger = Log(name, output_file_path)

    def log(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        log_string = "%s | %s: %s" % (time.strftime("%H:%M:%S"), self.application_id, text)
        self.logger.log(log_string)

    def log_table(self, app_id, job_progress, time_progress, current_cap, previous_cap, action):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        line = timestamp, app_id, job_progress, time_progress, previous_cap, current_cap, action
        self.logger.log(line)


class TableLog:
    def __init__(self, name, output_file_path):
        self.logger = Log(name, output_file_path)
        self.table = texttable.Texttable()
        self.table.set_cols_align(["c", "c", "c", "c", 'c', 'c', 'c'])
        self.table.set_cols_width([8, 24, 15, 14, 9, 15, 26])
        
    def log(self, app_id, controller_name, actuator_name, current_cap, previous_cap, progress_error, action):
#       line = "%s %s %s %s %s %s %s" % (timestamp, app_id, job_progress, time_progress, previous_cap, current_cap, action)
        timestamp = time.strftime("%H:%M:%S")

        if previous_cap != '--':
            previous_cap_formatted = str(previous_cap) + "%"
        else:
            previous_cap_formatted = previous_cap

        if current_cap != '--':
            current_cap_formatted = str(current_cap) + "%"
        else:
            current_cap_formatted = current_cap

        if progress_error != '--':
            progress_error_formatted = str(float("{0:.1}".format(float(progress_error)))) + "%"
        else:
            progress_error_formatted = progress_error

        line = [timestamp, app_id, controller_name, actuator_name, current_cap_formatted, progress_error_formatted, action]
        self.table.add_row(line)
        last_line = self.table.draw().split('\n')[-2]
        self.logger.log(last_line)

    def header_log(self):
        header_row = [["Time", "Application ID", "Controller", "Actuator", "CPU Cap", "Progress Error", "Action"]]
        self.table.add_rows(header_row)
        last_line = self.table.draw().split('\n')[:3]
        self.logger.log(last_line[0])
        self.logger.log(last_line[1])
        self.logger.log(last_line[2])


def enable():
    global global_enabled
    global_enabled = True


def disable():
    global global_enabled
    global_enabled = False


def configure_logging(logging_level="INFO"):
    levels = {"CRITICAL": logging.CRITICAL, "DEBUG": logging.DEBUG, "ERROR": logging.ERROR,
              "FATAL": logging.FATAL, "INFO": logging.INFO, "NOTSET": logging.NOTSET,
              "WARN": logging.WARN, "WARNING": logging.WARNING
              }

    logging.basicConfig(level=levels[logging_level])
