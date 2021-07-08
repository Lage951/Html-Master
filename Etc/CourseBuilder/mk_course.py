#!/usr/bin/env python3

from Utils.dbg import ERR, WARN
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape, unescape

if __name__ == '__main__':

	_currline = -1
	_currcolumn = -1

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

			isStr(self.__st, False)
			isStr(self.__cmd, False)
			isStr(self.__args, False)
			
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
		def __MkLink(a, exlink, left, right):
			
			args = isStr(a).split(",")
			assert len(args)==2
			
			arg0 = isStr(args[0], False)
			arg1 = isStr(args[1]).strip()
			
			if len(arg1)==0:
				ERR("need second link argument, currently empty")
			
			if len(arg0)==0:
				n = arg1.rfind('/')
				if n<=0:
					ERR(f"if first argument to link is empty, second arg='{arg1}' must contain at least one slash '/'")
				
				arg0 = arg1[n+1:]
				if len(arg0)==0:
					ERR("second arg still empty, this was not expected")
				
			extra =  " rel='noopener' target='_blank'" if isBool(exlink) else ""
			return f"{isStr(left)}span style='font-family: courier new, courier;'{isStr(right)}{left}a href='{arg1}'{extra}{right}{arg0}{left}/a{right}{left}/span{right}"		

		@staticmethod	
		def __MkStyle(a, left, right):
			
			args = isStr(a).split(",")
			assert len(args)==2
			
			arg0 = isStr(args[0]).strip()
			arg1 = isStr(args[1]).strip()
			
			if arg0.find('"')>=0 or arg0.find("'")>=0:
				ERR(f"do not use pligs (') or quotes (\") in style command, style='{arg0}'")
			
			return f"{isStr(left)}span style='{arg0}'{isStr(right)}{arg1}{left}/span{right}"		
	
		@staticmethod	
		def __isHtmlCmd(c):			
			return isStr(c) in  ["b", "i", "p", "ul", "ol", "li", "header", "sub", "em", "indent", "code", "ipynb", "displaystyle"]

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
			# fun(arg)..
			if Cmd.__isHtmlCmd(c):
				
				style = ""				
				if c=="header":
					c = "h3"
				elif c=="sub":
					c = "h4"
				elif c=="em":
					c = "i" 
				elif c=="displaystyle":
					c = "p"
					style = " style='margin-left: 30px'" 
				elif c=="indent":
					c = "span"
					style = " style='margin-left: 30px'" 
				elif c=="code" or c=="ipynb":
					c = "span" 
					style=" style='font-family: courier new, courier;'"
					
				v = f"{left}{c}{style}{right}{a}{left}/{c}{right}"
			
			# fun(arg0, arg1)..
			elif c=="link" or c=="linkex":
				v = Cmd.__MkLink(a, c=="linkex", left, right)
			elif c=="style":
				v = Cmd.__MkStyle(a, left, right)				
			else:
				ERR(f"unknown command '{c}' with argument(s) '{a}'")
						
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
					if c=='(':
						WARN("found left parathesis '(' while in command parsing mode, did you mean '{'?")
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
		
	def ParseStructure(courselist):

		def ParseToHtml(elems):
			
			curr = Cmd()
			st = [] 
			
			for j in isList(elems):
				N = len(isStr(j, False))
				
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
			

		def ParseRefs(refs):
			r = {}
			for i in refs.split("\n"):					
				if len(isStr(i, False).strip())>0:						
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
			elif t=="DEFS":
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
		if isDict(htmlstructure).get("DEFS"):
			r = unescape(htmlstructure["DEFS"])
			del htmlstructure["DEFS"]			
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
			return escape(isStr(s, False))    

		def MkHtml(htmlstructure, addhtmlheaders, filenamebase):
			
			def MkHtmlPage(htmlcontent):
				assert isStr(htmlcontent).find("DOCTYPE")<0 and htmlcontent.find("<html>")<=0 and htmlcontent.find("<body>")<=0
				#bodystyle = "style='font-family: Verdana;font-size: 12pt;color: #494c4e;'"
				bodystyle = "style='font-family: times new roman, times, serif;font-size: 12pt;color: #424222;'"
				meta = "<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>"
				return f"<!DOCTYPE html>\n<html>\n{meta}\n<body {bodystyle}>\n" + htmlcontent + "\n</body>\n</html>"										
							
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
					
		def LoadCourseFile(coursefile):
			r = []
			for i in LoadText(isStr(coursefile)):
				t = i.strip()
				if len(t)>0 and t[0]!='%': # and t[0]!='#':
					r.append(i)
				else: 
					r.append("")
			return r
							
		f = "some ( test \\call{a, b} fun ) end"
		assert f==HtmlEncode(f)
		
		verbose = 0
		coursefile = "course.tex"
	
		parser = ArgumentParser(prog=argv[0], epilog="version 0.2")
		parser.add_argument("-v", default=verbose,     action="count",      help= "increase output verbosity, default={verbose}\n")
		parser.add_argument("-t", default=False,       action="store_true", help=f"generate simple html (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-o", default="",          type=str,            help=f"outputfilt, default=''\n")
		parser.add_argument("-c", default=coursefile,  type=str,            help="cause file to be parsed, default='{coursefile}'\n")
		
		args = parser.parse_args()
				
		verbose = isInt(args.v)				
		coursefile = isStr(args.c)
		
		Dbg(verbose, f"{Col('PURPLE')}GENERATING html course from file '{coursefile}'..{ColEnd()}")

		htmlencoded   = [HtmlEncode(i) for i in LoadCourseFile(coursefile)]
		htmlstructure = ParseStructure(htmlencoded)				
	
		MkHtml(htmlstructure, not args.t, args.o)		
		
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
		
	except Exception as ex:
		HandleException(ex)