"""
This module is a part of CSVEdit.
It contains auxiliary classes that hold various information that is used by the editor.
"""
import tables
import curses

QUOTING_INDICATORS = ['M', 'A', 'L', 'N']

class Key:
    def __init__(self, representation: str, key_code: int, *args):
        self.code = key_code
        self.text = f"[{representation}]"
        self.all_codes = [key_code] + list(args)

KEY_Q = Key('q', ord('q'))
KEY_SQ = Key('Q', ord('Q'))
KEY_S = Key('s', ord('s'))
KEY_SS = Key('S', ord('S'))
KEY_X = Key('x', ord('x'))
KEY_SX = Key('X', ord('X'))
KEY_Z = Key('z', ord('z'))
KEY_SZ = Key('Z', ord('Z'))
KEY_C = Key('c', ord('c'))
KEY_SC = Key('C', ord('C'))
KEY_V = Key('v', ord('v'))
KEY_SV = Key('V', ord('V'))

KEY_ESC = Key('Esc', 27)
KEY_ENTER = Key('Enter', curses.KEY_ENTER, 13, 10)
KEY_ALT = Key('Alt', 27)
KEY_DELETE = Key('Delete', curses.KEY_DC)
KEY_HOME = Key('Home', curses.KEY_HOME, curses.KEY_SHOME)
KEY_END = Key('End', curses.KEY_END, curses.KEY_SEND)
KEY_PGUP = Key('PgUp', curses.KEY_PPAGE)
KEY_PGDN = Key('PgDn', curses.KEY_NPAGE)
KEY_F1 = Key('F1', curses.KEY_F1)
KEY_F5 = Key('F5', curses.KEY_F5)

class Pointer:
    """
    A class that defines a pointer for the interface.
    It has its own coordinates and methods of moving.
    """
    def __init__(self, column_number, row):
        # Creates a pointer with set coordinates
        self.column_number = column_number
        self.row = row
        self.update_column()

    def update_column(self):
        """Updates the column letter"""
        self.column = tables.get_column(self.column_number)

    def right(self):
        """Moves the pointer one column right"""
        self.column_number += 1
        self.update_column()

    def left(self):
        """Moves the pointer one column left"""
        self.column_number -= 1
        self.update_column()

    def down(self):
        """Moves the pointer one row down"""
        self.row += 1

    def up(self):
        """Moves the pointer one row up"""
        self.row -= 1

class Info:
    """
    A class that holds information about the interface:
    - message that is currently being displayed
    - text of the default mesasge
    - current mode of the editor
    - alert symbol
    """
    def __init__(self, default_message: str = None):
        self.default_message = default_message
        self.message = self.default_message
        self.mode = 'R'
        self.show_mode = True
        self.alert = None

    def set_alert(self, alert_sign: str, new_message: str):
        """Sets the alert symbol message."""
        self.alert = alert_sign
        self.message = new_message
        self.show_mode = False

    def reset_alert(self):
        """Resets the alert symbol and message to default values."""
        self.alert = None
        self.message = self.default_message
        self.show_mode = True

    def set_message(self, new_message: str, show_mode: bool):
        """Sets the message to be displayed."""
        self.message = new_message
        self.show_mode = show_mode

    def reset_messsage(self):
        """Resets the message the default value."""
        self.message = self.default_message
        self.show_mode = True
