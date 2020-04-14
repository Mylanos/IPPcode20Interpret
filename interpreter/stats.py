# -*- coding: utf-8 -*-

##################################################
 # Soubor: stats.py
 # Projekt - Interpret of IPPcode20's XML representation
 # Autor: Marek Ziska, xziska03@stud.fit.vutbr.cz
 # Skupina: 2BIB
 # Datum 14.04.2020
##################################################

from myerrors import *


class Stats:
    def __init__(self, args):
        """
        Args:
            args: Argument class, holds a lot of data needed in Stats
        """
        self.passed_args = args.passedArgs
        self.stats_file = args.statsFile
        self.stat_insts = False
        self.stat_vars = False
        self.max_vars_count = 0
        self.instr_count = 0
        self.vars_count = 0
        self.first_stat_arg = args.first_stat_arg
        if "insts" in self.passed_args:
            self.stat_insts = True
        if "vars" in self.passed_args:
            self.stat_vars = True
        if ("insts" not in self.passed_args and "vars" not in self.passed_args) and "stats" in self.passed_args:
            raise ArgError("Error 10: Wrong combination of arguments!")

    def update_instr_count(self):
        """ counts instructions
        """
        self.instr_count += 1

    def check_vars_count(self, frame):
        """ counts instructions
        Args:
            :param frame: observed frame
        """
        if frame.init_vars > self.max_vars_count:
            self.max_vars_count = frame.init_vars

    def print_statistics(self):
        """ Prints statistics to desired file
        """
        if "stats" in self.passed_args:
            with open(self.stats_file, "w") as f:
                if self.stat_insts and self.stat_vars:
                    if self.first_stat_arg == "insts":
                        f.write(str(self.instr_count) + "\n" + str(self.max_vars_count))
                    else:
                        f.write(str(self.max_vars_count) + "\n" + str(self.instr_count))
                elif self.stat_insts:
                    f.write(str(self.instr_count))
                elif self.stat_vars:
                    f.write(str(self.max_vars_count))
                else:
                    pass

