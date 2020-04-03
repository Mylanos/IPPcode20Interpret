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
        self.check_corresponding_args(arg_type)
        self.check_arg_type(arg_type, arg_content)
        self.arg_contents.append(arg_content)
        self.arg_types.append(arg_type)

    def check_corresponding_args(self, arg_type):
        # instruction expects var
        if self.name in ["DEFVAR", "POPS"]:
            if arg_type != "var":
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (\"var\") got (\"" + arg_type + "\")")
        # instruction expects symb
        elif self.name in ["PUSHS", "WRITE", "EXIT", "DPRINT"]:
            if arg_type not in ["string", "bool", "int", "nil", "var"]:
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (symb) got (\"" + arg_type + "\")")
        # instruction expects label
        elif self.name in ["CALL", "LABEL", "JUMP"]:
            if arg_type != "label":
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (symb) got (\"" + arg_type + "\")")
        # instruction expects var,symb
        elif self.name in ["MOVE", "INT2CHAR", "STRLEN", "TYPE"]:
            if arg_type == "var" and self.arg_count == 1:
                return
            elif arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2:
                return
            else:
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (\"var\",symb) got (\"" + arg_type + "\")")
        # instruction expects var, type
        elif self.name == "READ":
            if arg_type == "var" and self.arg_count == 1:
                return
            elif arg_type == "type" and self.arg_count == 2:
                return
            else:
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (\"var\",\"type\") got (\"" + arg_type + "\")")
        # instruction expects var,symb, symb
        elif self.name in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "STRI2INT",
                           "CONCAT", "GETCHAR", "SETCHAR"]:
            if arg_type == "var" and self.arg_count == 1:
                return
            elif arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2:
                return
            elif arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 3:
                return
            else:
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (\"var\",symb, symb)")
        # instruction expects label, symb, symb
        elif self.name in ["JUMPIFEQ", "JUMPIFNEQ"]:
            if arg_type == "label" and self.arg_count == 1:
                return
            elif arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 2:
                return
            elif arg_type in ["string", "bool", "int", "nil", "var"] and self.arg_count == 3:
                return
            else:
                raise XMLformatError("Error 32: Received wrong argument type for " + self.name + "!"
                                     " Expected (\"label\", symb, symb)")

    def is_constant(self, arg_type, arg_content):
        if arg_type == "string":
            if not re.match('^((\\\[0-9]{3}|[^#\\\])*)$', arg_content):
                return False
            return True
        elif arg_type == "int":
            if not re.match('^([0-9]|-|\+)*$', arg_content):
                return False
            return True
        elif arg_type == "bool":
            if not re.match('^(true|false)$', arg_content):
                return False
            return True
        elif arg_type == "nil":
            if not re.match('^nil$', arg_content):
                return False
            return True
        else:
            raise XMLformatError("Error 32: The arg" + str(self.arg_count) + " in instruction " +
                                 self.name +
                                 " is not valid! Unknown data type \"" + arg_type + "\"")

    def is_variable(self, arg_content):
        if re.match('^((LF|GF|TF)@([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
            return True
        return False

    def check_arg_type(self, arg_type, arg_content):
        if arg_type == "type":
            if not re.match('^(int|string|bool)$', arg_content):
                raise XMLformatError("Error 32: The content of instruction " + self.name +
                                     " is not valid! \"(bool|int|string)\" expected, got \"" + arg_content + "\"")
        elif arg_type == "var":
            if not self.is_variable(arg_content):
                raise XMLformatError("Error 32: The content of  arg" + str(self.arg_count) + " in instruction " +
                                     self.name +
                                     " is not valid! \"(GF|LF|TF@someVar)\" expected, got \"" + arg_content + "\"")
        elif arg_type == "label":
            if not re.match('^(([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
                raise XMLformatError("Error 32: The content of arg" + str(self.arg_count) + " in instruction " +
                                     self.name +
                                     " is not valid! \"(seqOfChars without \s)\" expected, got \"" + arg_content + "\"")
        else:
            if not self.is_constant(arg_type, arg_content):
                raise XMLformatError("Error 32: The content of arg" + str(self.arg_count) + " in instruction " +
                                     self.name +
                                     " is not valid! Got \"" + arg_content + "\"")
