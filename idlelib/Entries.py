from parse import *
import string
from idlelib.EditorWindow import EditorWindow, fixwordbreaks


class Entry:
	def __init__(self, eid, line, pyshell):
		self.pyshell = pyshell
		self.eid = eid
		self.open = True
		self.mark_is_set = False
		self.style = "Entry"
		self.line = line
		self.block = []

	def append(self, Entry):
		self.block.append(Entry)

	def show(self):
		self.pyshell.set_start_mark(self.eid)
		self.pyshell.vis_write(self.toString())		
		self.pyshell.set_end_mark(self.eid)
		self.mark_is_set = True
		#self.pyshell.update_vis1()
		

	def update(self):		
		#self.pyshell.vis_write(self.toString())
		#self.pyshell.update_vis1()
		pass

	def makeBlock(self, line):
		lines = string.split(line,"\n")
		for n in lines:
			self.block.append(self.toEntry(self.eid, string.strip(n)))

	def toEntry(self, eid, line):
		thisEntry = Entry(eid, line, self.pyshell)
		if line.find('for')>-1:
			thisEntry = For_Entry(eid, line, self.pyshell)          
		elif line.find('if')>-1:
			thisEntry = If_Entry(eid, line, self.pyshell)
		elif line.find('while')>-1:
			thisEntry = While_Entry(eid, line, self.pyshell)
		elif line.find('=')>-1:
			thisEntry = Var_Entry(eid, line, self.pyshell)
		return thisEntry

	def toString(self):
		return "E"


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
			return str(self.name) + " = None" + "\n"
		else:
			return str(self.name) + " = " + str(self.value) +"\n"

class For_Entry(Entry):
	def __init__(self, eid, line, pyshell):
		temp = parse("{}:{}",line)
		Entry.__init__(self, eid, temp[0]+":", pyshell)
		self.style = "For"
		self.open = True
		self.loopCounter = 1
		x = parse("for {} in {}:{}",line)
		self.makeBlock(temp[1])	
		x = string.strip(x[0])+"= NONE"
		self.iterator = Var_Entry(eid, x, pyshell)
		self.report = temp[0]+':\n'
		self.lastSub = ""

	def step(self):
		if(self.open):
			if(self.iterator.toString().find("NONE")<0):
				sub = self.iterator.toString()[:-1]+"    | "
				for n in range(len(self.block)):
					if(self.block[n].style != "Entry"):
						sub = sub + self.block[n].toString()[:-1]
						if(n+1<len(self.block) and self.block[n+1].style != "Entry"):
							sub = sub + "\n" +(" "*len(self.iterator.toString()))+ "    | "						
				sub = sub+"\n"
				if(sub!=self.lastSub):#corrects closed block updates
					self.report = self.report+sub
					self.lastSub = sub
	
	def toString(self):
		return self.report

class While_Entry(Entry):
	def __init__(self, eid, line, pyshell):
		temp = parse("{}:{}",line)
		Entry.__init__(self, eid, temp[0]+":", pyshell)
		self.style = "While"
		self.open = True
		self.loopCounter = 1
		x = parse("while{}:{}",line)
		self.makeBlock(temp[1])	
		x = string.strip(x[0])+"= " + str(bool(x[0]))
		self.conditional = Var_Entry(eid, x, pyshell)
		self.report = temp[0]+':\n'
		self.lastSub = ""

	def step(self):
		if(self.open):
			sub = self.conditional.toString()[:-1]+"| "
			for n in range(len(self.block)):
				if(self.block[n].style != "Entry"):
					sub = sub + self.block[n].toString()[:-1]
					if(n+1<len(self.block) and self.block[n+1].style != "Entry"):
						sub = sub + "\n" +(" "*len(self.conditional.toString()))+ "\t| "						
			sub = sub+"\n"
			if(sub!=self.lastSub):#corrects closed block updates
				self.report = self.report+sub
				self.lastSub = sub

	
	def toString(self):
		return self.report

class If_Entry(Entry):
	def __init__(self, eid, line, pyshell):
		temp = parse("{}:{}",line)
		Entry.__init__(self, eid, temp[0]+":", pyshell)
		self.style = "If"
		self.open = True
		self.loopCounter = 1
		x = parse("if{}:{}",line)
		self.makeBlock(temp[1])	
		x = string.strip(x[0])+"= " + str(bool(x[0]))
		self.conditional = Var_Entry(eid, x, pyshell)
		self.report = temp[0]+':\n'
		self.lastSub = ""

	def step(self):
		if(self.open):
			sub = self.conditional.toString()[:-1]+"| "
			for n in range(len(self.block)):
				if(self.block[n].style != "Entry"):
					sub = sub + self.block[n].toString()[:-1]
					if(n+1<len(self.block) and self.block[n+1].style != "Entry"):
						sub = sub + "\n" +(" "*len(self.conditional.toString()))+ "\t| "						
			sub = sub+"\n"
			if(sub!=self.lastSub):#corrects closed block updates
				self.report = self.report+sub
				self.lastSub = sub


	def toString(self):
		return self.report

class Entries:
	def __init__(self, pyshell):
		self.pyshell = pyshell
		self.list = []
		self.currentEid=0


	#def showAll(self):
	#	for n in self.list:
	#		if(n.style != "Entry" and not n.mark_is_set):
	#			n.show()
	#		else:
	#			print "CHECK SHOW TEST %s" % n.eid
	#			self.pyshell.vis_update(string.strip(n.toString()), n.eid)


	def showAll(self):
		for n in self.list:
			if(n.open):
				if(n.style != "Entry" and not n.mark_is_set):
					n.show()
					if n.style == "For" or n.style == "While" or n.style == "If":
						n.open = False
				else:
					print "start M = %s" % self.pyshell.vis_text.index("s%s" % n.eid)
					print "end M = %s" % self.pyshell.vis_text.index("e%s" % n.eid)
					previous = string.strip(self.pyshell.get_text("s%s" % n.eid, "e%s" % n.eid))
					current = string.strip(n.toString())
					print previous + "\n" + current
					if not previous == current:
						self.pyshell.vis_update(current+"\n", n.eid)
					

	

	def add(self, Entry):
		if(Entry.eid>=len(self.list)):
			self.list.append(Entry)
		else:
			self.list[Entry.eid].append(Entry)


	def Vars(self):
		result = Entries(self.pyshell)
		for n in self.list:
			if(n.style=="Variable"):
				result.add(n)
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