# -*- coding: utf-8 -*-

##################################################
 # Soubor: frame.py
 # Projekt - Interpret of IPPcode20's XML representation
 # Autor: Marek Ziska, xziska03@stud.fit.vutbr.cz
 # Skupina: 2BIB
 # Datum 14.04.2020
##################################################

from myerrors import *


class Frame:
    """ Class represents frame of one context in interpreted program
    """
    def __init__(self):
        self.variables = {}
        self.types = {}

    def define_variable(self, name):
        """ Defines variable
        Args:
            name: Variable to be defined
        """
        if name in self.variables:
            raise SemanticError("Error 52: Redefinition of variable!")
        self.variables[name] = None
        self.types[name] = None

    def update_variable(self, name, value, var_type):
        """ Updates value and type of defined variable
        Args:
            name: Variable to be initialized/updated
            value: Initializing/updating value
            var_type: Type of assigned value
        """
        if name not in self.variables:
            raise AccesingAbsentVariableError("Error 54: Trying to access undefined variable!")
        self.variables[name] = value
        self.types[name] = var_type

    def get_type_and_value(self, name, type_exception):
        """ Returns value and type of variable
        Args:
            name: Desired variable
            type_exception: TYPE flag, returning None in all instructions except TYPE causes error

        :return type and value of variable
        """
        if name in self.variables:
            if self.variables[name] is None and not type_exception:
                raise MissingValueError("Error 56: Missing value!")
            return self.types[name], self.variables[name]
        else:
            raise AccesingAbsentVariableError("Error 54: Trying to access undefined variable!")
