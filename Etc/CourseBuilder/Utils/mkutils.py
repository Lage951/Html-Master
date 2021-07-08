#!/usr/bin/env python3

from Utils.dbg import 	DiagStdErr, PrettyPrintTracebackDiagnostics
from sys import stdout, stderr

def isStr(t, checknonempty=True):
	assert isinstance(t, str),  f"exected string but got type='{type(t)}'"
	assert (not checknonempty) or (len(t)>0), f"string is empty, and this was unexpected"
	return t

def isBool(t):
	assert isinstance(t, bool), f"exected bool but got type='{type(t)}'"
	return t

def isInt(t, minval=0):
	assert isinstance(t, int), f"exected int but got type='{type(t)}'"
	assert t>=minval
	return t
	
def isList(t):
	assert isinstance(t, list), f"exected list but got type='{type(t)}'"
	return t

def isDict(t):
	assert isinstance(t, dict), f"exected dict but got type='{type(t)}'"
	return t

def isTuple(t, expectedlen=2):
	assert isinstance(t, tuple),f"exected tuple but got type='{type(t)}'"
	assert len(t)==isInt(expectedlen, 1)
	return t

def Check(expr, msg):
	isStr(msg)
	if not expr:
		Err("EXPRESSION NOT FULLFILLED: " + msg)

def Trim(s, checknonempty=True):
	s = isStr(s, isBool(checknonempty)).replace("\t"," ")
	s = s.strip()
	return s

def SuffixFrom(s, splitstr):
	n = isStr(s).rfind(isStr(splitstr))
	if n<0: 
		ERR(f"string '{s}' does not contain split string '{splitstr}' at all")
	return s[n+len(splitstr):]

def Dbg(verbose, msg, level=1):
	isInt(verbose)
	isStr(msg)
	isInt(level)
	if level <= verbose:
		print(msg, file=stderr)

def Outputfile(outputfile):
	assert outputfile is not None
	outputfile = isStr(outputfile).replace(" ", "_")	
	f = stdout if (outputfile is None or len(outputfile)==0 or outputfile=="None") else open(outputfile, 'w')
	return f

def LoadText(filename, timeout=4000, split=True):
	with open(isStr(filename), 'r', timeout) as f:
		c = f.read()
		if split:
			c = c.split("\n")
		return c

def MkHtmlPage(htmlcontent):
	assert isStr(htmlcontent).find("DOCTYPE")<0 and htmlcontent.find("<html>")<=0 and htmlcontent.find("<body>")<=0
	#bodystyle = "style='font-family: Verdana;font-size: 12pt;color: #494c4e;'"
	bodystyle = "style='font-family: times new roman, times, serif;font-size: 12pt;color: #424222;'"
	meta = "<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>"
	return f"<!DOCTYPE html>\n<html>\n{meta}\n<body {bodystyle}>\n" + htmlcontent + "\n</body>\n</html>"  

def HandleException(ex):
	try:
		assert isinstance(ex, Exception)
		DiagStdErr(stderr)
		PrettyPrintTracebackDiagnostics(ex)
	except:
		print(f"EXCEPTION: {ex} (and exception in exceptions handling)")
		
	exit(-1)