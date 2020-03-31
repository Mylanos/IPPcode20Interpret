# -*- coding: utf-8 -*-


class Error(Exception):
    """Base class for other exceptions"""
    pass


class ArgError(Error):
    """chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů"""
    pass


class InputFileError(Error):
    """chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění)"""
    pass


class OutputFileError(Error):
    """chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění)"""
    pass


class SemanticError(Error):
    """chyba při sémantických kontrolách vstupního kódu v IPPcode20 (např. použití
    nedefino- vaného návěští, redefinice proměnné"""
    pass


class WrongOperandsError(Error):
    """běhová chyba interpretace – špatné typy operandů;"""
    pass


class NonexistantVariableAccessError(Error):
    """běhová chyba interpretace – přístup k neexistující proměnné (rámec existuje);"""
    pass

