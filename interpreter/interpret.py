#!/usr/local/bin/python
# -*- coding: utf-8 -*-

##################################################
 # Soubor: interpret.py
 # Projekt - Interpret of IPPcode20's XML representation
 # Autor: Marek Ziska, xziska03@stud.fit.vutbr.cz
 # Skupina: 2BIB
 # Datum 14.04.2020
##################################################

import sys
from argument import Arguments
from frame import Frame
from myerrors import *
from parser import Parser as Parser
from stats import Stats


class Interpret:

    def __init__(self):
        self.global_frame = Frame()
        self.local_frame = []
        self.temporary_frame = None
        self.instr_list = []
        self.instr_index = 0
        self.label_dict = {}
        self.call_index_stack = []
        self.value_stack = []
        self.type_stack = []
        self.input_lines = None
        self.input_file = None
        self.statistics = None

    def start(self):
        """ Main method of interpret
        """
        # parses arguments
        args = Arguments(sys.argv[1:])
        self.input_file = args.inputFile
        # parses source XML file
        parser = Parser(args.sourceFile)
        parser.parse()
        self.instr_list = parser.instr_list
        try:
            self.search_and_store_labels(self.instr_list)
            # statistics class
            self.statistics = Stats(args)
            if self.input_file:
                with open(self.input_file) as file_handle:
                    self.input_lines = file_handle.read().splitlines()
        except Error as E:
            print(E.get_msg())
            sys.exit(E.code)
        except FileNotFoundError:
            print("Error 11: ", file=sys.stderr)
            sys.exit(11)
        # loops over all instructions
        while self.instr_index < len(self.instr_list):
            try:
                # executes current instruction
                self.__execution(self.instr_list[self.instr_index])
            except Error as E:
                print(E.get_msg(), file=sys.stderr)
                sys.exit(E.code)
            except ValueError:
                print("rip pff", file=sys.stderr)
                sys.exit(58)
            self.instr_index += 1
            self.statistics.update_instr_count()
        self.__exit_interpret(0)

    def __exit_interpret(self, exit_code):
        """ Quits interpret with possible output of statistics
        Args:
            exit_code:
        """
        self.__count_vars_in_frames()
        self.statistics.print_statistics()
        sys.exit(exit_code)

    def __count_vars_in_frames(self):
        """ count vars in all frames
        """
        for frame in self.local_frame:
            self.statistics.update_vars_count(frame.initialized_stats_count)
        self.statistics.update_vars_count(self.global_frame.initialized_stats_count)
        if self.temporary_frame:
            self.statistics.update_vars_count(self.temporary_frame.initialized_stats_count)

    def search_and_store_labels(self, instr_list):
        """ Finds all labels, checks for uniqueness of label and saves index
        Args:
            instr_list: instruction list
        """
        index = 0
        for item in instr_list:
            if item.name == "LABEL":
                if item.arg_contents[0] in self.label_dict:
                    raise SemanticError("Error 52: Redefinition of label!")
                self.label_dict[item.arg_contents[0]] = index
            index += 1

    def __execution(self, instruct):
        """ Directs flow of program according to current instruction
        Args:
            instruct: instruction class
        """
        if instruct.name == "CREATEFRAME":
            self.temporary_frame = Frame()
        elif instruct.name == "POPFRAME":
            if not self.local_frame:
                raise FrameDoesntExistError("Error 55: Trying to pop undefined frame!")
            self.statistics.update_vars_count(self.local_frame[-1].initialized_stats_count)
            self.temporary_frame = self.local_frame.pop(-1)
        elif instruct.name == "PUSHFRAME":
            if not self.temporary_frame:
                raise FrameDoesntExistError("Error 55: Trying to push undefined frame!")
            self.local_frame.append(self.temporary_frame)
            self.temporary_frame = None
        elif instruct.name == "DEFVAR":
            self.__defvar(instruct)
        elif instruct.name == "WRITE":
            self.__write(instruct)
        elif instruct.name == "EXIT":
            self.__exit(instruct)
        elif instruct.name == "MOVE":
            self.__move(instruct)
        elif instruct.name in ["ADD", "MUL", "IDIV", "SUB", "AND", "OR", "LT", "GT", "EQ"]:
            self.__basic_operations(instruct, False)
        elif instruct.name in ["ADDS", "MULS", "IDIVS", "SUBS", "ANDS", "ORS", "LTS", "GTS", "EQS"]:
            self.__basic_operations(instruct, True)
        elif instruct.name in "TYPE":
            self.__type(instruct)
        elif instruct.name == "NOT":
            self.__not(instruct, False)
        elif instruct.name == "NOTS":
            self.__not(instruct, True)
        elif instruct.name in ["INT2CHAR", "STRLEN", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR"]:
            self.__string_operations(instruct, False)
        elif instruct.name in ["INT2CHARS", "STRI2INTS"]:
            self.__string_operations(instruct, True)
        elif instruct.name == "LABEL":
            pass
        elif instruct.name in ["JUMP", "CALL", "RETURN"]:
            self.__flow_instructions(instruct)
        elif instruct.name in ["BREAK", "DPRINT"]:
            self.__debug_instructions(instruct)
        elif instruct.name in ["POPS", "PUSHS"]:
            self.__stack_instructions(instruct)
        elif instruct.name in ["JUMPIFEQ", "JUMPIFNEQ"]:
            self.__cond_jumps(instruct, False)
        elif instruct.name in ["JUMPIFEQS", "JUMPIFNEQS"]:
            self.__cond_jumps(instruct, True)
        elif instruct.name == "READ":
            self.__read(instruct)
        elif instruct.name == "CLEARS":
            self.value_stack = []
            self.type_stack = []

    def __defvar(self, instruct):
        """ Defines variable
        Args:
            instruct: instruction class
        """
        var_parts = instruct.arg_contents[0].split('@')
        var_frame = var_parts[0]
        var_name = var_parts[1]
        if var_frame == "GF":
            self.global_frame.define_variable(var_name)
        elif var_frame == "TF":
            if self.temporary_frame is None:
                raise FrameDoesntExistError("Error 55: Trying to define variable in undefined frame!")
            self.temporary_frame.define_variable(var_name)
        elif var_frame == "LF":
            if self.local_frame:
                self.local_frame[-1].define_variable(var_name)
            else:
                raise FrameDoesntExistError("Error 55: Trying to define variable in undefined frame!")
        else:
            raise InternalError("Error 99: Internal error, unknown frame! ")

    def __write(self, instruct):
        """ Writes content of instruction to stdin
        Args:
            instruct: instruction class
        """
        if instruct.arg_types[0] == "var":
            arg_type, arg_value = self.__get_value_var(instruct.arg_contents[0])
            if arg_value is None:
                raise MissingValueError("Error 56: Trying to output uninitialized variable!")
            else:
                if arg_type == "bool":
                    print(str(arg_value).lower(), end="")
                elif arg_type == "nil":
                    print("", end="")
                else:
                    print(arg_value, end="")
        else:
            constant = instruct.arg_contents[0]
            if constant == "nil" and instruct.arg_types[0]:
                print("", end="")
            elif instruct.arg_types[0] == "bool":
                print(str(constant).lower(), end="")
            else:
                print(constant, end="")

    def __split_argument_content(self, arg_content):
        """ Splits content with @ which separates frame with name of variable
        Args:
            arg_content: content of instruction to be divided
        """
        var_parts = arg_content.split('@')
        return var_parts[0], var_parts[1]

    def __check_undefined_frame(self, frame):
        """ check if frame is defined
        Args:
            frame:
        """
        if frame == "GF":
            if self.global_frame is not None:
                return
        elif frame == "LF":
            if self.local_frame:
                return
        elif frame == "TF":
            if self.temporary_frame is not None:
                return
        raise FrameDoesntExistError("Error 55: Trying to access undefined frame!")

    def __get_value_var(self, arg_content):
        """ Gets type and value of a variable
        Args:
            arg_content: content of instruction to be divided
        """
        frame, name = self.__split_argument_content(arg_content)
        self.__check_undefined_frame(frame)
        type_exception = False
        if self.instr_list[self.instr_index].name == "TYPE":
            type_exception = True
        if frame == "GF":
            return self.global_frame.get_type_and_value(name, type_exception)
        elif frame == "LF":
            return self.local_frame[-1].get_type_and_value(name, type_exception)
        elif frame == "TF":
            return self.temporary_frame.get_type_and_value(name, type_exception)
        else:
            raise InternalError("Error 99: Internal error, unknown frame!")

    def __exit(self, instruct):
        # treba tiež čekovať podla toho do akeho framu pristupovat
        """ Exits interpretation
        Args:
            instruct:  Instruction class
        """
        if instruct.arg_types[0] == "var":
            arg_type, arg_value = self.__get_value_var(instruct.arg_contents[0])
            if arg_value is None:
                raise MissingValueError("Error 56: Trying to access uninitialized variable!")
            elif arg_type == "int":
                if 50 > arg_value >= 0:
                    self.__exit_interpret(arg_value)
                else:
                    raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49!")
            else:
                raise WrongOperandsError("Error 53: Wrong value of EXIT's operand!")
        elif instruct.arg_types[0] == "int":
            exit_code = instruct.arg_contents[0]
            if 50 > exit_code >= 0:
                self.__exit_interpret(exit_code)
            else:
                raise OperandsValueError("Error 57: Value out of range! Exit function expects int in range 0..49!")
        else:
            raise WrongOperandsError("Error 53: Wrong value of EXIT's operand!")

    def __store_value(self, frame, name, arg_value, arg_type, stack):
        """ Stores value and type to variable
        Args:
            frame: frame var is defined in
            name: name of var
            arg_value: value of variable
            arg_type: type of variable
        """
        if stack:
            self.value_stack.append(arg_value)
            self.type_stack.append(arg_type)
        else:
            self.__check_undefined_frame(frame)
            if frame == "GF":
                self.global_frame.update_variable(name, arg_value, arg_type)
            elif frame == "LF":
                self.local_frame[-1].update_variable(name, arg_value, arg_type)
            elif frame == "TF":
                self.temporary_frame.update_variable(name, arg_value, arg_type)
            else:
                raise InternalError("Error 99: Internal error, unknown frame!")

    def __get_value_symb(self, instruct, index, stack):
        """ Returns value of <symb>, which can be variable or a constant
        Args:
            instruct: Instruction class
            index: index of Instruction's argument
            stack: flag when called in stack instructions
        """
        if stack:
            if self.value_stack:
                return self.type_stack.pop(-1), self.value_stack.pop(-1)
            else:
                raise MissingValueError("Error 56: Instruction POP was called on empty stack!")
        else:
            var_type = instruct.arg_types[index]
            if var_type in ["string", "int", "bool", "nil"]:
                return instruct.arg_types[index], instruct.arg_contents[index]
            elif var_type == "var":
                return self.__get_value_var(instruct.arg_contents[index])
            else:
                raise InternalError("Error 99: Internal error, unknown type!")

    def __move(self, instruct):
        """ Moves value to variable
        Args:
            instruct: Instruction class
        """
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type, arg_value = self.__get_value_symb(instruct, 1, False)
        self.__store_value(frame, name, arg_value, arg_type, False)

    def __not(self, instruct, stack):
        """ Negates instruction's value
        Args:
            instruct: Instruction class
            stack: flag when called in stack instructions
        """
        frame = None
        name = None
        if not stack:
            frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
        if arg_type1 == "bool":
            self.__store_value(frame, name, not arg_value1, arg_type1, stack)
        else:
            raise WrongOperandsError("Error 53: NOT instruction is expecting bool!")

    def __basic_operations(self, instruct, stack):
        """ Executes commands [ADD/ADDS,MUL/MULS,IDIV/IDIVS,SUB/SUBS,AND/ANDS,OR/ORS,LT/LTS,GT/GTS,EQ/EQS]
        Args:
            instruct: Instruction object
            stack: flag when called in stack instructions
        """
        result = None
        frame = None
        name = None
        if stack:
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)
            arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
        else:
            frame, name = self.__split_argument_content(instruct.arg_contents[0])
            arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)

        if (arg_type1 == "bool" and arg_type2 == "bool") or \
                (arg_type1 == "int" and arg_type2 == "int") or \
                (arg_type1 == "string" and arg_type2 == "string"):
            if instruct.name in ["AND", "ANDS"]:
                result = arg_value1 and arg_value2
            elif instruct.name in ["OR", "ORS"]:
                result = arg_value1 or arg_value2
            elif instruct.name in ["LT", "LTS"]:
                result = arg_value1 < arg_value2
            elif instruct.name in ["GT", "GTS"]:
                result = arg_value1 > arg_value2
            elif instruct.name in ["EQ", "EQS"]:
                result = arg_value1 == arg_value2
            else:
                if arg_type1 != "int":
                    raise WrongOperandsError("Error 53: Passed arguments are not compatible with instruction!" +
                                             "(\"" + instruct.name + "\")")
            if result is not None:
                self.__store_value(frame, name, result, "bool", stack),
                return
        if arg_type1 == "int" and arg_type2 == "int":
            if instruct.name in ["IDIV", "IDIVS"]:
                if arg_value2 == 0:
                    raise OperandsValueError("Error 57: DIV instruction tried to divide by zero!")
                result = arg_value1 / arg_value2
                result = int(result)
            elif instruct.name in ["MUL", "MULS"]:
                result = arg_value1 * arg_value2
            elif instruct.name in ["ADD", "ADDS"]:
                result = arg_value1 + arg_value2
            elif instruct.name in ["SUB", "SUBS"]:
                result = arg_value1 - arg_value2
            else:
                raise WrongOperandsError("Error 53: Passed arguments are not compatible with instruction! " +
                                         "(\"" + instruct.name + "\")")
            self.__store_value(frame, name, result, arg_type1, stack)
        elif arg_type2 == "nil" or arg_type1 == "nil":
            if instruct.name in ["EQ", "EQS"]:
                result = arg_value1 == arg_value2
            else:
                raise WrongOperandsError("Error 53: Nil arguments are only compatible with EQ instruction!" "(\"" +
                                         instruct.name + "\")")
            self.__store_value(frame, name, result, "bool", stack)
        else:
            raise WrongOperandsError("Error 53: Instructions are expecting bool/string/int and "
                                     "both operands of the same type !")

    def __type(self, instruct):
        """
        Args:
            instruct:
        """
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        arg_type, arg_value = self.__get_value_symb(instruct, 1, False)
        if arg_type in ["nil", "string", "bool", "int"]:
            self.__store_value(frame, name, arg_type, "string", False)
        elif arg_type is None:
            self.__store_value(frame, name, "nil", "nil", False)
        else:
            if arg_value is None:
                self.__store_value(frame, name, "", "string", False)
            else:
                raise InternalError("Error 99: Internal error, unknown type! ")

    def __string_operations(self, instruct, stack):
        """
        Args:
            instruct:
        """
        frame = None
        name = None
        arg_type2 = None
        arg_type1 = None
        if stack:
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)
        else:
            frame, name = self.__split_argument_content(instruct.arg_contents[0])
            arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
        if instruct.name == "INT2CHAR":
            if arg_type1 == "int":
                self.__store_value(frame, name, chr(arg_value1), "string", stack)
            else:
                raise WrongOperandsError("Error 53: Instruction INT2CHAR received wrong operand type, expecting int!")
        elif instruct.name == "INT2CHARS":
            if arg_type2 == "int":
                self.__store_value(frame, name, chr(arg_value2), "string", stack)
            else:
                raise WrongOperandsError("Error 53: Instruction INT2CHAR received wrong operand type, expecting int!")
        elif instruct.name == "STRLEN":
            if arg_type1 == "string":
                self.__store_value(frame, name, len(arg_value1), "int", False)
            else:
                raise WrongOperandsError("Error 53: Instruction STRLEN received wrong operand type, expecting string!")
        else:
            if stack:
                arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
            else:
                arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)
            if instruct.name in ["STRI2INT", "STRI2INTS"]:
                if arg_type1 == "string" and arg_type2 == "int":
                    if arg_value2 >= len(arg_value1) or arg_value2 < 0:
                        raise StringOperationError("Error 58: Index in STRI2INT is out of range!")
                    self.__store_value(frame, name, ord(arg_value1[arg_value2]), "int", stack)
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction INT2CHAR received wrong operands type, expecting (\"string int\")!")
            elif instruct.name == "CONCAT":
                if arg_type1 == "string" and arg_type2 == "string":
                    self.__store_value(frame, name, arg_value1 + arg_value2, "string", False)
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction CONCAT received wrong operands, expecting (\"string string\")!")
            elif instruct.name == "GETCHAR":
                if arg_type1 == "string" and arg_type2 == "int":
                    if arg_value2 >= len(arg_value1) or arg_value2 < 0:
                        raise StringOperationError("Error 58: Index is out of range in string!")
                    self.__store_value(frame, name, arg_value1[arg_value2], "string", False)
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction GETCHAR received wrong operands type, expecting (\"string int\")!")
            elif instruct.name == "SETCHAR":
                arg_type0, arg_value0 = self.__get_value_var(instruct.arg_contents[0])
                if arg_type0 == "string" and arg_type1 == "int" and arg_type2 == "string":
                    if arg_value1 >= len(arg_value0) or arg_value1 < 0:
                        raise StringOperationError("Error 58: Index is out of range in string!")
                    string_list = list(arg_value0)
                    if arg_value2:
                        string_list[arg_value1] = arg_value2[0]
                    else:
                        raise StringOperationError("Error 58: Bad value of SETCHAR operand!")
                    self.__store_value(frame, name, "".join(string_list), "string", False)
                else:
                    raise WrongOperandsError(
                        "Error 53: Instruction GETCHAR received wrong operands type, expecting (\"string int string\")!")

    def __flow_instructions(self, instruct):
        """
        Args:
            instruct:
        """
        if instruct.name == "RETURN":
            if not self.call_index_stack:
                raise MissingValueError("Error 56: Return instruction appeared before any CALL! (Call stack is empty)")
            return_to_index = self.call_index_stack.pop()
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
        """
        Args:
            instruct:
        """
        if instruct.name == "BREAK":
            print("custom break output", file=sys.stderr, end="")
        else:
            _, arg_value = self.__get_value_symb(instruct, 0, False)
            print(arg_value, file=sys.stderr, end="")

    def __stack_instructions(self, instruct):
        """
        Args:
            instruct:
        """
        if instruct.name == "PUSHS":
            arg_type, arg_value = self.__get_value_symb(instruct, 0, False)
            self.value_stack.append(arg_value)
            self.type_stack.append(arg_type)
        else:
            if self.value_stack:
                frame, name = self.__split_argument_content(instruct.arg_contents[0])
                value = self.value_stack.pop(-1)
                _type = self.type_stack.pop(-1)
                self.__store_value(frame, name, value, _type, False)
            else:
                raise MissingValueError("Error 56: Instruction POP was called on empty stack!")

    def __cond_jumps(self, instruct, stack):
        """
        Args:
            instruct:
            stack:
        """
        if instruct.arg_contents[0] not in self.label_dict:
            raise SemanticError("Error 52: Instruction JUMPIFEQ/JUMPIFNEQ received undefined label!")
        jump_to_index = self.label_dict.get(instruct.arg_contents[0])
        if stack:
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)
            arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
        else:
            arg_type1, arg_value1 = self.__get_value_symb(instruct, 1, stack)
            arg_type2, arg_value2 = self.__get_value_symb(instruct, 2, stack)
        if arg_type1 == arg_type2 or \
                arg_type1 == "nil" or arg_type2 == "nil":
            if instruct.name in ["JUMPIFEQ", "JUMPIFEQS"]:
                if arg_value1 == arg_value2:
                    self.instr_index = jump_to_index
            elif instruct.name in ["JUMPIFNEQ", "JUMPIFNEQS"]:
                if arg_value1 != arg_value2:
                    self.instr_index = jump_to_index
        else:
            raise WrongOperandsError(
                "Error 53: Instruction JUMPIFEQ/JUMPIFNEQ received wrong operands type! " + str(self.instr_index))

    def __is_int(self, string):
        """
        Args:
            string:
        """
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __read(self, instruct):
        """
        Args:
            instruct:
        """
        frame, name = self.__split_argument_content(instruct.arg_contents[0])
        _type = instruct.arg_contents[1]
        if self.input_file:
            if self.input_lines:
                user_input = self.input_lines.pop(0)
            else:
                self.__store_value(frame, name, "nil", "nil", False)
                return
        else:
            user_input = input()

        if self.__is_int(user_input) and _type == "int":
            self.__store_value(frame, name, int(user_input), _type, False)
        elif isinstance(user_input, str) and _type == "string":
            self.__store_value(frame, name, user_input, _type, False)
        elif user_input.lower() == "true" and _type == "bool":
            self.__store_value(frame, name, True, _type, False)
        elif user_input.lower() == "false" and _type == "bool":
            self.__store_value(frame, name, False, _type, False)
        else:
            self.__store_value(frame, name, "nil", "nil", False)


interpret = Interpret()
interpret.start()
