# -*- coding: utf-8 -*-


class Error(Exception):
    def __init__(self, message):
        self.code = 99
        self.message = message

    def err_code(self):
        return self.code
    """Base class for other exceptions"""

    def get_msg(self):
        return self.message


class InternalError(Error):
    """chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů"""
    def __init__(self, message):
        self.code = 99
        self.message = message


class ArgError(Error):
    """chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů"""
    def __init__(self, message):
        self.code = 10
        self.message = message


class XMLformatError(Error):
    """chybný XML formát ve vstupním souboru (soubor není tzv. dobře formátovaný, angl. well-formed"""
    def __init__(self, message):
        self.code = 31
        self.message = message


class XMLstructureError(Error):
    """
        neočekávaná struktura XML (např. element pro argument mimo element pro instrukci, instrukce s
        duplicitním pořadím nebo záporným pořadím) či lexikální nebo syntaktická chyba textových elementů a
        atributů ve vstupním XML souboru (např. chybný lexém pro řetězcový literál, neznámý operační kód
        apod
    """
    def __init__(self, message):
        self.code = 32
        self.message = message


class SemanticError(Error):
    """chyba při sémantických kontrolách vstupního kódu v IPPcode20 (např. použití
    nedefino- vaného návěští, redefinice proměnné"""
    def __init__(self, message):
        self.code = 52
        self.message = message


class WrongOperandsError(Error):
    """běhová chyba interpretace – špatné typy operandů;"""
    def __init__(self, message):
        self.code = 53
        self.message = message


class AccesingAbsentVariableError(Error):
    """běhová chyba interpretace – přístup k neexistující proměnné (rámec existuje);"""
    def __init__(self, message):
        self.code = 54
        self.message = message


class FrameDoesntExistError(Error):
    """ rámec neexistuje (např. čtení z prázdného zásobníku rámců)"""
    def __init__(self, message):
        self.code = 55
        self.message = message


class MissingValueError(Error):
    """chybějící hodnota (v proměnné, na datovém zásobníku, nebo v zásobníku volání)"""
    def __init__(self, message):
        self.code = 56
        self.message = message


class OperandsValueError(Error):
    """špatná hodnota operandu (např. dělení nulou, špatná návra- tová hodnota instrukce EXIT)"""
    def __init__(self, message):
        self.code = 57
        self.message = message


class StringOperationError(Error):
    """špatná hodnota operandu (např. dělení nulou, špatná návra- tová hodnota instrukce EXIT)"""
    def __init__(self, message):
        self.code = 58
        self.message = message