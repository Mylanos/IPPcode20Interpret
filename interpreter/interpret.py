#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from argument import Arguments
from parser import Parser as Parser


class Interpret:

    def start(self):
        args = Arguments(sys.argv[1:])
        parser = Parser(args.sourceFile)
        parser.parse()
        for instruction in parser.instr_list:
            print(instruction.name)
            print(instruction.arg_contents)

interpret = Interpret()
interpret.start()