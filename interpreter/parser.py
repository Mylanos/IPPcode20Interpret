
import xml.etree.ElementTree as Et
from myerrors import *
from instruction import Instruction
import sys


class Parser:

    def __init__(self, filexml):
        try:
            self.tree = Et.parse(filexml)
            self.root = self.tree.getroot()
            self.instr_list = []
            self.instr_count = 1
        except FileNotFoundError:
            print("Error 10: No such file or directory! (" + filexml + ")")
            sys.exit(11)
        except Exception:
            print("Error 31: There was an error while parsing the XML file! (" + filexml + ")")
            sys.exit(31)

    def parse(self):
        try:
            self.__check_header()
            self.__parse_instructions()
        except XMLformatError as XMLfE:
            print(XMLfE.get_msg())
            sys.exit(32)

    def __check_header(self):
        if self.root.tag != "program":
            raise XMLformatError("Error 32: The root tag of XML file was not valid! \"Program\" "
                                 "expected, got " + self.root.tag)
        if self.root.attrib != {'language': 'IPPcode20'}:
            raise XMLformatError("Error 32: The root attributes of XML file are not valid!")

    def __parse_instructions(self):
        for instruct in self.root:
            arg_count = 1
            if instruct.tag != "instruction":
                raise XMLformatError("Error 32: The instruction tag (order" + str(self.instr_count) +
                                     ") in XML file is not valid! ")
            if "order" in instruct.attrib:
                if instruct.attrib.get("order") != str(self.instr_count):
                    raise XMLformatError("Error 32: The counter in instruction(order" + str(self.instr_count) +
                                         ") is not valid! ")
            else:
                raise XMLformatError("Error 32: The order attribute in instruction(order" + str(self.instr_count) +
                                     ") was not found! ")
            if "opcode" in instruct.attrib:
                instruction_name = instruct.attrib.get("opcode").upper()
                instruction = Instruction(instruction_name)
                if not list(instruct):
                    instruction.check_inst_without_args()
                else:
                    for argument in instruct:
                        if argument.tag != ("arg" + str(arg_count)):
                            raise XMLformatError("Error 32: The argument(" + str(arg_count) + ") tag in instruction"
                                                 "(order" + str(self.instr_count) +
                                                 ") is not valid! ")
                        if "type" in argument.attrib:
                            arg_type = argument.attrib.get("type")
                            arg_content = argument.text
                            if arg_content is None:
                                arg_content = ""
                            instruction.arg_append(arg_type, arg_content, arg_count)
                        else:
                            raise XMLformatError("Error 32: The argument(" + str(arg_count) + ") attribute in instruction"
                                                 "(order" + str(self.instr_count) + ") is not valid! ")
                        arg_count += 1
                self.instr_list.append(instruction)
            else:
                raise XMLformatError("Error 32: The opcode attribute in instruction (order" + str(self.instr_count) +
                                     ") was not found! ")

            self.instr_count += 1







