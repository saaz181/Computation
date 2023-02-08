class AutomatonException(Exception):
    """The base class for all automaton-related errors."""

    pass


class InfiniteLanguageException(AutomatonException):
    """The operation cannot be performed because the language is infinite"""
    pass


class EmptyLanguageException(AutomatonException):
    """ The language is empty"""
    pass


class InfiniteFiniteException(AutomatonException):
    """The Language of DFA is finite,but it accepts infinite words"""
    pass


class SymbolMisMatchException(AutomatonException):
    """In Product of 2 DFAs if input symbols are not equal"""
    pass

class ElementNotInTable(Exception):
    """if an element is not in table"""
    pass


class StackRegexException(Exception):
    """The Processing Stack is empty"""
    pass