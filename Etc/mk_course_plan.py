#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, DBG, PrettyPrintTracebackDiagnostics, DiagStdErr #, Diagnostics, isBool, isInt, isStr, isTuple, isList, isDict
from Utils.colors import Col, ColEnd

from sys import stderr
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':

	def LoadText(filename, timeout=4000):
		assert isinstance(filename, str)
		with open(filename, 'r', timeout) as f:
			c = f.read().split("\n")
			return c

	def ParseWidths(headers):
		assert isinstance(headers, list)
		w = []
		h = []
		for i in headers:
			curr = 65
			if i[-1]=="}":
				n = i.find("{")
				if n>=0:
					curr = int(i[n+1:-1])
					#print(curr)
					h.append(i[:n])
			else:
				h.append(i)
				
			assert isinstance(curr, int) and curr>=0
			w.append(curr)
		
		assert len(w)==len(headers) and len(w)==len(h)
		return w, h		
			
	def ParseLine(h, expectedlen):
		def Trim(s):
			assert isinstance(s, str)
			s = s.replace("\t"," ")
			s = s.strip()
			return s

		def Encode(s):
			assert isinstance(s, str)
			return escape(s)

		assert isinstance(h, str)
		
		s = h.split("|")
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
			r.append(Encode(t))
		print(o)
		
		return r
		
	def GenerateHtml(headers, widths, parsed, fullhtmldoc):
		assert isinstance(headers, list)
		assert isinstance(widths, list)
		assert isinstance(parsed, list)
		assert isinstance(fullhtmldoc, bool)		
		
		M = len(headers)
		html = '<!DOCTYPE html>\n<html>\n<body>\n' if fullhtmldoc else ""
		html += '<table cellspacing="0px" cellpadding="1px" border="1px" align="center">\n<tbody>\n<tr style="background-color: #000000;" align="center">\n'		
		for i in zip(headers, widths):
			assert isinstance(i, tuple) and len(i)==2
			assert isinstance(i[0], str)
			assert isinstance(i[1], int) and i[1]>=0
			html += f'<td width="{i[1]}"><span style="background-color: #000000; color: #ffffff;"><strong>{i[0]}</strong></span></td>\n'
		html += '</tr>\n'

		for j in parsed:
			assert isinstance(j, list)
			assert len(j)==M
			html += '<tr align="center">\n'
			
			assert len(j)==len(widths)
			for k in zip(j, widths):
				assert isinstance(k, tuple) and len(k)==2
				assert isinstance(k[0], str)
				assert isinstance(k[1], int) and k[1]>=0
				html += f'<td width="{k[1]}">{k[0]}</td>\n'
			html += '</tr>'
		html += '</table>\n'
		html += '</body>\n</html>' if fullhtmldoc else ""
		
		return html
		
	def Usage(msg=""):
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
		planlist = LoadText(planfile)
		assert isinstance(planlist, list)
		
		N = len(planlist)
		if N<3:
			ERR(f"expected more that three lines in planfile '{planfile}', but got {N} lines")
		if planlist[0]!="COUSEPLAN":
			ERR(f"expected tag 'COUSEPLAN' in header of planfile '{planfile}', but got '{planlinst[0]}'")
		
		headers = ParseLine(planlist[1], -1)
		widths, headers = ParseWidths(headers)
		
		M = len(headers)
		if args.v > 0:
			print(headers, stderr)
		
		parsed = []
		for i in range(2, N):
			l = ParseLine(planlist[i], M)
			if args.v > 0:
				print(l, stderr)
			parsed.append(l)
			
		html = GenerateHtml(headers, widths, parsed, not args.t)
		
		outputfile = args.o
		assert isinstance(outputfile, str)
		with open(outputfile, 'w') as f:
			f.write(html)
		
		print("DONE")
		
	except Exception as e:
		DiagStdErr(stderr)
		PrettyPrintTracebackDiagnostics(e)
		exit(-1)