#!/usr/bin/env python3

from Utils.dbg import ERR, WARN
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':
	
	class Cmd:
		__cmdstate = 0 # 0: txt, 1: cmd, 2: args
		__st  = ""
		__cmd = ""
		__args= ""
		__txt = ""
		__tree = {}
				
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
				WARN(f"not correct class of object, got type '{s}', expected '{e}'")
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
		
		@staticmethod	
		def isHtmlCmd(c):			
			return isStr(c) in  ["em", "bf", "it", "p", "h1", "h2", "h3", "h4", "h5", "ul", "li"]
		
		def __MkCmd(self):
			assert self.Ok()
			
			c = self.__cmd
			a = self.__args
			
			self.__cmd = ""
			self.__args= ""
			
			left = '<'
			right= '>'
			
			t = f"cmd={c}({a})"			
			Dbg(verbose, f"FOUND COMMAND={t}..", 2)
			
			v = ""
			if Cmd.isHtmlCmd(c):
				v = f"{left}{c}{right}{a}{left}/{c}{right}"
			elif c=="link":
				args = a.split(",")
				assert len(args)==2
				v = f"{left}span style='font-family: courier new, courier;'{right}{left}a href='{args[1]}'{right}{args[0]}{left}/a{right}{left}/span{right}"
			elif c=="px":
				c = "p"
				v = f"{left}{c} style='margin-left: 30px'{right}{a}{left}/{c}{right}"

			else:
				ERR(f"unknown command '{c}'")
						
			self.__txt += v
			
			return (c, a)
	
		def Add(self, text):
			assert self.State()==2
			self.__st += isStr(text)
			
		def Parse(self, c):
			assert self.Ok()
			
			r = ""
			#self.__st += c
											
			if self.__cmdstate==2:
				if c=='}':	
					self.__cmdstate = 0	
					assert self.__args==""
					self.__args = isStr(self.__st, True)
					self.__st = ""
					return True, self.__MkCmd()
				else:
					self.__st += c
			elif self.__cmdstate==1:
				if c=='{':
					self.__cmdstate = 2
					assert self.__cmd==""
					self.__cmd = isStr(self.__st, True)
					self.__st = ""
				else:
					self.__st += c
			else:	
				assert self.__args==""
				assert self.__cmd==""
	
				if c=='\\':
					self.__cmdstate = 1
					self.__st = ""
				else:
					pass
					self.__txt += c

			return False, None	
	
	
	def ParseToHtml(elems):
		
		curr = Cmd()
		st = [] 
		
		for j in isList(elems):
			N = len(isStr(j))
			
			for i in range(N):		
				Cmd.isCmd(curr)
				c = j[i]	
				
				if c=='\\' and curr.State()!=0:
					st.append(curr)
					curr = Cmd()
				
				Cmd.isCmd(curr)
				
				p = curr.Parse(c)
				if p[0] and len(st)>0:
					t = curr.Text()
					curr = st.pop()
					curr.Add(t)
			
			curr.Parse("\n")
					
		if curr.State() != 0:
			ERR(f"still in command parsing state={curr.State()}")	
		
		if len(st) != 0:
			ERR(f"still {len(st)} elements on stack, expected zero")
		
		txt = curr.Text()		
		Dbg(verbose, f"{Col('CYAN')}{isStr(txt)}{ColEnd()}", 3)		
		return txt
		
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
			elif t=="REFS":
				curr = []
				assert not s.get(t)
				s[t] = curr				
			else:
				curr.append(t)
		
		html = "" 
		for i in s:
			h = ParseToHtml(s[i])
			html += h	
			Dbg(verbose, f"{Col('YELLOW')}found '{i}' {ColEnd()} => '{h}'", 2)
		
		return html
						
	try:
		def HtmlEncode(s):
			return escape(isStr(s))    

		f = "some { test \\call(a, b) fun end } end"
		assert f==HtmlEncode(f)
		
		verbose = 0
		coursefile = "course.txt"
		outputfile= None
	
		parser = ArgumentParser(prog=argv[0], epilog="version 0.1")
		parser.add_argument("-v", default=verbose,    action="count",      help= "increase output verbosity, default={verbose}\n")
		parser.add_argument("-t", default=False,      action="store_true", help=f"generate simple html (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-p", default=coursefile, type=str,            help=f"coursefile, default='{coursefile}'\n")
		parser.add_argument("-o", default=outputfile, type=str,            help=f"outputfilt, default='{outputfile}\n")
		args = parser.parse_args()
				
		verbose = isInt(args.v)				
		coursefile = args.p
		Dbg(verbose, f"{Col('PURPLE')}GENERATING course file '{coursefile}'..{ColEnd()}")

		htmlencoded = [HtmlEncode(i) for i in LoadText(coursefile)]
		html = ParseStructure(htmlencoded)				
		#html = html.replace("\n\n","<br>\n")
	
		if not args.t:
			bodystyle = "style='font-family: Verdana;font-size: 12pt;color: #494c4e;'"
			bodystyle = "style='font-family: times new roman, times, serif;font-size: 13pt;color: #424222;'"
			html = f"<!DOCTYPE html>\n<html>\n<body {bodystyle}>\n" + html + "\n</body>\n</html>"
		
		if args.o is None or len(args.o)<=0:
			print(html)
		else:
			with Outputfile(args.o) as f:
				f.write(html)		
		
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
		
	except Exception as ex:
		HandleException(ex)