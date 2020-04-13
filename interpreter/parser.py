# -*- coding: utf-8 -*-

##################################################
 # Soubor: parser.py
 # Projekt - Interpret of IPPcode20's XML representation
 # Autor: Marek Ziska, xziska03@stud.fit.vutbr.cz
 # Skupina: 2BIB
 # Datum 14.04.2020
##################################################

import xml.etree.ElementTree as Et
from myerrors import *
from instruction import Instruction
import sys


class Parser:
    def __init__(self, filexml):
        """
        Args:
            filexml: source file
        """
        try:
            self.tree = Et.parse(filexml)
            self.root = self.tree.getroot()
            self.instr_list = []
            self.instr_count = 0
        except FileNotFoundError:
            print("Error 10: No such file or directory! (" + filexml + ")", file=sys.stderr)
            sys.exit(11)
        except Exception:
            print("Error 31: There was an error while parsing the XML file! (" + filexml + ")", file=sys.stderr)
            sys.exit(31)

    def parse(self):
        try:
            self.__check_header()
            self.__parse_instructions()
        except XMLformatError as XMLfE:
            print(XMLfE.get_msg(), file=sys.stderr)
            sys.exit(32)
        except ValueError:
            print("lmfao error", file=sys.stderr)
            sys.exit(32)

    def __check_header(self):
        """ checks for mistakes in program element
        """
        if self.root.tag != "program":
            raise XMLformatError("Error 32: The root tag of XML file was not valid! \"Program\" "
                                 "expected, got " + self.root.tag)
        if "language" not in self.root.attrib:
            raise XMLformatError("Error 32: The root attributes of XML file are not valid!")
        if self.root.attrib.get("language") != "IPPcode20":
            raise XMLformatError("Error 32: The root language attribute is not valid!")

    def __parse_instructions(self):
        """ parses instructions from source XML file
        """
        # cycle over childs of root element
        for instruct in self.root:
            if instruct.tag != "instruction":
                raise XMLformatError("Error 32: The instruction tag (order" + str(self.instr_count) +
                                     ") in XML file is not valid! ")
            if "order" in instruct.attrib:
                if int(instruct.attrib.get("order")) <= self.instr_count:
                    raise XMLformatError("Error 32: The counter in instruction(order" + str(self.instr_count) +
                                         ") is not valid! ")
                else:
                    self.instr_count = int(instruct.attrib.get("order"))
            else:
                raise XMLformatError("Error 32: The order attribute in instruction(order" + str(self.instr_count) +
                                     ") was not found! ")
            if "opcode" in instruct.attrib:
                instruction_name = instruct.attrib.get("opcode")
                # valid format of instruction element -> new instance of Instruction class
                instruction = Instruction(instruction_name)
                if not list(instruct):
                    instruction.check_inst_without_args()
                else:
                    arg_count = 1
                    argument_list = []
                    argument_order = []
                    # cycle over childs(args) of instruction element and sort them by order
                    for arg in instruct:
                        # arguments cant have more childs
                        for subchild in arg:
                            raise XMLformatError("Error 32: The argument has child elements!")
                        tag_list = list(arg.tag)
                        arg_order = tag_list[-1]
                        if arg_order not in ["1", "2", "3"]:
                            raise XMLformatError("Error 32: The tag in argument(" + arg.tag + ") is not valid! ")
                        else:
                            if not argument_list:
                                argument_list.append(arg)
                            else:
                                if int(arg_order) < argument_order[-1]:
                                    argument_list.insert(0, arg)
                                elif int(arg_order) > argument_order[-1]:
                                    argument_list.insert(len(argument_list), arg)
                                else:
                                    raise XMLformatError("Error 32: The tag in argument (" + arg.tag + ") "
                                                         "is not valid! Duplicated argument")
                            argument_order.append(int(arg_order))
                    # cycle over childs(args) of instruction element and store them
                    for argument in argument_list:
                        if argument.tag != ("arg" + str(arg_count)):
                            raise XMLformatError("Error 32: The " + str(arg_count) + ". argument tag in"
                                                 + str(self.instr_count) + ". instruction is not valid! ")
                        if "type" in argument.attrib:
                            arg_type = argument.attrib.get("type")
                            arg_content = argument.text
                            if arg_content is None:
                                arg_content = ""
                            instruction.arg_append(arg_type, arg_content, arg_count)
                        else:
                            raise XMLformatError("Error 32: The " + str(arg_count) + ". argument tag in"
                                                 + str(self.instr_count) + ". instruction is not valid! ")
                        arg_count += 1
                    instruction.check_argument_count(arg_count - 1)
                self.instr_list.append(instruction)
            else:
                raise XMLformatError("Error 32: The opcode attribute in " + str(self.instr_count) +
                                     ". instruction was not found! ")






