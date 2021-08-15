#!/usr/bin/env python3

from Utils.dbg import ERR
from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv
from argparse import ArgumentParser
from html import escape
 
if __name__ == '__main__':
	
		
	def ParseStructure(planlist):

		def ParseWidths(headers):
			w = []
			h = []
			for i in List(headers):
				curr = 65
				if i[-1]=="}":
					n = i.find("{")
					if n>=0:
						curr = int(i[n+1:-1])
						#print(curr)
						h.append(i[:n])
				else:
					h.append(i)
					
				w.append(Int(curr, 0))
			
			assert len(w)==len(headers) and len(w)==len(h)
			return w, h		
				
		def ParseLine(h, expectedlen):
			s = Str(h).split("|")
			N = len(s)
			
			if N != expectedlen:
				if expectedlen < 0 and N < 2:
					ERR(f"expected more than one column in header '{h}', but got {N} column(s)")
				elif expectedlen >= 0:
					ERR(f"expected exaclty {expectedlen} column(s) in line '{h}', but got {N} column(s)")
			
			r = []
			o = ""
			for i in s:
				t = Trim(i, False)
				o += ("     " if expectedlen < 0 else "  ") + t + ("\n" if expectedlen < 0 else " | ") 
				r.append(t)
		
			Dbg(verbose, str(o), 3)
			
			return r
		
		def CheckLine(i, expected):
			Check(i<len(planlist),       f"i={i} < len of planlist={len(planlist)}") 
			Check(planlist[i]==expected, f"planlist missing tag '{expected}' at line {i}, got='{planlist[i]}'")
		
		def CheckContent(elem):
			if Str(elem)!=elem.lower():
				ERR(f"elem '{elem}' must be all-lower-case")
				
			t = s.get(Str(elem))
			Check(isinstance(t, list), f"planlist missing {elem.upper()} structure")
						
		N = len(List(planlist))
		if N < 7:
			ERR("planlist too short, expected at least four lines with COUSEPLAN/HEAD/CONTENT/[REFS]/END")
		
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
			i = Str(Trim(planlist[j]))
			
			if i=="NOTES":
				assert not s.get('content')
				s['content']=curr
				curr = []
			elif i=="REFS":
				assert not s.get('notes')
				s['notes']=curr
				curr = []
			elif i=="END":
				assert not s.get('refs')
				s['refs']=curr
				curr = None
		
				e = True
				break
				
			curr.append(i)
		
		Check(curr is None, 	"plainlist missing END tag")
		CheckContent('content')
		CheckContent('notes')
		CheckContent('refs')
		
		parsed = []
		for i in s['content']:
			l = ParseLine(i, M)
			Dbg(verbose, str(l), 2)
			parsed.append(l)
			
		s['parsed'] = parsed
	
		return s

	def GenerateHtml(headers, widths, parsed, notes, fullhtmldoc):
		def HtmlEncode(s):
			return escape(Str(s, False))
		
		def StyleSheet():
			return """
			<style type='text/css'> 
				.ECE_coursebuilder_table                    { background-color:white; border-collapse:collapse; text-align:center }
				.ECE_coursebuilder_table th                 { background-color:black; color:white;  } 
				.ECE_coursebuilder_table th, .ECE_coursebuilder_table td { padding:5px; border:1px solid black; }
				.ECE_coursebuilder_table tr:nth-child(even) { background: #DDD;  }
				.ECE_coursebuilder_table tr:nth-child(odd)  { background: white; }
			</style>
			""".replace("\t\t\t", "")
		
		def GenerateRow(headers, widths, type):
			assert len(List(headers))==len(List(widths))
			assert Str(type)=="th" or type=="td"
			
			html = "\t\t<tr>\n"	
			for i in zip(List(headers), List(widths)):
				Tuple(i)
				elem = HtmlEncode(i[0])
				assert Int(i[1])>=0
				w = f" width='{Int(i[1])}'" if type=="th" else ""
				html += f"\t\t\t<{type}{w}>{elem}</{type}>\n" 
			html += "\t\t</tr>\n"
			return html
		
		M = len(List(headers))
		html = StyleSheet()

		for i in List(notes):
			html += i + "<br>\n"
		
		if len(notes)>0:
			html += "<br>\n"

		html += "<table class='ECE_coursebuilder_table'>\n"
		html += "\t<tbody>\n"
				
		html += GenerateRow(headers, widths, "th")	

		for j in List(parsed):
			assert len(List(j))==M
			html += GenerateRow(j, widths, "td")	
			
		html += "\t</tbody>\n"
		html += "</table>\n"
		
		if fullhtmldoc:
			html = MkHtmlPage(html)
		
		Dbg(verbose, f"  {Col('YELLOW')}FOUND a  {len(parsed)} x {len(headers)}  table (rows x columns){ColEnd()}")

		return html
		
	try:	
		verbose = 0
		planfile = "plan.txt"
		outputfile = "plan.html" 
		
		parser = ArgumentParser(prog=argv[0], epilog="version 0.2")
		parser.add_argument("-v", default=verbose,    action="count",      help= "increase output verbosity, default={verbose}\n")
		parser.add_argument("-t", default=False,      action="store_true", help=f"generate simple table (witouth <html> <body> etc tags), default=False\n")
		parser.add_argument("-p", default=planfile,   type=str,            help=f"planfile, default='{planfile}'\n")
		parser.add_argument("-o", default=outputfile, type=str,            help=f"outputfilt, default='{outputfile}\n")
		args = parser.parse_args()
				
		verbose = Int(args.v)
				
		planfile = Str(args.p)
		outputfil = Str(args.o)
		
		Dbg(verbose, f"{Col('PURPLE')}GENERATING html plan from file '{planfile}..{ColEnd()}")

		structure = ParseStructure(LoadText(planfile))		
	
		Dbg(verbose, str(structure['headers']), 2)
		html = GenerateHtml(structure['headers'], structure['widths'], structure['parsed'], structure['notes'], not args.t)
		
		with Outputfile(outputfil) as f:
			f.write(html)
		
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
		
	except Exception as ex:
		HandleException(ex)

# example from: https://www.html.am/html-codes/tables/table-background-color.cfm
"""
<!-- Start Styles. Move the 'style' tags and everything between them to between the 'head' tags -->
	
	<style type="text/css">
	.ECE_coursebuilder_table { background-color:#eee;border-collapse:collapse; }
	.ECE_coursebuilder_table th { background-color:#000;color:white;width:50%; }
	.ECE_coursebuilder_table td, .ECE_coursebuilder_table th { padding:5px;border:1px solid #000; }
	</style>
	
	<!-- End Styles -->
	<table class="ECE_coursebuilder_table">
	<tr>
	<th>Table Header</th><th>Table Header</th>
	</tr>
	<tr>
	<td>Table cell 1</td><td>Table cell 2</td>
	</tr>
	<tr>
	<td>Table cell 3</td><td>Table cell 4</td>
	</tr>
	</table>

	<table class="ECE_coursebuilder_table">
		<tbody>
			<tr>
				<th>Table Header</th><th>Table Header</th>
			</tr>
			<tr>
				<td>Table cell 1</td><td>Table cell 2</td>
			</tr>
			<tr>
				<td>Table cell 3</td><td>Table cell 4</td>
			</tr>
		</tbody>
	</table>
	"""		
