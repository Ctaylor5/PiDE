from Tkinter import *
from idlelib.EditorWindow import EditorWindow
import re
import tkMessageBox
from idlelib import IOBinding
from idlelib.configHandler import idleConf



class OutputWindow(EditorWindow):

    """An editor window that can serve as an output file.

    Also the future base class for the Python shell window.
    This class has no input facilities.
    """

    def __init__(self, *args):
        EditorWindow.__init__(self, *args)
        self.text.bind("<<goto-file-line>>", self.goto_file_line)

    # Customize EditorWindow

    # No colorization needed
    def ispythonsource(self, filename):
        return 0

    def short_title(self):
        return "Output"

    def maybesave(self):
        # Override base class method -- don't ask any questions
        if self.get_saved():
            return "yes"
        else:
            return "no"

    # Act as output file

    def write(self, s, tags=(), mark="insert"):
        # Tk assumes that byte strings are Latin-1;
        # we assume that they are in the locale's encoding
        if isinstance(s, str):
            try:
                s = unicode(s, IOBinding.encoding)
            except UnicodeError:
                # some other encoding; let Tcl deal with it
                pass
        self.text.insert(mark, s, tags)
        #self.vis_text.insert("insert", s, tags)
        self.text.see(mark)
        self.text.update()       
        
        #self.vis_text.see(mark)
        #self.vis_text.update()

    def vis_write(self, s, tags=(), mark="insert"):
        # Tk assumes that byte strings are Latin-1;
        # we assume that they are in the locale's encoding
        if isinstance(s, str):
            try:
                s = unicode(s, IOBinding.encoding)
            except UnicodeError:
                # some other encoding; let Tcl deal with it
                pass

        self.vis_text.config(state=NORMAL)        
        self.vis_text.insert("insert",s)
        self.vis_text.see("insert")
        self.vis_text.update()
        self.vis_text.config(state=DISABLED)

        #self.vis_text.insert("insert", s, tags)
        #self.vis_text.update()

    def console_write(self, s, tags=(), mark="insert"):
        # Tk assumes that byte strings are Latin-1;
        # we assume that they are in the locale's encoding
        if isinstance(s, str):
            try:
                s = unicode(s, IOBinding.encoding)
            except UnicodeError:
                # some other encoding; let Tcl deal with it
                pass
        if 'stderr' in tags:
            self.check_err(s, tags, mark)
        else:
            self.console_text.config(state=NORMAL)
            self.console_text.insert(END,s,tags)
            self.console_text.see(END)
            self.console_text.update()
            self.console_text.config(state=DISABLED) 
 

    def check_err(self, s, tags=(), mark="insert"):
        if("NameError: name ") in s and (" is not defined") in s:
            s += "\tThe variable you were trying to use is undefined. You must define it first.\n\t\tExample: x = 4\n-------------------------------------------------------------------------------\n"
        if("SyntaxError: invalid syntax") in s:
            s += "\tThere seems to be a problem with your syntax. Check the highlighted section to see what you did wrong.\n\t\tIf something is highlighted, you have typed something invalid. If there is highlighting after what you typed,\n\t\tthen the syntax is incomplete.------------\n"
        if("TypeError: unsupported operand type(s) for") in s:
            s += "\tYou cannot perform this operation on these data types. Change the data type.\n-------------\n"
        if("ZeroDivisionError:") in s:
            s += "\tDividing by zero will end the universe. So we can't allow you to do that.\n--------------\n"
        if("KeyboardInterrupt") in s:
            s += "\tYour program stopped manually.----------------\n"
        if("SyntaxError: EOL while scanning string literal") in s:
            s += "\tDon't forget to put double quotes on both sides when you are working with a string.\n\t\tSee the highighted code for reference as to where you forgot to add the quotation mark.\n\t\t\tExample: \"your text here\"\n-------------------------------------------------------------------------------\n"
        if("IndentationError:") in s:
            s += "\tCheck the way you indented. Remember that the indentation only increases after a statement ending with a : colon, and afterwards must return to the previous indentation.\n------------\n"
        if("TypeError: range() integer end argument expected, got list.") in s:
            s += "\tThe range() method can only be used on an integer value, not a list. Must pass an integer value.\n--------------\n"
        if("TypeError: range() integer end argument expected, got str.") in s:
            s += "\tThe range() method can only be used on an integer value, not a string. Must pass an integer value.\n--------------\n"
        if("IndexError: list index out of range") in s:
            s += "\tYour list doesn't have enough items. Your index value is greater than the length of the list. Check the value of the index for your list.\n-------------\n"
        if("IndexError: tuple index out of range") in s:
            s += "\tYour tuple doesn't have enough items. Your index value is greater than the length of the tuple. Check the value of the index for your tuple.\n-------------\n"
        if("TypeError: 'tuple' object is not callable") in s:
            s += "\tYou cannot get a value of a tuple at a specific index. If you wish to do that, you must create a list.\n------------\n"
        if("TypeError: 'str' object does not support item assignment") in s:
            s += "\tYou cannot perform this assignment for strings. use another way to assign this value to your string\n--------------\n"
        if("TypeError: cannot concatenate 'str' and 'int' objects") in s:
            s += "\tYou cannot combine a string with an integer value. You must convert the integer value to a string first & try again.\n\t\tYou can use this format to combine those values into a string: \str%%s %% int\n\t\t\tBut be careful to put quotes when the string you want to add something to is not a variable.\n-------------\n"
        if("AttributeError: 'str' object has no attribute") in s:
            s += "\tYou cannot do this for a string value. Check the spelling of the attribute.\n" + "-----------\n"
        if("AttributeError: 'int' object has no attribute") in s:
            s += "\tYou cannot do this for an integer value. Check the spelling of the attribute.\n" + "-----------\n"

        else:
            self.console_text.config(state=NORMAL)
            self.console_text.insert(END,s,tags)
            self.console_text.see(END)
            self.console_text.update()
            self.console_text.config(state=DISABLED) 


    def is_error(self, s):
        if "SyntaxError: " in s:
            return True
        else:
            return False

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        pass

    # Our own right-button menu

    rmenu_specs = [
        ("Cut", "<<cut>>", "rmenu_check_cut"),
        ("Copy", "<<copy>>", "rmenu_check_copy"),
        ("Paste", "<<paste>>", "rmenu_check_paste"),
        (None, None, None),
        ("Go to file/line", "<<goto-file-line>>", None),
    ]

    file_line_pats = [
        # order of patterns matters
        r'file "([^"]*)", line (\d+)',
        r'([^\s]+)\((\d+)\)',
        r'^(\s*\S.*?):\s*(\d+):',  # Win filename, maybe starting with spaces
        r'([^\s]+):\s*(\d+):',     # filename or path, ltrim
        r'^\s*(\S.*?):\s*(\d+):',  # Win abs path with embedded spaces, ltrim
    ]

    file_line_progs = None

    def goto_file_line(self, event=None):
        if self.file_line_progs is None:
            l = []
            for pat in self.file_line_pats:
                l.append(re.compile(pat, re.IGNORECASE))
            self.file_line_progs = l
        # x, y = self.event.x, self.event.y
        # self.text.mark_set("insert", "@%d,%d" % (x, y))
        line = self.text.get("insert linestart", "insert lineend")
        result = self._file_line_helper(line)
        if not result:
            # Try the previous line.  This is handy e.g. in tracebacks,
            # where you tend to right-click on the displayed source line
            line = self.text.get("insert -1line linestart",
                                 "insert -1line lineend")
            result = self._file_line_helper(line)
            if not result:
                tkMessageBox.showerror(
                    "No special line",
                    "The line you point at doesn't look like "
                    "a valid file name followed by a line number.",
                    master=self.text)
                return
        filename, lineno = result
        edit = self.flist.open(filename)
        edit.gotoline(lineno)

    def _file_line_helper(self, line):
        for prog in self.file_line_progs:
            match = prog.search(line)
            if match:
                filename, lineno = match.group(1, 2)
                try:
                    f = open(filename, "r")
                    f.close()
                    break
                except IOError:
                    continue
        else:
            return None
        try:
            return filename, int(lineno)
        except TypeError:
            return None

# These classes are currently not used but might come in handy

class OnDemandOutputWindow:

    tagdefs = {
        # XXX Should use IdlePrefs.ColorPrefs
        "stdout":  {"foreground": "blue"},
        "stderr":  {"foreground": "#007700"},
    }

    def __init__(self, flist):
        self.flist = flist
        self.owin = None

    def write(self, s, tags, mark):
        if not self.owin:
            self.setup()
        self.owin.write(s, tags, mark)

    def setup(self):
        self.owin = owin = OutputWindow(self.flist)
        text = owin.text
        for tag, cnf in self.tagdefs.items():
            if cnf:
                text.tag_configure(tag, **cnf)
        text.tag_raise('sel')
        self.write = self.owin.write
