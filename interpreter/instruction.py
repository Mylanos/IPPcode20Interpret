import re
from myerrors import XMLformatError


class Instruction:
    def __init__(self, name):
        self.name = name
        self.arg_types = []
        self.arg_contents = []
        self.arg_count = 0

    def check_inst_without_args(self):
        if self.name not in ["POPFRAME", "RETURN", "PUSHFRAME", "CREATEFRAME", "BREAK"]:
            raise XMLformatError("Error 32: Unknown instruction!"
                                 " Got (" + self.name + ")")

    def arg_append(self, arg_type, arg_content, arg_count):
        self.arg_count = arg_count
        self.__check_corresponding_args(arg_type)
        self.__check_arg_type(arg_type, arg_content)
        self.arg_contents.append(arg_content)
        self.arg_types.append(arg_type)

    def __check_corresponding_args(self, arg_type):
        # instruction expects var
        if self.name in ["DEFVAR", "POPS"]:
            if arg_type == "var":
                return
        # instruction expects symb
        elif self.name in ["PUSHS", "WRITE", "EXIT", "DPRINT"]:
            if arg_type in ["string", "bool", "int", "nil", "var"]:
                return
        # instruction expects label
        elif self.name in ["CALL", "LABEL", "JUMP"]:
            if arg_type == "label":
                return
        # instruction expects var,symb
        elif self.name in ["MOVE", "INT2CHAR", "STRLEN", "TYPE"]:
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2:
                return
        # instruction expects var, type
        elif self.name == "READ":
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type == "type" and self.arg_count == 2:
                return
        # instruction expects var,symb, symb
        elif self.name in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "STRI2INT",
                           "CONCAT", "GETCHAR", "SETCHAR"]:
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2 or \
               arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 3:
                return
        # instruction expects label, symb, symb
        elif self.name in ["JUMPIFEQ", "JUMPIFNEQ"]:
            if arg_type == "label" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2 or \
               arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 3:
                return
        # unknown instruction
        else:
            raise XMLformatError("Error 32: Received unknown instruction \"" + self.name + "\"!")
        raise XMLformatError("Error 32: Received wrong argument type for arg" + str(self.arg_count) + " in instruction "
                             + self.name + "!")

    def __check_arg_type(self, arg_type, arg_content):
        if arg_type == "type":
            if re.match('^(int|string|bool)$', arg_content):
                return
        elif arg_type == "var":
            if re.match('^((LF|GF|TF)@([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
                return
        elif arg_type == "label":
            if re.match('^(([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
                return
        elif arg_type == "string":
            if re.match('^((\\\[0-9]{3}|[^#\\\])*)$', arg_content):
                return
        elif arg_type == "int":
            if re.match('^([0-9]|-|\+)*$', arg_content):
                return
        elif arg_type == "bool":
            if re.match('^(true|false)$', arg_content):
                return
        elif arg_type == "nil":
            if re.match('^nil$', arg_content):
                return
        else:
            raise XMLformatError("Error 32: The arg" + str(self.arg_count) + " in instruction " +
                                 self.name +
                                 " is not valid! Unknown data type \"" + arg_type + "\"")
        raise XMLformatError("Error 32: The content of arg" + str(self.arg_count) + " in instruction " +
                             self.name + " is not valid! Got \"" + arg_content + "\"")



