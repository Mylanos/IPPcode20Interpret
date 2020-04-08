#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
from argument import Arguments
from myerrors import *
from parser import Parser as Parser


class Frame:
    def __init__(self):
        self.variables = {}
        self.types = {}

    def update_variable(self, name, value, var_type):
        self.variables[name] = value
        self.types[name] = var_type

    def get_type_and_value(self, name):
        if name in self.variables:
            return self.types[name], self.variables[name]
        else:
            raise AccesingAbsentVariableError("Error 54: Trying to access undefined variable!")


class Interpret:

    def __init__(self):
        self.global_frame = Frame()
        self.local_frame = []
        self.temporary_frame = None
        self.output = ""
        self.instr_list = []
        self.instr_index = 0
        self.label_dict = {}
        self.call_index_stack = []
        self.value_stack = []
        self.type_stack = []
        self.input_lines = None

    def start(self):
        args = Arguments(sys.argv[1:])
        parser = Parser(args.sourceFile)
        parser.parse()
        self.instr_list = parser.instr_list
        try:
            self.search_and_store_labels(self.instr_list)
            if args.inputFile:
                with open(args.inputFile) as file_handle:
                    self.input_lines = file_handle.read().splitlines()
        except SemanticError as SE:
            print(SE.get_msg())
            sys.exit(SE.code)
        except FileNotFoundError:
            print("rip omfg")
            sys.exit(11)
        while self.instr_index < len(self.instr_list):
            try:
                self.__execution(self.instr_list[self.instr_index])
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
            except StringOperationError as SOE:
                print(SOE.get_msg())
                sys.exit(SOE.code)
            except WrongOperandsError as WOE:
                print(WOE.get_msg())
                sys.exit(WOE.code)
            except SemanticError as SE:
                print(SE.get_msg())
                sys.exit(SE.code)
            except ValueError:
                print("rip pff")
                sys.exit(58)
            self.instr_index += 1

    def search_and_store_labels(self, instr_list):
        index = 0
        for item in instr_list:
            if item.name == "LABEL":
                if item.arg_contents[0] in self.label_dict:
                    raise SemanticError("Error 52: Redefinition of label!")
                self.label_dict[item.arg_contents[0]] = index
            index += 1

    def __execution(self, instruct):
        if instruct.name == "CREATEFRAME":
            self.temporary_frame = Frame()
        elif instruct.name == "POPFRAME":
            if not self.local_frame:
                raise FrameDoesntExistError("Error 55: Trying to pop undefined frame!")
            self.temporary_frame = self.local_frame.pop(-1)
        elif instruct.name == "PUSHFRAME":
            if not self.temporary_frame:
                raise FrameDoesntExistError("Error 55: Trying to push undefined frame!")
            self.local_frame.append(self.temporary_frame)
            self.temporary_frame = None
        elif instruct.name == "DEFVAR":
            self.defvar(instruct)
        elif instruct.name == "WRITE":
            self.__write(instruct)
        elif instruct.name == "EXIT":
            self.__exit(instruct)
        elif instruct.name == "MOVE":
            self.__move(instruct)
        elif instruct.name in ["ADD", "MUL", "IDIV", "SUB", "AND", "NOT", "OR", "LT", "GT", "EQ"]:
            self.__basic_operations(instruct)
        elif instruct.name in "TYPE":
            self.__type(instruct)
        elif instruct.name in ["INT2CHAR", "STRLEN", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR"]:
            self.__string_operations(instruct)
        elif instruct.name == "LABEL":
            pass
        elif instruct.name in ["JUMP", "CALL", "RETURN"]:
            self.__flow_instructions(instruct)
        elif instruct.name in ["BREAK", "DPRINT"]:
            self.__debug_instructions(instruct)
        elif instruct.name in ["POPS", "PUSHS"]:
            self.__stack_instructions(instruct)
        elif instruct.name in ["JUMPIFEQ", "JUMPIFNEQ"]:
            self.__cond_jumps(instruct)
        elif instruct.name == "READ":
            self.__read(instruct)

    def defvar(self, instruct):
        var_parts = instruct.arg_contents[0].split('@')
        var_frame = var_parts[0]
        var_name = var_parts[1]
        if var_frame == "GF":
            self.global_frame.update_variable(var_name, None, None)
        elif var_frame == "TF":
            if self.temporary_frame is None:
                raise FrameDoesntExistError("Error 55: Trying to define variable in undefined frame!")
            self.temporary_frame.update_variable(var_name, None, None)
        elif var_frame == "LF":
            self.local_frame[-1].update_variable(var_name, None, None)
        else:
            raise InternalError("Error 99: Internal error, unknown frame! ")

    def __write(self, instruct):
        if instruct.arg_types[0] == "var":
            arg_type, arg_value = self.__get_value_var(instruct.arg_contents[0])
            if arg_value is None:
                raise MissingValueError("Error 56: Trying to output uninitialized variable!")
            else:
                if arg_type == "bool":
                    print(str(arg_value).lower(), end="")
                else:
                    print(arg_value, end="")
        else:
            constant = instruct.arg_contents[0]
            print(constant, end="")

    def __split_argument_content(self, arg_content):
        var_parts = arg_content.split('@')
        return var_parts[0], var_parts[1]

    def __check_undefined_frame(self, frame):
        if frame == "GF":
            if self.global_frame is not None:
                return
        elif frame == "LF":
            if self.local_frame is not None:
                return
        elif frame == "TF":
            if self.temporary_frame is not None:
                return
        raise FrameDoesntExistError("Error 55: Trying to access undefined frame!")

    def __get_value_var(self, arg_content):
        frame, name = self.__split_argument_content(arg_content)
        self.__check_undefined_frame(frame)
        if frame == "GF":
            return self.global_frame.get_type_and_value(name)
        elif frame == "LF":
            return self.local_frame[-1].get_type_and_value(name)
        elif frame == "TF":
            return self.temporary_frame.get_type_and_value(name)
        else:
            raise InternalError("Error 99: Internal error, unknown frame!")

    def __exit(self, instruct):
        # treba tiež čekovať podla toho do akeho framu pristupovat
        if instruct.arg_types[0] == "var":
            arg_type, arg_value = self.__get_value_var(instruct.arg_contents[0])
            if arg_value is None:
                raise MissingValueError("Error 56: Trying to access uninitialized variable!")
            elif arg_type == "int":
                if 50 > arg_value >= 0:
                    sys.exit(arg_value)
                else:
                    raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49!")
            else:
                raise OperandsValueError("Error 57: Wrong value of EXIT's operand!")
        elif instruct.arg_types[0] == "int":
            exit_code = instruct.arg_contents[0]
            if 50 > exit_code >= 0:
                sys.exit(exit_code)
            else:
                raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49!")
        else:
            raise OperandsValueError("Error 57: Wrong value of EXIT's operand!")

    def __store_value(self, frame, name, arg_value, arg_type):
        if frame == "GF":
            self.global_frame.update_variable(name, arg_value, arg_type)
        elif frame == "LF":
            self.local_frame[-1].update_variable(name, arg_value, arg_type)
        elif frame == "TF":
            if self.temporary_frame is None:
                raise FrameDoesntExistError("Error 55: Trying to access variable in undefined frame!")
            self.temporary_frame.update_variable(name, arg_value, arg_type)
        else:
            raise InternalError("Error 99: Internal error, unknown frame!")

    def __get_value_symb(self, instruct, index):
        var_type = instruct.arg_types[index]
        if var_type in ["string", "int", "bool", "nil"]:
            return instruct.arg_types[index], instruct.arg_contents[index]
        elif var_type == "var":
            return self.__get_value_var(instruct.arg_contents[index])
        else:
            raise InternalError("Error 99: Internal error, unknown type!")

    def __move(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type, arg_value = self.__get_value_symb(instruct, 1)
        self.__store_value(frame, name, arg_value, arg_type)

    def __basic_operations(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type1, arg_value1 = self.__get_value_symb(instruct, 1)
        result = None
        if instruct.name == "NOT":
            if arg_type1 == "bool":
                print(arg_value1)
                self.__store_value(frame, name, not arg_value1, arg_type1)
            else:
                raise OperandsValueError("Error 57: NOT instruction is expecting bool!")
        else:
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2)
            if arg_type1 == "bool" and arg_type2 == "bool":
                if instruct.name == "AND":
                    result = arg_value1 and arg_value2
                elif instruct.name == "OR":
                    result = arg_value1 or arg_value2
                elif instruct.name == "LT":
                    result = arg_value1 < arg_value2
                elif instruct.name == "GT":
                    result = arg_value1 > arg_value2
                elif instruct.name == "EQ":
                    result = arg_value1 == arg_value2
                else:
                    raise OperandsValueError("Error 53: Passed arguments are not compatible with instruction!")
                self.__store_value(frame, name, result, arg_type1),

            elif arg_type1 == "int" and arg_type2 == "int" or \
                    arg_type1 == "string" and arg_type1 == "string":
                if instruct.name == "LT":
                    result = arg_value1 < arg_value2
                elif instruct.name == "GT":
                    result = arg_value1 > arg_value2
                elif instruct.name == "EQ":
                    result = arg_value1 == arg_value2
                if arg_type1 == "int" and arg_type2 == "int":
                    if instruct.name == "IDIV":
                        if arg_value2 == 0:
                            raise OperandsValueError("Error 57: DIV instruction tried to divide by zero!")
                        result = arg_value1 / arg_value2
                        result = int(result)
                    elif instruct.name == "MUL":
                        result = arg_value1 * arg_value2
                    elif instruct.name == "ADD":
                        result = arg_value1 + arg_value2
                    elif instruct.name == "SUB":
                        result = arg_value1 - arg_value2
                    else:
                        raise WrongOperandsError("Error 53: Passed arguments are not compatible with instruction! " +
                                                 "(\"" + instruct.name + "\")")
                else:
                    raise WrongOperandsError("Error 53: Instruction is expecting int!")
                self.__store_value(frame, name, result, arg_type1)
            else:
                raise WrongOperandsError("Error 53: Instructions are expecting bool/string/int and "
                                         "both operands of the same type !")

    def __type(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type, arg_value = self.__get_value_symb(instruct, 1)
        if arg_type in ["nil", "string", "bool", "int"]:
            self.__store_value(frame, name, arg_type, arg_type)
        else:
            if arg_value is None:
                self.__store_value(frame, name, "", "string")
            else:
                raise InternalError("Error 99: Internal error, unknown type! ")

    def __string_operations(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type1, arg_value1 = self.__get_value_symb(instruct, 1)
        if instruct.name == "INT2CHAR":
            if arg_type1 == "int":
                self.__store_value(frame, name, chr(arg_value1), "string")
            else:
                raise WrongOperandsError("Error 53: Instruction INT2CHAR received wrong operand type, expecting int!")
        elif instruct.name == "STRLEN":
            if arg_type1 == "string":
                self.__store_value(frame, name, len(arg_value1), "int")
            else:
                raise WrongOperandsError("Error 53: Instruction STRLEN received wrong operand type, expecting string!")
        else:
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2)
            if instruct.name == "STRI2INT":
                if arg_type1 == "string" and arg_type2 == "int":
                    if arg_value2 > len(arg_value1) or arg_value2 < 0:
                        raise StringOperationError("Error 58: Index in STRI2INT is out of range!")
                    self.__store_value(frame, name, ord(arg_value1[arg_value2]), "int")
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction INT2CHAR received wrong operands type, expecting (\"string int\")!")
            elif instruct.name == "CONCAT":
                if arg_type1 == "string" and arg_type2 == "string":
                    self.__store_value(frame, name, arg_value1 + arg_value2, "string")
                else:
                    raise  WrongOperandsError(
                        "Error 53: Instruction CONCAT received wrong operands, expecting (\"string string\")!")
            elif instruct.name == "GETCHAR":
                if arg_type1 == "string" and arg_type2 == "int":
                    if arg_value2 > len(arg_value1) or arg_value2 < 0:
                        raise StringOperationError("Error 58: Index is out of range in string!")
                    self.__store_value(frame, name, arg_value1[arg_value2], "int")
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction GETCHAR received wrong operands type, expecting (\"string int\")!")
            elif instruct.name == "SETCHAR":
                arg_type0, arg_value0 = self.__get_value_var(instruct.arg_contents[0])
                if arg_type0 == "string" and arg_type1 == "int" and arg_type2 == "string":
                    if arg_value1 > len(arg_value0) or arg_value1 < 0:
                        raise StringOperationError("Error 58: Index is out of range in string!")
                    string_list = list(arg_value0)
                    string_list[arg_value1] = arg_value2[0]
                    self.__store_value(frame, name, "".join(string_list), "string")
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction GETCHAR received wrong operands type, expecting (\"string int string\")!")

    def __flow_instructions(self, instruct):
        if instruct.name == "RETURN":
            if not self.call_index_stack:
                raise MissingValueError("Error 56: Return instruction appeared before any CALL! (Call stack is empty)")
            return_to_index = self.call_index_stack[-1]
            self.instr_index = return_to_index
        else:
            if instruct.arg_contents[0] in self.label_dict:
                if instruct.name == "JUMP":
                    jump_to_index = self.label_dict.get(instruct.arg_contents[0])
                    self.instr_index = jump_to_index
                elif instruct.name == "CALL":
                    jump_to_index = self.label_dict.get(instruct.arg_contents[0])
                    self.call_index_stack.append(self.instr_index)
                    self.instr_index = jump_to_index
            else:
                raise SemanticError("Error 52: Instruction JUMP/CALL received undefined label!")

    def __debug_instructions(self, instruct):
        if instruct.name == "BREAK":
            print("custom break output", file=sys.stderr, end="")
        else:
            _, arg_value = self.__get_value_symb(instruct, 0)
            print(arg_value, file=sys.stderr, end="")

    def __stack_instructions(self, instruct):
        if instruct.name == "PUSHS":
            arg_type, arg_value = self.__get_value_symb(instruct, 0)
            self.value_stack.append(arg_value)
            self.type_stack.append(arg_type)
        else:
            if self.value_stack:
                frame, name = self.__split_argument_content(instruct.arg_contents[0])
                value = self.value_stack.pop(-1)
                _type = self.type_stack.pop(-1)
                self.__store_value(frame, name, value, _type)
            else:
                raise MissingValueError("Error 56: Instruction POP was called on empty stack!")

    def __cond_jumps(self, instruct):
        if instruct.arg_contents[0] not in self.label_dict:
            raise SemanticError("Error 52: Instruction JUMPIFEQ/JUMPIFNEQ received undefined label!")
        jump_to_index = self.label_dict.get(instruct.arg_contents[0])
        arg_type1, arg_value1 = self.__get_value_symb(instruct, 1)
        arg_type2, arg_value2 = self.__get_value_symb(instruct, 2)
        if arg_type1 == arg_type2:
            if instruct.name == "JUMPIFEQ":
                if arg_value1 == arg_value2:
                    self.instr_index = jump_to_index
            elif instruct.name == "JUMPIFNEQ":
                if arg_value1 != arg_value2:
                    self.instr_index = jump_to_index
        else:
            raise WrongOperandsError(
                "Error 53: Instruction JUMPIFEQ/JUMPIFNEQ received wrong operands type! ")

    def __is_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __read(self, instruct):
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        _type = instruct.arg_contents[1]
        if self.input_lines:
            user_input = self.input_lines.pop(0)
        else:
            user_input = input()

        if self.__is_int(user_input) and _type == "int":
            self.__store_value(frame, name, int(user_input), _type)
        elif isinstance(user_input, str) and _type == "string":
            self.__store_value(frame, name, user_input, _type)
        elif (user_input == "true" or user_input == "false") and _type == "bool":
            self.__store_value(frame, name, bool(user_input), _type)
        else:
            self.__store_value(frame, name, "nil", "nil")


interpret = Interpret()
interpret.start()