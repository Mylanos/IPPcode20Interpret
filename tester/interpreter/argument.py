
import re
import sys

from myerrors import *


class Arguments:
    def __init__(self, args):
        self.args = args
        self.sourceFile = None
        self.inputFile = None
        self.passedArgs = [""]
        try:
            self.__check_arg_count()
            self.__parse_args()
            self.__check_errors()
        except ArgError as ArgE:
            print("Error: " + ArgE.get_msg(), file=sys.stderr)
            sys.exit(ArgE.err_code())
        except Exception:
            print("Error: Internal program error!")
            sys.exit(99)

    def __parse_args(self):
        for argument in self.args:
            source_arg = re.match("^(--source=(([A-Z]|[a-z]|/|_|[0-9]|.)+))$", argument)
            input_arg = re.match("^(--input=(([A-Z]|[a-z]|/|_|[0-9]|.)+))$", argument)
            help_arg = re.match("^--help$", argument)
            if source_arg:
                self.sourceFile = source_arg.group(2)
                self.passedArgs.append("source")
            elif input_arg:
                self.inputFile = input_arg.group(2)
                self.passedArgs.append("input")
            elif help_arg:
                print("napoveda")
                sys.exit(0)
            else:
                raise ArgError("Unknown argument or format of the argument! (" + argument + ")")

    def __check_errors(self):
        if not("input" in self.passedArgs or "source" in self.passedArgs):
            raise ArgError("Program did not receive any of mandatory arguments! (--source=file, --input=file)")

    def __check_arg_count(self):
        if len(self.args) > 3 or len(self.args) == 0:
            raise ArgError("Unsupported amount of arguments! (" + str(len(self.args)) + ")")

    def get_source_file(self):
        return self.sourceFile

    def get_input_file(self):
        return self.inputFile



