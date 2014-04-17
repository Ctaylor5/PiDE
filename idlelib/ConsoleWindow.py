from Tkinter import *
#from idlelib.EditorWindow import EditorWindow
from idlelib.OutputWindow import OutputWindow
import re
import tkMessageBox
from idlelib import IOBinding

class ConsoleWindow(OutputWindow):

    """An editor window that can serve as an output file.

    Also the future base class for the Python shell window.
    This class has no input facilities.
    """

    def __init__(self, *args):
        OutputWindow.__init__(self, *args)
        self.text.bind("<<goto-file-line>>", self.goto_file_line)