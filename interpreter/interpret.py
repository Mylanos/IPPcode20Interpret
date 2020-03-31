#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from myerrors import *
from argument import Arguments

args = sys.argv[1:]
try:
    Arguments = Arguments(args)
except Exception as error:
    print("Caught this error : " + repr(error))
