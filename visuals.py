import tables

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
