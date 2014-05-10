import os
import bdb
import types
import string
from parse import *
from Tkinter import *
from idlelib.WindowList import ListedToplevel
from idlelib.ScrolledList import ScrolledList
from idlelib import macosxSupport
from Entries import *




class VIdb(bdb.Bdb):

    def __init__(self, gui):
        self.gui = gui
        bdb.Bdb.__init__(self)

    def run(self, cmd, globals=None, locals=None):
        print "Vidb Run"
        if globals is None:
            import __main__
            globals = __main__.__dict__
        if locals is None:
            locals = globals
        self.reset()
        sys.settrace(self.trace_dispatch)
        if not isinstance(cmd, types.CodeType):
            cmd = cmd+'\n'
        try:
            exec cmd in globals, locals
        except bdb.BdbQuit:
            pass
        finally:
            self.quitting = 1
            sys.settrace(None)
            # self.set_continue()

    def user_line(self, frame):
        if self.in_rpc_code(frame):
            self.set_step()
            return
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame)

    def user_exception(self, frame, info):
        if self.in_rpc_code(frame):
            self.set_step()
            return
        message = self.__frame2message(frame)
        self.gui.interaction(message, frame, info)

    def in_rpc_code(self, frame):
        if frame.f_code.co_filename.count('rpc.py'):
            return True
        else:
            prev_frame = frame.f_back
            if prev_frame.f_code.co_filename.count('Debugger.py'):
                # (that test will catch both Debugger.py and RemoteDebugger.py)
                return False
            return self.in_rpc_code(prev_frame)

    def __frame2message(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        basename = os.path.basename(filename)
        message = "%s:%s" % (basename, lineno)
        if code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)
        return message


class Vis_Debugger:

    vstack = vsource = vlocals = vglobals = None

    def __init__(self, pyshell, idb=None):
        if idb is None:
            idb = VIdb(self)
        self.pyshell = pyshell
        self.idb = idb
        self.frame = None
        self.Entries = Entries(pyshell)
        self.eid = 0
        #pyshell = self.pyshell
        self.make_gui()
        self.interacting = 0
        


    def handleEntry(self, line):
        thisEntry = self.toEntry(self.eid,line)
        if thisEntry != None:
            if(self.Entries.length()==0):
                self.Entries.add(thisEntry)
                self.eid = self.eid + 1
            else:
                if(self.eid<self.Entries.length()):
                    print "Adding to block 1"
                    self.Entries.get(self.eid).append(thisEntry)
                else:
                    if thisEntry.style == "Variable":
                        if self.Entries.hasVar(thisEntry.name):
                            pass
                        else:
                            self.Entries.add(thisEntry)
                            self.eid = self.eid + 1
                    elif thisEntry.style != "Entry":
                        self.Entries.add(thisEntry)
                        self.eid = self.eid + 1
        else:
            print "WHELP!"

        
    def toEntry(self, eid, line):
        thisEntry = Entry(eid, line, self.pyshell)
        if line.find('for')>-1:
            print "FOOUR!!", eid
            thisEntry = For_Entry(eid, line, self.pyshell)          
        elif line.find('if')>-1:
            thisEntry = If_Entry(eid, line, self.pyshell)
        elif line.find('while')>-1:
            thisEntry = While_Entry(eid, line, self.pyshell)
        elif line.find('=')>-1:
            thisEntry = Var_Entry(eid, line, self.pyshell)
        return thisEntry

    def run(self, *args):
        try:
            args
            self.interacting = 1
            return self.idb.run(*args)
        finally:
            self.interacting = 0

    def close(self, event=None):
        if self.interacting:
            self.top.bell()
            return
        if self.stackviewer:
            self.stackviewer.close(); self.stackviewer = None
        # Clean up pyshell if user clicked debugger control close widget.
        # (Causes a harmless extra cycle through close_debugger() if user
        # toggled debugger from pyshell Debug menu)
        self.pyshell.close_debugger()
        # Now close the debugger control window....
        self.top.destroy()

    def make_gui(self):
        pyshell = self.pyshell
        self.flist = pyshell.flist
        self.root = root = pyshell.root
        self.top = top = ListedToplevel(root)
        #self.top.wm_title("Debug Control")
        #self.top.wm_iconname("Debug")
        top.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<Escape>", self.close)
        #        
        self.bframe = bframe = Frame(top, visual=False)
        self.bframe.pack(anchor="w")
        self.buttons = bl = []
        #
        self.bcont = b = Button(bframe, text="Go", command=self.cont)
        bl.append(b)
        self.bstep = b = Button(bframe, text="Step", command=self.step)
        bl.append(b)
        self.bnext = b = Button(bframe, text="Over", command=self.next)
        bl.append(b)
        self.bret = b = Button(bframe, text="Out", command=self.ret)
        bl.append(b)
        self.bret = b = Button(bframe, text="Quit", command=self.quit)
        bl.append(b)
        #
        for b in bl:
            b.configure(state="disabled")
            b.pack(side="left")
        #
        self.cframe = cframe = Frame(bframe)
        #self.cframe.pack(side="left")
        #
        if not self.vstack:
            self.__class__.vstack = BooleanVar(top)
            self.vstack.set(1)
        self.bstack = Checkbutton(cframe,
            text="Stack", command=self.show_stack, variable=self.vstack)
        self.bstack.grid(row=0, column=0)
        if not self.vsource:
            self.__class__.vsource = BooleanVar(top)
        self.bsource = Checkbutton(cframe,
            text="Source", command=self.show_source, variable=self.vsource)
        self.bsource.grid(row=0, column=1)
        if not self.vlocals:
            self.__class__.vlocals = BooleanVar(top)
            self.vlocals.set(1)
        self.blocals = Checkbutton(cframe,
            text="Locals", command=self.show_locals, variable=self.vlocals)
        self.blocals.grid(row=1, column=0)
        if not self.vglobals:
            self.__class__.vglobals = BooleanVar(top)
        self.bglobals = Checkbutton(cframe,
            text="Globals", command=self.show_globals, variable=self.vglobals)
        self.bglobals.grid(row=1, column=1)
        #
        self.status = Label(top, anchor="w")
        #self.status.pack(anchor="w")
        self.error = Label(top, anchor="w")
        #self.error.pack(anchor="w", fill="x")
        self.errorbg = self.error.cget("background")
        #
        self.fstack = Frame(top, height=1)
        #self.fstack.pack(expand=1, fill="both")
        self.flocals = Frame(top)
        #self.flocals.pack(expand=1, fill="both")
        self.fglobals = Frame(top, height=1)
        #self.fglobals.pack(expand=1, fill="both")
        #
        top.withdraw()
        if self.vstack.get():
            self.show_stack()
        if self.vlocals.get():
            self.show_locals()
        if self.vglobals.get():
            self.show_globals()

    def interaction(self, message, frame, info=None):
        self.frame = frame
        self.status.configure(text=message)
        #
        if info:
            type, value, tb = info
            try:
                m1 = type.__name__
            except AttributeError:
                m1 = "%s" % str(type)
            if value is not None:
                try:
                    m1 = "%s: %s" % (m1, str(value))
                except:
                    pass
            bg = "yellow"
        else:
            m1 = ""
            tb = None
            bg = self.errorbg
        self.error.configure(text=m1, background=bg)
        #
        sv = self.stackviewer
        if sv:
            stack, i = self.idb.get_stack(self.frame, tb)
            sv.load_stack(stack, i)
        #HERE!!
        #if(self.eid==0):
            #self.show_variables(1)
        #self.update_entry(self.current_Entry)
        #
        if self.vsource.get():
            self.sync_source_line()
        #
        for b in self.buttons:
            b.configure(state="normal")
        #
        print "C I 1"
        #self.top.wakeup()
        print "EID "+str(self.eid)

        if (self.Entries.get(self.eid-1)!=-1):
            if(self.Entries.get(self.eid-1).style=="Variable"):
                print "Continuing IN"
                self.show_variables(1)
                self.step()                
            else:
                print "Stepping through"
                #self.show_Entry(self.Entries.Controls)
                self.show_variables(1)
                self.next()
        else:
            print "Continuing Out"
            self.cont()
        #self.root.mainloop()
        print "C I 2"
        #self.step()
        print "C I 3"
        #
        for b in self.buttons:
            b.configure(state="disabled")
        self.status.configure(text="")
        self.error.configure(text="", background=self.errorbg)
        self.frame = None
        print "C I End"
        


    def sync_source_line(self):
        frame = self.frame
        if not frame:
            return
        filename, lineno = self.__frame2fileline(frame)
        if filename[:1] + filename[-1:] != "<>" and os.path.exists(filename):
            self.flist.gotofileline(filename, lineno)

    def __frame2fileline(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        return filename, lineno

    def cont(self):
        self.idb.set_continue()
        self.root.quit()

    def step(self):
        self.idb.set_step()
        self.root.quit()

    def next(self):
        self.idb.set_next(self.frame)
        self.root.quit()

    def ret(self):
        self.idb.set_return(self.frame)
        self.root.quit()

    def quit(self):
        self.idb.set_quit()
        self.root.quit()

    stackviewer = None

    def show_stack(self):
        if not self.stackviewer and self.vstack.get():
            self.stackviewer = sv = StackViewer(self.fstack, self.flist, self)
            if self.frame:
                stack, i = self.idb.get_stack(self.frame, None)
                sv.load_stack(stack, i)
        else:
            sv = self.stackviewer
            if sv and not self.vstack.get():
                self.stackviewer = None
                sv.close()
            self.fstack['height'] = 1

    def show_source(self):
        if self.vsource.get():
            self.sync_source_line()

    def show_frame(self, (frame, lineno)):
        self.frame = frame
        self.show_variables()

    localsviewer = None
    globalsviewer = None

    def show_locals(self):
        lv = self.localsviewer
        if self.vlocals.get():
            if not lv:
                self.localsviewer = NamespaceViewer(self.flocals, "Locals")
        else:
            if lv:
                self.localsviewer = None
                lv.close()
                self.flocals['height'] = 1
        self.show_variables()

    def show_globals(self):
        gv = self.globalsviewer
        if self.vglobals.get():
            if not gv:
                self.globalsviewer = NamespaceViewer(self.fglobals, "Globals")
        else:
            if gv:
                self.globalsviewer = None
                gv.close()
                self.fglobals['height'] = 1
        self.show_variables()


    def show_Entry(self, Entries):
        lv = self.localsviewer
        frame = self.frame
        if not frame:
            ldict = gdict = None
        else:
            ldict = frame.f_locals
            gdict = frame.f_globals
            if lv and ldict is gdict:
                ldict = None
        if lv:
            lv.load_dict(ldict, Entries, 1, self.pyshell.interp.rpcclt)
        

    def show_variables(self, force=0):
        lv = self.localsviewer
        gv = self.globalsviewer
        frame = self.frame
        if not frame:
            #print "sv1"
            ldict = gdict = None
        else:
            #print "sv2"
            ldict = frame.f_locals
            gdict = frame.f_globals
            if lv and gv and ldict is gdict:
                ldict = None
        if lv:
            lv.load_dict(ldict, self.Entries, force, self.pyshell.interp.rpcclt)
        if gv:
            gv.load_dict(gdict, self.Entries, force, self.pyshell.interp.rpcclt)
        

    def set_breakpoint_here(self, filename, lineno):
        self.idb.set_break(filename, lineno)

    def clear_breakpoint_here(self, filename, lineno):
        self.idb.clear_break(filename, lineno)

    def clear_file_breaks(self, filename):
        self.idb.clear_all_file_breaks(filename)

    def load_breakpoints(self):
        "Load PyShellEditorWindow breakpoints into subprocess debugger"
        pyshell_edit_windows = self.pyshell.flist.inversedict.keys()
        for editwin in pyshell_edit_windows:
            filename = editwin.io.filename
            try:
                for lineno in editwin.breakpoints:
                    self.set_breakpoint_here(filename, lineno)
            except AttributeError:
                continue

class StackViewer(ScrolledList):

    def __init__(self, master, flist, gui):
        if macosxSupport.runningAsOSXApp():
            # At least on with the stock AquaTk version on OSX 10.4 you'll
            # get an shaking GUI that eventually kills IDLE if the width
            # argument is specified.
            ScrolledList.__init__(self, master)
        else:
            ScrolledList.__init__(self, master, width=80)
        self.flist = flist
        self.gui = gui
        self.stack = []

    def load_stack(self, stack, index=None):
        self.stack = stack
        self.clear()
        for i in range(len(stack)):
            frame, lineno = stack[i]
            try:
                modname = frame.f_globals["__name__"]
            except:
                modname = "?"
            code = frame.f_code
            filename = code.co_filename
            funcname = code.co_name
            import linecache
            sourceline = linecache.getline(filename, lineno)
            import string
            sourceline = string.strip(sourceline)
            if funcname in ("?", "", None):
                item = "%s, line %d: %s" % (modname, lineno, sourceline)
            else:
                item = "%s.%s(), line %d: %s" % (modname, funcname,
                                                 lineno, sourceline)
            if i == index:
                item = "> " + item
            self.append(item)
        if index is not None:
            self.select(index)

    def popup_event(self, event):
        "override base method"
        if self.stack:
            return ScrolledList.popup_event(self, event)

    def fill_menu(self):
        "override base method"
        menu = self.menu
        menu.add_command(label="Go to source line",
                         command=self.goto_source_line)
        menu.add_command(label="Show stack frame",
                         command=self.show_stack_frame)

    def on_select(self, index):
        "override base method"
        if 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    def on_double(self, index):
        "override base method"
        self.show_source(index)

    def goto_source_line(self):
        index = self.listbox.index("active")
        self.show_source(index)

    def show_stack_frame(self):
        index = self.listbox.index("active")
        if 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])

    def show_source(self, index):
        if not (0 <= index < len(self.stack)):
            return
        frame, lineno = self.stack[index]
        code = frame.f_code
        filename = code.co_filename
        if os.path.isfile(filename):
            edit = self.flist.open(filename)
            if edit:
                edit.gotoline(lineno)


class NamespaceViewer:

    def __init__(self, master, title, dict=None):
        width = 0
        height = 40
        self.loadCount = 1        
        self.loopCounter = 1
        if dict:
            height = 20*len(dict) # XXX 20 == observed height of Entry widget
        self.master = master
        self.title = title
        import repr
        self.repr = repr.Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.frame = frame = Frame(master)
        self.frame.pack(expand=1, fill="both")
        self.label = Label(frame, text=title, borderwidth=2, relief="groove")
        self.label.pack(fill="x")
        self.vbar = vbar = Scrollbar(frame, name="vbar")
        vbar.pack(side="right", fill="y")
        self.canvas = canvas = Canvas(frame,
                                      height=min(300, max(40, height)),
                                      scrollregion=(0, 0, width, height))
        canvas.pack(side="left", fill="both", expand=1)
        vbar["command"] = canvas.yview
        canvas["yscrollcommand"] = vbar.set
        self.subframe = subframe = Frame(canvas)
        self.sfid = canvas.create_window(0, 0, window=subframe, anchor="nw")
        self.load_dict(dict,0,{})

    dict = -1

    def loadHandler(self, dict, Entry):
            print "Load Handler"
            #if(self.loadCount%2==1):
            if(Entry.style =="Variable"):
                try:
                    Entry.update(repr(dict[Entry.name]))
                    #Entry.show()
                except KeyError:
                    pass
            elif (Entry.style == "For" and Entry.open):
                try:                            
                    Entry.iterator.update(repr(dict[Entry.iterator.name]))
                except KeyError:
                    pass
                for i in Entry.block:
                    print "In block " + i.toString()[:-1]
                    self.loadHandler(dict, i)
                self.loadCount = self.loadCount+1                    
                if(Entry.loopCounter%len(Entry.block)==0):
                    Entry.step()
                    Entry.loopCounter = 1
                else:
                    Entry.loopCounter = Entry.loopCounter + 1
                #Entry.update()
                #Entry.show()
            elif (Entry.style == "While"):
                try:                            
                    Entry.conditional.update(bool(Entry.conditional.name))
                except KeyError:
                    pass
                for i in Entry.block:
                    print "In block " + i.toString()[:-1]
                    self.loadHandler(dict, i)
                self.loadCount = self.loadCount+1                    
                if(Entry.loopCounter%len(Entry.block)==0):
                    Entry.step()
                    Entry.loopCounter = 1
                else:
                    Entry.loopCounter = Entry.loopCounter + 1
            elif (Entry.style == "If"):
                try:                            
                    Entry.conditional.update(repr(dict[Entry.conditional.name]))
                except KeyError:
                    pass
                for i in Entry.block:
                    self.loadHandler(dict, i)
            self.loadCount = 1

    def load_dict(self, dict, Entries, force=0, rpc_client=None):
        print "load_dict Check", self.repr.repr(self.master)
        #print self.repr.repr(self.subframe)

        if dict is self.dict and not force:
            return
        subframe = self.subframe
        frame = self.frame
        for c in subframe.children.values():
            c.destroy()
        self.dict = None
        if not dict:
            print "WHY YOU Hate me!!!!"
            l = Label(subframe, text="None")
            l.grid(row=0, column=0)
        else:
            names = dict.keys()
            names.sort()
            row = 0
            ind = 0
            for name in names:
                value = dict[name]
                svalue = self.repr.repr(value)
                # repr(value)
                # Strip extra quotes caused by calling repr on the (already)
                # repr'd value sent across the RPC interface:
                #print "Name:",name,"Value:", value
                #print "1Repr:",self.repr.repr(value)
                
                if rpc_client:
                    svalue = svalue[1:-1]
                #l = Label(subframe, text=name)
                #l.grid(row=row, column=0, sticky="nw")
                #l = Entry(subframe, width=0, borderwidth=0)
                #l.insert(0, svalue)
                #l.grid(row=row, column=1, sticky="nw")
                #row = row+1
            if len(Entries.list)>=1:
                for n in Entries.list:
                    self.loadHandler(dict, n)

        #print "EID =",eid
        #thisEnt = Entries.get(eid)
        #if (thisEnt!=None):
        #    print thisEnt.line
        #    print "IM HELPING"               
        #    try:
        #        #if Entry.name == pyshell.vis_Entries.
        #        print "NAME = ", thisEnt.name
        #        thisEnt.update(repr(dict[repr(thisEnt.name)]))
        #    except KeyError:
        #        print "WRONG!"                    
        self.dict = dict
        # XXX Could we use a <Configure> callback for the following?
        #subframe.update()
        subframe.update_idletasks() # Alas!          
        width = subframe.winfo_reqwidth()
        height = subframe.winfo_reqheight()
        canvas = self.canvas
        self.canvas["scrollregion"] = (0, 0, width, height)
        if height > 300:
            canvas["height"] = 300
            frame.pack(expand=1)
        else:
            canvas["height"] = height
            frame.pack(expand=0)

    def close(self):
        self.frame.destroy()