from parse import *
import string

class Entry:
	def __init__(self, eid, line, pyshell):
		self.pyshell = pyshell
		self.eid = eid
		self.style = "Entry"
		self.line = line
		self.block = []

	def append(self, Entry):
		self.block.append(Entry)

	def update(self):
		self.pyshell.update_vis1()
		pass

	def makeBlock(self, line):
		lines = string.split(line,"\n")
		for n in lines:
			self.toEntry(self.eid, n)

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

	def toString(self):
		return ""



class Var_Entry(Entry):
	def __init__(self, eid, line, pyshell):
		Entry.__init__(self, eid, line, pyshell)
		self.style = "Variable"
		x = parse("{}={}",line)		
		self.name = string.strip(x[0])
		self.value = string.strip(x[1])

	def set_value(self, value):
		self.value = value

	def update(self, value):
		self.value = value
		Entry.update(self)

	def toString(self):
		if (self.value == None):
			return self.name + " = None"
		else:
			return self.name + " = " + self.value

class For_Entry(Entry):
	def __init__(self, eid, line, pyshell):
		temp = parse("{}:{}",line)
		Entry.__init__(self, eid, temp[0]+":", pyshell)
		self.style = "For"
		self.open = True
		x = parse("for {} in {}:{}",line)
		print "WHAT UP!!!"
		print repr(temp)
		print temp[1]+" "
		self.makeBlock(repr(temp[1]))	
		x = string.strip(x[0])+"= NONE"
		self.iterator = Var_Entry(eid, x, pyshell)
		self.report = temp[0]+':\n'

	def step(self):
		print "For Step!"
		self.report = self.report+self.iterator.toString()+"\t|"
		for n in self.block:
			if(n.style != "Entry"):
				self.report = self.report+"\n"+(" "*len(self.iterator.toString()))+ "\t| "+ n.toString()

	


	def toString(self):
		return self.report


class Entries:
	def __init__(self, pyshell):
		self.pyshell = pyshell
		self.list = []
		self.currentEid=0

	#def add(self, lines):
	#	self.eid=eid
	#	for n in range(len(lines)):
    #    	if line[n].find('for')>-1:
    #    	    self.parse_for(line[n])
    #    	elif line[n].find('if')>-1:
    #    	    self.parse_if(line[n])
    #    	elif line[n].find('while')>-1:
    #    	    self.parse_while(line[n])
    #    	elif line[n].find('=')>-1:
    #    	    x = parse('{}={}',line[n])
    #    	    print x[0]
    #    	    thisEntry = self.Entries.hasVar(x[0])
    #    	    if thisEntry==None:
    #    	        thisEntry = Var_Entry(eid, line[], self)
    #    	        self.Entries.add(thisEntry)
	
	def add(self, Entry):
		if(Entry.eid>=len(self.list)):
			print len(self.list)
			print "add 1", Entry.line, Entry.style, Entry.eid
			self.list.append(Entry)
			print self.list[0].toString()
		else:
			print "Appending"
			self.list[Entry.eid].append(Entry)


	def Vars(self):
		result = Entries(self.pyshell)
		#print self.list
		for n in self.list:
			#print n.__repr__
			if(n.style=="Variable"):
				result.add(n)
		#print result
		return result

	def Ifs(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style=="If"):
				result.add(n)
		return result

	def Fors(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style=="For"):
				result.add(n)
		return result

	def Controls(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style!="Variable" or n.style!="Entry"):
				result.add(n)
		return result

	def While(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style=="While"):
				result.add(n)
		return result

	def Funs(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style=="Function"):
				result.add(n)
		return result

	def get(self, x):
		if x<len(self.list):
			return self.list[x]
		else:
			return -1

	def getVar(self, name):
		thevars = self.Vars()
		for n in thevars.list:
			if (name == n.name):
				return n
		return None

	def hasVar(self, name):
		thevars = self.Vars()
		for n in thevars.list:
			if (name == n.name):
				return True
		return False

	def length(self):
		return len(self.list)

	def show(self):
		block = []
		for n in len(self.list):
			block.append(repr(self.list))
		return block