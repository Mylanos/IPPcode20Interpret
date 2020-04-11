import re
from myerrors import XMLformatError


class Instruction:
    def __init__(self, name):
        self.name = name
        self.arg_types = []
        self.arg_contents = []
        self.arg_count = 0

    def check_inst_without_args(self):
        if self.name not in ["POPFRAME", "RETURN", "PUSHFRAME", "CREATEFRAME", "BREAK", "ADDS", "SUBS", "MULS",
                             "IDIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "NOTS", "INT2CHARS", "STRI2INTS", "CLEARS"]:
            raise XMLformatError("Error 32: Unknown instruction or valid instruction without needed arguments!"
                                 " Got (" + self.name + ")")

    def check_argument_count(self, count):
        if self.name in ["DEFVAR", "POPS", "PUSHS", "WRITE", "EXIT", "DPRINT", "CALL", "LABEL", "JUMP",
                         "JUMPIFEQS", "JUMPIFNEQS"] and count == 1 \
            or self.name in ["MOVE", "INT2CHAR", "STRLEN", "TYPE", "NOT", "READ", "INT2FLOAT",
                             "FLOAT2INT"] and count == 2 \
            or self.name in ["ADD", "SUB", "MUL", "IDIV", "DIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT",
                             "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"] and count == 3:
            return
        else:
            raise XMLformatError("Error 32: Received wrong ammount of arguments in instruction "
                + self.name + "!")

    def arg_append(self, arg_type, arg_content, arg_count):
        self.arg_count = arg_count
        self.__check_corresponding_args(arg_type)
        arg_value = self.__check_arg_type(arg_type, arg_content)
        self.arg_contents.append(arg_value)
        self.arg_types.append(arg_type)

    def __check_corresponding_args(self, arg_type):
        # instruction expects var
        if self.name in ["DEFVAR", "POPS"]:
            if arg_type == "var":
                return
        # instruction expects symb
        elif self.name in ["PUSHS", "WRITE", "EXIT", "DPRINT"]:
            if arg_type in ["string", "bool", "int", "nil", "var", "float"]:
                return
        # instruction expects label
        elif self.name in ["CALL", "LABEL", "JUMP", "JUMPIFEQS", "JUMPIFNEQS"]:
            if arg_type == "label":
                return
        # instruction expects var,symb
        elif self.name in ["MOVE", "INT2CHAR", "STRLEN", "TYPE", "NOT", "INT2FLOAT", "FLOAT2INT"]:
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var", "float"] and self.arg_count == 2:
                return
        # instruction expects var, type
        elif self.name == "READ":
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type == "type" and self.arg_count == 2:
                return
        # instruction expects var,symb, symb
        elif self.name in ["ADD", "SUB", "MUL", "DIV", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT",
                           "CONCAT", "GETCHAR", "SETCHAR"]:
            if arg_type == "var" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var", "float"] and self.arg_count == 2 or \
               arg_type in ["string", "bool", "int", "nil", "var", "float"] and self.arg_count == 3:
                return
        # instruction expects label, symb, symb
        elif self.name in ["JUMPIFEQ", "JUMPIFNEQ"]:
            if arg_type == "label" and self.arg_count == 1 or\
               arg_type in ["string", "bool", "int", "nil", "var", "float"] and self.arg_count == 2 or \
               arg_type in ["string", "bool", "int", "nil", "var", "float"] and self.arg_count == 3:
                return
        # unknown instruction
        else:
            raise XMLformatError("Error 32: Received unknown instruction \"" + self.name + "\"!")
        raise XMLformatError("Error 32: Received wrong argument type for arg" + str(self.arg_count) + " in instruction "
                             + self.name + "!")

    def __check_arg_type(self, arg_type, arg_content):
        if arg_type == "type":
            if re.match('^(int|string|bool|float)$', arg_content):
                return arg_content
        elif arg_type == "var":
            if re.match('^((LF|GF|TF)@([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
                return arg_content
        elif arg_type == "label":
            if re.match('^(([a-z]|[A-Z]|[0-9]|_|-|\$|&|%|\*|!|\?)+)$', arg_content):
                return arg_content
        elif arg_type == "string":
            if re.match('^((\\\\[0-9]{3}|[^#\\\\\s])*)$', arg_content):
                arg_content = self.__transform_escape_sequences(arg_content)
                return arg_content
        elif arg_type == "int":
            if re.match('^([0-9]|-|\+)+$', arg_content):
                return int(arg_content)
        elif arg_type == "float":
            if re.match('^(|-|\+)?([0-9])*\.?([0-9])*$', arg_content):
                return float(arg_content)
            elif re.match('^(\+|-)?(0x)?([0-9]|a|b|c|d|e|f)+\.?([0-9]|a|b|c|d|e|f)*(p\+||p-|p)?([0-9])*$', arg_content):
                return float.fromhex(arg_content)
        elif arg_type == "bool":
            if re.match('^(true|false)$', arg_content):
                if arg_content == "true":
                    return True
                elif arg_content == "false":
                    return False
        elif arg_type == "nil":
            if re.match('^nil$', arg_content):
                return "nil"
        else:
            raise XMLformatError("Error 32: The arg" + str(self.arg_count) + " in instruction " +
                                 self.name +
                                 " is not valid! Unknown data type \"" + arg_type + "\"")
        raise XMLformatError("Error 32: The content of arg" + str(self.arg_count) + " in instruction " +
                             self.name + " is not valid! Got \"" + arg_content + "\"")

    def __transform_escape_sequences(self, string):
        espace_sequences = re.findall('\\\\\d{3}', string)
        if espace_sequences:
            for seq in espace_sequences:
                seq_list = list(seq)
                number = seq_list[1:]
                number = int("".join(number))
                transformed_seq = chr(number)
                string = string.replace(seq, transformed_seq)
        return string