#!/usr/bin/env python3

from Utils.dbg import ERR, WARN
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape, unescape

if __name__ == '__main__':

	#_currline = -1
	#_currcolumn = -1

	LEFT = '<'
	RIGHT= '>'

	def HtmlEncode(s):
		return escape(Str(s, False))    

	def HtmlDecode(s):
		return unescape(Str(s, False))

	def _mkHtml(tag, style=""):
		if len(Str(style, False)) > 0:
			if style[0]!=" ":
				style = " " + style
				if style.find("'") >= 0:
					ERR(f"no plings in style, please, got style = '{style}'")
				if style.find('"') >= 0:
					ERR(f"no quotes in style, please, got style = '{style}'")
					
		return f"{LEFT}{Str(tag)}{style}{RIGHT}"

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
			assert Int(self.__cmdstate)>=0 and self.__cmdstate<=2

			Str(self.__st, False)
			Str(self.__cmd, False)
			Str(self.__args, False)
			
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
		def __MkParseArg(a, checknonempty0=True, checknonempty1=True):

			args = Str(a).split(",")
			assert len(args)==2
			
			arg0 = Trim(args[0], checknonempty0)
			arg1 = Trim(args[1], checknonempty1)	
			if arg0.find('"')>=0 or arg0.find("'")>=0:
				ERR(f"do not use pligs (') or quotes (\") in style command, style='{arg0}'")
			
			return arg0, arg1
	
		@staticmethod	
		def __MkLink(a, isstar, uselinkfilename, left, right):
			
			if Str(a).find(",")<=0:
				Dbg(verbose, f"one argument link command '{a}'..", 2)
	
				arg0 = ""				
				arg1 = Trim(a)
			else:
				args = Str(a).split(",")
				assert len(args)==2
			
				arg0 = Str(args[0], False)
				arg1 = Trim(args[1])
			
			if len(arg1)==0:
				ERR(f"need second link argument or nonempty first argument, currently empty for arguments '{a}'")
			
			n_http  = arg1.find("http://")
			n_https = arg1.find("https://")
			m = 7 + (1 if n_https==0 else 0)
			
			if not (n_http==0 or n_https==0):
				ERR(f"link '{arg1}' does not begin with 'http://' or 'https://' as it should")
				
			if arg1[m]=="/":
				ERR(f"link with triple '///', for '{arg1}'")
			
			if len(arg0)==0:
				#n = arg1.rfind('/')
				#if n<=0:
				#	ERR(f"if first argument to link is empty, second arg='{arg1}' must contain at least one slash '/'")
				#
				#arg0 = arg1[n+1:]
				#if len(arg0)==0:
				#	ERR("second arg still empty, this was not expected")
				arg0 = arg1[m:]
				
				if uselinkfilename:
					k = arg0.rfind("/")
					if arg0[-1]=="/":
						ERR(f"can not generate file name, when link argument '{arg0}' ends in a slash '/'")
					if k<=0:
						ERR("could not generate filename from link '{arg0}', need at least one slash '/'")
					arg0 = arg0[k+1:]
			
			if len(arg0)==0:
				ERR("link arg0 ends-up empty, this was not the way it should be")
			
			exlink = True
			if arg1.find("au.dk")>0:
				exlink = False
				Dbg(verbose, f"internal link = '{arg1}'..", 2)
			else:
				Dbg(verbose, f"exernal link = '{arg1}'..",  2)
	
			extra = " rel='noopener' target='_blank'" if Bool(exlink) else ""
			style = " style='font-family: courier new, courier;'" if not Bool(isstar) else ""
			return f"{Str(left)}span{style}{Str(right)}{left}a href='{arg1}'{extra}{right}{arg0}{left}/a{right}{left}/span{right}"		

		@staticmethod	
		def __MkStyle(a, left, right):
			arg0, arg1 = Cmd.__MkParseArg(a)
			return f"{Str(left)}span style='{arg0}'{Str(right)}{arg1}{left}/span{right}"		
	
		@staticmethod	
		def __MkImg(a, left, right):		
			arg0, arg1 = Cmd.__MkParseArg(a, True, False)
			if arg1=="":
				arg1="the-missing-link: " + arg0
			return f"{Str(left)}img src='{arg0}' alt='{arg1}'{Str(right)}"		
	
		@staticmethod	
		def __isCmd(c):			
			return Str(c) in  ["b", "i", "p", "pre", "dl", "dt", "dd", "em", "itemize", "itemize*", "enumerate", "item", "item*", "subitem", "subitem*", "header", "sub", "subsub", "indent", "code", "ipynb", "quote", "displaystyle", "displaycode", "cite"]

		def __MkCmd(self):

			assert self.Ok()
			
			c = self.__cmd
			a = self.__args
			
			self.__cmd = ""
			self.__args= ""
			
			left = '<'
			right= '>'
			leftmarg = " style='margin-left: 30px;'"
			
			t = f"cmd={c}({a})"			
			Dbg(verbose, f"FOUND COMMAND={t}..", 2)
			
			v = ""
			# fun(arg)..
			if Cmd.__isCmd(c):
				
				head  =""
				tail  =""
				style = ""
				closing = True
								
				if c=="b" or c=="i" or c=="p" or c=="ul" or c=="li" or c=="ol" or c=="dl" or c=="pre":
					pass
				elif c=="itemize":
					c = "ul"
				elif c=="itemize*":
					c = "ul"
					style =  " style='list-style-type:none;'"
				elif c=="enumerate":
					c = "ol"
					style = " type='i'"
				elif c=="item" or c=="item*":
					if c=="item*":
						c = "p"
						style = leftmarg
					else:
						c = "li"
				elif c=="subitem" or c=="subitem*":
					if c=="subitem*":
						head = _mkHtml("dl")
						tail = _mkHtml("/dl")
						c = "dd"
					else:
						head = _mkHtml("ul")
						tail = _mkHtml("/ul")
						c = "li"
				elif c=="dt" or c=="dd":
					closing = False
				elif c=="header":
					c = "h2"
				elif c=="sub":
					c = "h3"
				elif c=="subsub":
					c = "h4"
				elif c=="em":
					c = "i" 
				elif c=="displaystyle":
					c = "p"
					style = leftmarg
				elif c=="displaycode":
					c = "code" 
					head = _mkHtml("pre", leftmarg)
					tail = _mkHtml("/pre")
				elif c=="indent":
					c = "span"
					style = leftmarg
				elif c=="code" or c=="ipynb":
					c = "span" 
					style=" style='font-family: courier new, courier;'"
				elif c=="cite" :
					c = "span" 
					a = "[kilde: " + a + "]"
					style=" style='font-size: xx-small;'"
					head = "<br>\n"
					tail = "<br>\n"
				elif c=="quote":
					c = "span"
					style = leftmarg 
					head = "<br>\n<br>\n"
					tail = "<br>\n<br>\n"
				else:
					ERR(f"that odd, an unhandled command '{c}' that seem to be present in isCmd() list")
					
				closetags = f"{left}/{c}{right}{tail}" if closing else ""
				v = f"{head}{left}{c}{style}{right}{a}{closetags}"
			
			# fun(arg0, arg1)..
			elif c=="link" or c=="link*" or c=="link**":
				v = Cmd.__MkLink(a, c=="link*", c=="link**", left, right)
			elif c=="style":
				v = Cmd.__MkStyle(a, left, right)				
			elif c=="img":
				v = Cmd.__MkImg(a, left, right)				
			else:
				ERR(f"unknown command '{c}' with argument(s) '{a}'")
						
			self.__txt += v
			
			return (c, a)
	
		def Add(self, text):
			assert self.State()==2
			self.__st += Str(text)
			
		def Parse(self, c):
			assert self.Ok()
			
			r = ""
			#self.__st += c
											
			if self.__cmdstate==2:
				if c=='}':	
					self.__cmdstate = 0	
					assert self.__args==""
					self.__args = Str(self.__st, False)
					self.__st = ""
					return True, self.__MkCmd()
				else:
					self.__st += c
			elif self.__cmdstate==1:
				if c=='{':
					self.__cmdstate = 2
					assert self.__cmd==""
					self.__cmd = Str(self.__st)
					self.__st = ""
				else:
					if c=='(' or c=='[':
						WARN("found left parathesis '{c}' while in command parsing mode, did you mean '{'?")
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
			
			for j in List(elems):					
				N = len(Str(j, False))
				
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
			Dbg(verbose, f"{Col('CYAN')}{Str(txt)}{ColEnd()}", 3)		
			return txt
			

		def ParseDefs(refs):
			r = {}
			for i in refs.split("\n"):					
				if len(Trim(i, False))>0:						
					n = Str(i).find(']')
					
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
			
		def ParseDefs2(defs):
			r = {}
			for i in List(defs):				
				d = HtmlDecode(Trim(i, False))	
				if len(d) > 0:						
					n = Str(d).find(']')
					
					if n<=0 or d[0]!='[':
						ERR(f"refs need to be of the form '[key] value', got='{i}'")
					
					key = d[0:n+1].strip()
					val = d[n+1:].strip()
					
					if len(key)==0:
						ERR(f"empty key in ref element='{i}'")
					if len(val)==0:
						ERR(f"empty value in ref element='{i}'")
						
					Dbg(verbose, f"    ParseRef(): found '{key}' => '{val}'", 2)
					assert not r.get(key)
					r[key]=val
			return r

		def ParseBasetructure(courselist):
			N = len(List(courselist))
			
			if N<=0:
				ERR("file seems to be empty")
			if courselist[0]!="COURSE":
				ERR("missing tag 'COURSE' in course file")
				
			s = {}
			curr = None
					
			# 1: 
			for i in range(1, N):
						
				t = Trim(courselist[i], False)
							
				if t=="END":
					break
				elif t.find("CONTENT")==0:
					curr = []
					assert not s.get(t)
					s[t] = curr
				elif t=="DEFS":
					curr = []
					assert not s.get(t)
					s[t] = curr				
				else:
					curr.append(t)
			return s
		
		# 1: base structure
		s = ParseBasetructure(courselist)
		
		# 2: preprocess, search and replace defs
		defs = {} 
		if Dict(s).get("DEFS"):
			r =s["DEFS"]
			del s["DEFS"]			
			defs = ParseDefs2(r)
		
		for i in s:
			n = Str(i).find("CONTENT")

			if n>0:
				ERR("CONTENT tag not in column 1, but in column {n} for entry '{i}'")
			elif n==0:
				l = []
				for line in List(s[i]):
					for key in defs:
						assert Str(key)[0]=='[' and key[-1]==']'			
						val = Str(defs[key])
						line = line.replace(key, val)			
					l.append(Str(line, False))
				s[i] = l
		
		# 3: parse structure and generate html code
		htmlstructure = {}		
		for i in s:		
			h = ParseToHtml(s[i])
			assert not htmlstructure.get(i)
			htmlstructure[i] = h	
			Dbg(verbose, f"  {Col('YELLOW')}FOUND '{i}' {ColEnd()} {' => ' + h if verbose>2 else ''}", 2)

		#defs = {} 
		#if Dict(htmlstructure).get("DEFS"):
		#	r = unescape(htmlstructure["DEFS"])
		#	del htmlstructure["DEFS"]			
		#	defs = ParseDefs(r)
		#
		#for i in htmlstructure:
		#	html = Str(htmlstructure[Str(i)])
		#	for key in defs:
		#		assert Str(key)[0]=='[' and key[-1]==']'			
		#		val = Str(defs[key])
		#		html = html.replace(key, val)			
		#	htmlstructure[i] = Str(html)
		#			
		
		return htmlstructure
						
	try:
		def MkHtml(htmlstructure, addhtmlheaders, filenamebase):		
			for i in htmlstructure:
				assert Str(i).find("CONTENT")==0
				
				sublesson = i[7:].strip()
				if len(sublesson)<=0:
					ERR("sublesson name empty (or just whitespace)")
				
				outputfilename = Str(filenamebase) + sublesson + ".html" 
				htmlcontent = Str(htmlstructure[i]) 
				
				Dbg(verbose, f"  {Col('YELLOW')}WRITING '{i}' => '{outputfilename}'{ColEnd()}", 1)
				html = MkHtmlPage(htmlcontent) if Bool(addhtmlheaders) else htmlcontentl 
				
				with Outputfile(outputfilename) as f:
					f.write(html)				
					
		def LoadCourseFile(coursefile):
			r = []
			for i in LoadText(Str(coursefile)):
				n = i.find('%')
				if n>=0:
					r.append(i[0:n])
				else:			
					r.append(i)
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
				
		verbose = Int(args.v)				
		coursefile = Str(args.c)
		
		Dbg(verbose, f"{Col('PURPLE')}GENERATING html course from file '{coursefile}'..{ColEnd()}")

		htmlencoded   = [HtmlEncode(i) for i in LoadCourseFile(coursefile)]
		htmlstructure = ParseStructure(htmlencoded)				
	
		MkHtml(htmlstructure, not args.t, args.o)		
		
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
		
	except Exception as ex:
		HandleException(ex)