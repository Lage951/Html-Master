#!/usr/bin/env python3

from Utils.dbg import ERR, WARN
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':
	
	verbose = 0
	coursefile = "course.txt"
	outputfile= None

	class Cmd:
		__cmdstate = 0 # 0: txt, 1: cmd, 2: args
		__st  = ""
		__cmd = ""
		__args= ""
		__txt = ""
		
		def State(self):
			assert self.Ok()
			return self.__cmdstate
			
		def Text(self):
			assert self.State()==0
			return self.__txt
					
		@staticmethod	
		def isCmd(obj):
			s = str(type(obj))
			e = "<class '__main__.Cmd'>"
			if s != e:
				WARN(f"no correct class of object, got type '{s}', expected '{e}'")
			return True
			
		def Ok(self):
			assert Cmd.isCmd(self)
			assert isInt(self.__cmdstate)>=0 and self.__cmdstate<=2

			isStr(self.__st)
			isStr(self.__cmd)
			isStr(self.__args)
			
			#if self.__cmdstate==0:
			#	assert self.__args==""
			#	assert self.__cmd==""
			#elif self.__cmdstate==1:
			#	assert self.__cmd!=""
			#	assert self.__args==""	
			#elif self.__cmdstate==2:
			#	assert self.__cmd!=""
	
			return True
		
		def __MkCmd(self):
			assert self.Ok()
			
			c = self.__cmd
			a = self.__args
			
			self.__cmd = ""
			self.__args= ""
			
			t = f"cmd={c}({a})"
			print(f"FOUND COMMAND={t}..")
			
			v = ""
			if c=="em" or c=="bf" or c=="it" or c=="h5" or c=="itemize" or c=="item":
				v = f"<{c}>{a}</{c}>"
			elif c=="link":
				args = a.split(",")
				assert len(args)==2
				v = f"<a href='{args[1]}'>{args[0]}</a>"
			else:
				ERR(f"unknown command '{c}'")
						
			self.__txt += v
	
			
		def Add(self, text):
			assert self.State()==2
			self.__st += isStr(text)
			
		def Parse(self, c):
			assert self.Ok()
			
			r = ""
			self.__st += c
											
			if self.__cmdstate==2:
				if c=='}':	
					self.__cmdstate = 0	
					assert self.__args==""
					self.__args = isStr(self.__st[:-1], True)
					self.__st = ""
					self.__MkCmd()
					return True
			elif self.__cmdstate==1:
				if c=='{':
					self.__cmdstate = 2
					assert self.__cmd==""
					self.__cmd = isStr(self.__st[:-1], True)
					self.__st = ""
			else:	
				assert self.__args==""
				assert self.__cmd==""
	
				if c=='\\':
					self.__cmdstate = 1
					self.__st = ""
				else:
					self.__txt += c

			return False
	
	def ParseToHtml(elems):
		
		curr = Cmd()
		st = [] 
		txt = ""
		
		for j in isList(elems):
			N = len(isStr(j))
			
			for i in range(N):		
				Cmd.isCmd(curr)
				c = j[i]	
				
				if c=='\\' and curr.State()!=0:
					st.append(curr)
					curr = Cmd()
				
				Cmd.isCmd(curr)
				
				if curr.Parse(c) and len(st)>0:
					t = curr.Text()
					curr = st.pop()
					curr.Add(t)
			
			curr.Parse("\n")
					
		if curr.State() != 0:
			ERR(f"still in command parsing state={curr.State()}")	
		
		if len(st) != 0:
			ERR(f"still {len(st)} elements on stack, expected zero")
		
		txt = curr.Text()		
		print(isStr(txt))
		
	def ParseStructure(courselist):
		N = len(isList(courselist))
		
		if N<=0:
			ERR("file seems to be empty")
		if courselist[0]!="COURSE":
			ERR("missing tag 'COURSE' in course file")
			
		s = {}
		curr = None
		for i in range(1, N):
			t = Trim(courselist[i])
						
			if t=="END":
				break
			elif t.find("LESSON")==0:
				curr = []
				assert not s.get(t)
				s[t] = curr
			else:
				curr.append(t)
				
		for i in s:
			print(f"found '{i}' => '{ParseToHtml(s[i])}'")
			
				
	try:	
		file = "course.txt"
	
		parser = ArgumentParser(prog=argv[0], epilog="version 0.1")
		parser.add_argument("-v", default=verbose,    action="count",      help= "increase output verbosity, default={verbose}\n")
		parser.add_argument("-t", default=False,      action="store_true", help=f"generate simple table (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-p", default=coursefile, type=str,            help=f"coursefile, default='{coursefile}'\n")
		parser.add_argument("-o", default=outputfile, type=str,            help=f"outputfilt, default='{outputfile}\n")
		args = parser.parse_args()
				
		verbose = isInt(args.v)
				
		coursefile = args.p
		Dbg(verbose, f"GENERATING course file '{coursefile}'..")

		structure = ParseStructure(LoadText(coursefile))		
	
		#Dbg(verbose, str(structure['headers']), 2)
		#html = GenerateHtml(structure['headers'], structure['widths'], structure['parsed'], not args.t)
		#
		#with Outputfile(args.o) as f:
		#	f.write(html)
		#
		
		Dbg(verbose, "DONE")
		
	except Exception as ex:
		HandleException(ex)