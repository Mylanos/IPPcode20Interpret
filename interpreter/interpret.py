#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from argument import Arguments
from parser import Parser as Parser



Args = Arguments(sys.argv[1:])
ParserO = Parser(Args.sourceFile)
ParserO.parse()

