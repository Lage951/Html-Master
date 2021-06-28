#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, DBG, PrettyPrintTracebackDiagnostics, DiagStdErr #, Diagnostics, isBool, isInt, isStr, isTuple, isList, isDict
from Utils.colors import Col, ColEnd

from sys import stderr
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':
	
	def isStr(t):
		assert isinstance(t, str)
		#assert len(t)>0
		return t

	def isBool(t):
		assert isinstance(t, bool)
		return t

	def isInt(t, minval=0):
		assert isinstance(t, int)
		assert t>=minval
		return t
		
	def isList(t):
		assert isinstance(t, list)
		return t
	
	def isTuple(t, expectedlen=2):
		assert isinstance(t, tuple)
		assert len(t)==isInt(expectedlen, 1)
		return t
	
	def LoadText(filename, timeout=4000, split=True):
		with open(isStr(filename), 'r', timeout) as f:
			c = f.read()
			if split:
				c= c.split("\n")
			return c
	
	def ParseStructure(planlist):

		def Check(expr, msg):
			isStr(msg)
			if not expr:
				Err("EXPRESSION NOT FULLFILLED: " + msg)
	
		def Trim(s):
			s = isStr(s).replace("\t"," ")
			s = s.strip()
			return s

		def ParseWidths(headers):
			w = []
			h = []
			for i in isList(headers):
				curr = 65
				if i[-1]=="}":
					n = i.find("{")
					if n>=0:
						curr = int(i[n+1:-1])
						#print(curr)
						h.append(i[:n])
				else:
					h.append(i)
					
				w.append(isInt(curr, 0))
			
			assert len(w)==len(headers) and len(w)==len(h)
			return w, h		
				
		def ParseLine(h, expectedlen):
			s = isStr(h).split("|")
			N = len(s)
			
			if N != expectedlen:
				if expectedlen < 0 and N < 2:
					ERR(f"expected more than one column in header '{h}', but got {N} column(s)")
				elif expectedlen >= 0:
					ERR(f"expected exaclty {expectedlen} column(s) in line '{h}', but got {N} column(s)")
			
			r = []
			o = ""
			for i in s:
				t = Trim(i)
				o += ("     " if expectedlen < 0 else "  ") + t + ("\n" if expectedlen < 0 else " | ") 
				r.append(t)
			print(o)
			
			return r
		
		def Check(expr, msg):
			isStr(msg)
			if not expr:
				ERR("CONDITION NOT FULLFILLED: " + msg)

		def CheckLine(i, expected):
			Check(i<len(planlist),        "i={i} < len of planlist={len(planlist}") 
			Check(planlist[i]==expected, f"planlist missing tag '{expected}' at line {i}, got='{planlist[i]}'")
						
		N = len(isList(planlist))
		if N < 7:
			ERR("planlist too short, expected at least three lines with COUSEPLAN/HEAD/CONTENT/REFS/END")
		
		CheckLine(0, "COUSEPLAN")
		CheckLine(1, "HEAD")
		CheckLine(3, "CONTENT")

		headers = ParseLine(planlist[2], -1)
		widths, headers = ParseWidths(headers)		
		M = len(headers)
		
		s = {}
		s['headers'] = headers
		s['widths']  = widths
		
		curr = []
		
		for j in range(4, N):
			i = isStr(Trim(planlist[j]))
			
			if i=="REFS":
				s['content']=curr
				curr = []
			if i=="END":
				e = True
				s['refs']=curr
				curr = None
				break
			curr.append(i)
					
		Check(curr is None, 	"plainlist missing END tag")
		Check(s.get('content'), "planlist missing content structure")
		Check(s.get('refs'),    "planlist missing ref structure")

		parsed = []
		for i in s['content']:
			l = ParseLine(i, M)
			if args.v > 0:
				print(l, stderr)
			parsed.append(l)
		s['parsed'] = parsed
	
		return s

	def GenerateHtml(headers, widths, parsed, fullhtmldoc):
		def HtmlEncode(s):
			return escape(isStr(s))
		
		M = len(isList(headers))
		html = '<!DOCTYPE html>\n<html>\n<body>\n' if isBool(fullhtmldoc) else ""
		html += '<table cellspacing="0px" cellpadding="1px" border="1px" align="center">\n<tbody>\n<tr style="background-color: #000000;" align="center">\n'		
		
		for i in zip(isList(headers), isList(widths)):
			isTuple(i)
			html += f'<td width="{isInt(i[1])}"><span style="background-color: #000000; color: #ffffff;"><strong>{HtmlEncode(i[0])}</strong></span></td>\n'
		html += '</tr>\n'

		for j in isList(parsed):
			assert len(isList(j))==M
			html += '<tr align="center">\n'
			
			assert len(j)==len(widths)
			for k in zip(j, widths):
				isTuple(k)
				html += f'<td width="{isInt(k[1])}">{HtmlEncode(k[0])}</td>\n'
			html += '</tr>'
		
		html += '</table>\n'
		html += '</body>\n</html>' if isBool(fullhtmldoc) else ""
		
		return html
		
	def Usage(msg=""):
		def test():
			print("test")
			
		print("Usage: mk_course_plan.py [-v] [-t] [-p <planfile>] [-o <outputfile>]") 
		print("  version 0.1")
		print("Args:")
		print("  -v: verbose, default=0")
		print("  -t: generate simple table (witouth <html> <body> etc tags), default=False")
		print("  -p <string>: planfile")
		print("  -o <string>: outputfile")
		if len(msg)>0:
			WARN(msg)
		return 1
		
	try:		
		planfile = "plan.txt"
		outputfile= "index.html"
		
		parser = ArgumentParser()
		parser.add_argument("-v", default=0,          action="count",      help= "increase output verbosity, default=0\n")
		parser.add_argument("-t", default=False,      action="store_true", help=f"generate simple table (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-p", default=planfile,   type=str,            help=f"planfile, default={planfile})\n")
		parser.add_argument("-o", default=outputfile, type=str,            help=f"outputfilt, default={outputfile})\n")
		args = parser.parse_args()
		
		planfile = args.p
		print(f"GENERATING html plan from file '{planfile}'..")
		
		structure = ParseStructure(LoadText(planfile))		
	
		if args.v > 0:
			print(structure['headers'], stderr)
		
		html = GenerateHtml(structure['headers'], structure['widths'], structure['parsed'], not args.t)
		
		with open(isStr(args.o), 'w') as f:
			f.write(html)
		
		print("DONE")
		
	except Exception as e:
		DiagStdErr(stderr)
		PrettyPrintTracebackDiagnostics(e)
		exit(-1)