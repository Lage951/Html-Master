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

		def ParseRefs(refs):
			r = {}
			for i in refs.split("\n"):					
				if len(isStr(i).strip())>0:						
					n = isStr(i).find(']')
					
					if n<=0 or i[0]!='[':
						ERR(f"refs need to be of the form '[key] value', got='{i}'")
					
					key = i[0:n+1].strip()
					val = i[n+1:].strip()
					
					if len(key)==0:
						ERR(f"empty key in ref element='{i}'")
					if len(val)==0:
						ERR(f"empty value in ref element='{i}'")
						
					Dbg(verbose, f"    ParseRef(): found '{key}' => '{val}'", 2)
					assert not r.get(key)
					r[key]=val
				
			return r

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
		
		htmlstructure = {}
		
		for i in s:
			h = ParseToHtml(s[i])
			assert not htmlstructure.get(i)
			htmlstructure[i] = h	
			Dbg(verbose, f"  {Col('YELLOW')}FOUND '{i}' {ColEnd()} {' => ' + h if verbose>2 else ''}", 2)

		refs = {} 
		if isDict(htmlstructure).get("REFS"):
			r = htmlstructure["REFS"]
			del htmlstructure["REFS"]			
			refs = ParseRefs(r)
		
		for i in htmlstructure:
			html = isStr(htmlstructure[isStr(i)])
			for key in refs:
				assert isStr(key)[0]=='[' and key[-1]==']'			
				val = isStr(refs[key])
				html = html.replace(key, val)			
			htmlstructure[i] = isStr(html)
					
		return htmlstructure
						
	try:
		def HtmlEncode(s):
			return escape(isStr(s))    

		def MkHtml(htmlstructure, addhtmlheaders, filenamebase):
			
			def MkHtmlPage(htmlcontent):
				assert isStr(htmlcontent).find("DOCTYPE")<0 and htmlcontent.find("<html>")<=0 and htmlcontent.find("<body>")<=0
				#bodystyle = "style='font-family: Verdana;font-size: 12pt;color: #494c4e;'"
				bodystyle = "style='font-family: times new roman, times, serif;font-size: 13pt;color: #424222;'"
				return f"<!DOCTYPE html>\n<html>\n<body {bodystyle}>\n" + htmlcontent + "\n</body>\n</html>"
						
				
							
			for i in htmlstructure:
				assert isStr(i).find("LESSON")==0
				
				sublesson = i[6:].strip()
				if len(sublesson)<=0:
					ERR("sublesson name empty (or just whitespace)")
				
				outputfilename = isStr(filenamebase) + sublesson + ".html" 
				htmlcontent = isStr(htmlstructure[i]) 
				
				Dbg(verbose, f"  {Col('YELLOW')}WRITING '{i}' => '{outputfilename}'{ColEnd()}", 1)
				html = MkHtmlPage(htmlcontent) if isBool(addhtmlheaders) else htmlcontentl 
				
				with Outputfile(outputfilename) as f:
					f.write(html)				
							
		f = "some ( test \\call{a, b} fun ) end"
		assert f==HtmlEncode(f)
		
		verbose = 0
		coursefile = "course.txt"
	
		parser = ArgumentParser(prog=argv[0], epilog="version 0.1")
		parser.add_argument("-v", default=verbose,    action="count",      help= "increase output verbosity, default={verbose}\n")
		parser.add_argument("-t", default=False,      action="store_true", help=f"generate simple html (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-p", default=coursefile, type=str,            help=f"coursefile, default='{coursefile}'\n")
		parser.add_argument("-o", default="",         type=str,            help=f"outputfilt, default=''\n")
		args = parser.parse_args()
				
		verbose = isInt(args.v)				
		coursefile = args.p
		Dbg(verbose, f"{Col('PURPLE')}GENERATING course file '{coursefile}'..{ColEnd()}")

		htmlencoded = [HtmlEncode(i) for i in LoadText(coursefile)]
		htmlstructure = ParseStructure(htmlencoded)				
	
		MkHtml(htmlstructure, not args.t, args.o)		
		
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
		
	except Exception as ex:
		HandleException(ex)