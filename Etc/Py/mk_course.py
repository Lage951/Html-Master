#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, DBG, PrettyPrintTracebackDiagnostics, DiagStdErr #, Diagnostics, isBool, isInt, isStr, isTuple, isList, isDict
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':
	
	verbose = 0
	planfile = "plan.txt"
	outputfile= None
		
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
		
			Dbg(verbose, str(o), 3)
			
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
			
			Dbg(verbose, str(l), 2)
				
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
	
		Dbg(verbose, str(structure['headers']), 2)
		html = GenerateHtml(structure['headers'], structure['widths'], structure['parsed'], not args.t)
		
		with Outputfile(args.o) as f:
			f.write(html)
		
		Dbg(verbose, "DONE")
		
	except Exception as ex:
		HandleException(ex)