#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from argument import Arguments
from myerrors import *
from parser import Parser as Parser


class Frame:
    def __init__(self):
        self.variables = {}

    def update_variable(self, name, value):
        self.variables[name] = value

    def get_value(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            raise AccesingAbsentVariableError("Error 54: Trying to access undefined variable! (\"" + name + "\")")


class Interpret:

    def __init__(self):
        self.global_frame = Frame()
        self.local_frame = [self.global_frame]
        self.temporary_frame = None
        self.output = ""

    def start(self):
        args = Arguments(sys.argv[1:])
        parser = Parser(args.sourceFile)
        parser.parse()
        for instruct in parser.instr_list:
            try:
                self.__execution(instruct)
            except InternalError as InE:
                print(InE.get_msg())
                sys.exit(InE.code)
            except AccesingAbsentVariableError as AAVE:
                print(AAVE.get_msg())
                sys.exit(AAVE.code)
            except FrameDoesntExistError as FDE:
                print(FDE.get_msg())
                sys.exit(FDE.code)
            except MissingValueError as MVE:
                print(MVE.get_msg())
                sys.exit(MVE.code)
            except OperandsValueError as OVE:
                print(OVE.get_msg())
                sys.exit(OVE.code)

    def __execution(self, instruct):
        if instruct.name == "CREATEFRAME":
            self.temporary_variables = Frame()
        elif instruct.name == "POPFRAME":
            self.local_frame.pop(-1)
        elif instruct.name == "PUSHFRAME":
            self.local_frame.append(self.temporary_frame)
        elif instruct.name == "DEFVAR":
            self.defvar(instruct)
        elif instruct.name == "WRITE":
            self.__write(instruct)
        elif instruct.name == "EXIT":
            self.__exit(instruct)
        elif instruct.name == "MOVE":
            self.__move(instruct)
        elif instruct.name in ["ADD", "MUL", "IDIV", "SUB"]:
            self.__basic_int_operations(instruct)

    def defvar(self, instruct):
        var_parts = instruct.arg_contents[0].split('@')
        var_frame = var_parts[0]
        var_name = var_parts[1]
        if var_frame == "GF":
            self.global_frame.update_variable(var_name, None)
        elif var_frame == "TF":
            if self.temporary_frame is None:
                raise FrameDoesntExistError("Error 55: Trying to define variable in undefined frame! (\""
                                            + var_frame + "\")")
            self.temporary_frame[var_name] = None
        elif var_frame == "LF":
            self.local_frame[-1].update_variable(var_name, None)
        else:
            raise InternalError("Error 99: Internal error, unknown frame (\"" + var_frame + "\")")

    def __write(self, instruct):
        if instruct.arg_types[0] == "var":
            arg_value = self.__get_value_var(instruct.arg_contents[0])
            if arg_value is None:
                raise MissingValueError("Error 56: Trying to output uninitialized variable!")
            else:
                print(arg_value, end="")

        else:
            constant = instruct.arg_contents[0]
            print(constant, end="")

    def __split_argument_content(self, arg_content):
        var_parts = arg_content.split('@')
        return var_parts[0], var_parts[1]

    def __get_value_var(self, arg_content):
        frame, name = self.__split_argument_content(arg_content)
        if frame == "GF":
            return self.global_frame.get_value(name)
        elif frame == "LF":
            return self.local_frame[-1].get_value(name)
        elif frame == "TF":
            return self.temporary_frame.get_value(name)
        else:
            raise InternalError("Error 99: Internal error, unknown frame (\"" + frame + "\")")

    def __exit(self, instruct):
        # treba tiež čekovať podla toho do akeho framu pristupovat
        if instruct.arg_types[0] == "var":
            instr_value = self.__get_value_var(instruct.arg_contents[0])
            if instr_value is None:
                raise MissingValueError("Error 56: Trying to access uninitialized variable!")
            elif isinstance(instr_value, int):
                if 50 > instr_value >= 0:
                    sys.exit(instr_value)
                else:
                    raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49"
                                             " got (\"" + str(instr_value) + "\")")
            else:
                raise OperandsValueError("Error 57: Wrong value of EXIT's operand! expected (\"int\")"
                                         " got (\"" + str(type(instr_value).__name__) + "\")")
        elif instruct.arg_types[0] == "int":
            exit_code = instruct.arg_contents[0]
            if 50 > exit_code >= 0:
                sys.exit(exit_code)
            else:
                raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49"
                                   " got (\"" + str(exit_code) + "\")")
        else:
            raise OperandsValueError("Error 57: Wrong value of EXIT's operand! expects (\"int|var\") got (\"" +
                                     instruct.arg_types[0] + "\")")

    def __store_value(self, frame, name, arg_value):
        if frame == "GF":
            self.global_frame.update_variable(name, arg_value)
        elif frame == "LF":
            self.local_frame[-1].update_variable(name, arg_value)
        elif frame == "TF":
            if self.temporary_frame is None:
                raise FrameDoesntExistError("Error 55: Trying to access variable in undefined frame! (\""
                                            + frame + "\")")
            self.temporary_frame.update_variable(name, arg_value)
        else:
            raise InternalError("Error 99: Internal error, unknown frame (\"" + frame + "\")")

    def __get_value_symb(self, instruct, index):
        var_type = instruct.arg_types[index]
        if var_type in ["string", "int", "bool", "nil"]:
            return instruct.arg_contents[index]
        elif var_type == "var":
            return self.__get_value_var(instruct.arg_contents[index])
        else:
            raise InternalError("Error 99: Internal error, unknown type (\"" + var_type + "\")")

    def __move(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_value = self.__get_value_symb(instruct, 1)
        self.__store_value(frame, name, arg_value)

    def __basic_int_operations(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_value1 = self.__get_value_symb(instruct, 1)
        arg_value2 = self.__get_value_symb(instruct, 2)
        if isinstance(arg_value1, int) and isinstance(arg_value2, int):
            result = 0
            if instruct.name == "IDIV":
                if arg_value2 == 0:
                    raise OperandsValueError("Error 57: DIV instruction tried to divide by zero!")
                result = arg_value1 / arg_value2
            elif instruct.name == "MUL":
                result = arg_value1 * arg_value2
            elif instruct.name == "ADD":
                result = arg_value1 + arg_value2
            elif instruct.name == "SUB":
                result = arg_value1 - arg_value2
            self.__store_value(frame, name, int(result))
        else:
            raise OperandsValueError("Error 57: DIV instruction expects int! got (\"" +
                                     str(type(arg_value1).__name__) + " / " + str(type(arg_value2).__name__) + "\")")


interpret = Interpret()
interpret.start()