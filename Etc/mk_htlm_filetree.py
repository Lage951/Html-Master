#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, PrettyPrintTracebackDiagnostics #, Diagnostics, isBool, isInt, isStr, isTuple, isList, isDict

from os import listdir
from os.path import join, isfile, isdir
from argparse import ArgumentParser

if __name__ == '__main__':
	# https://gitlab.au.dk/au204573/itmal/-/raw/master/L01/modules_and_classes.ipynb
	#url = "https://gitlab.au.dk/au204573/itmal/-/raw/master"
	url = "https://itundervisning.ase.au.dk/itmal"
	welcome = "ITMAL Backend File Structure"
		
	def Usage(msg=""):
		print("Usage: mk_html_filetree.py [-v] [-plain] [-url <url>]") 
		print("  version 0.1")
		print("Args:")
		print("  -v: verbose, default=0")
		print("  -url: url to prefix with with not trailing '/', default={url}")
		if len(msg)>0:
			print(msg)
		return 1
	
	def Find(root, excludepat):
		assert isinstance(root, str)
		assert isinstance(excludepat, list)

		tree = {}
		tree['trees'] = []
		tree['files'] = []
				
		for i in listdir(root):
			if i is not None:
				assert isinstance(i, str)
				
				d = join(root, i)
				assert isinstance(d, str)
				if d[0:2]=="./":
					d = d[2:]
				
				skip = False
				for j in excludepat:
					if d.find(j)>=0:
						skip = True
						break

				if not skip:
					dir = isdir(d)
					t = 'trees' if dir else 'files'
					tree[t].append((d, Find(d, excludepat) if dir else root))
					
		return tree

	def PrintTree(url, tree, htmlmode, level=0):
		def isTuple(t, n):
			return isinstance(t, tuple) and len(t)==n
		
		def PrintItem(url, i, htmlmode):
			def Tab(level, tab):
				assert isinstance(level, int) and level>=0
				assert isinstance(tab, str)
				
				t = ""
				for n in range(level):
					t += tab
				return t
				
			def Newline(htmlmode):
				return "<br>" if htmlmode else ""

			def Link(url, i):
				url += "/" + i
				r = f"<a href='{url}'>{i}</a>"
				return r

			assert isinstance(i, str)
			assert isinstance(htmlmode, bool)
			
			nbsp = "&nbsp;&nbsp;&nbsp;&nbsp;"
			
			tab  = Tab(level, nbsp if htmlmode else "  ")
			link = Link(url, i)    if htmlmode else i
			pre  = "<code>"        if htmlmode else ""
			post = "</code>"       if htmlmode else ""
			
			r = pre + tab + link + Newline(htmlmode) + post
			
			print(r)
			return r

		assert isinstance(url, str)
		assert isinstance(tree, dict)
		assert isinstance(tree['trees'], list)	
		assert isinstance(tree['files'], list)	

		d = sorted(tree['trees'])
		assert isinstance(d, list)				
		
		for i in d:
			assert isTuple(i, 2)
			PrintItem(url, i[0], htmlmode)
			PrintTree(url, i[1], htmlmode, level+1)
		
		f = sorted(tree['files'])
		for i in f:
			assert isTuple(i, 2)
			PrintItem(url, i[0], htmlmode)

	try:			

		htmlmode = True
		
		parser = ArgumentParser()
		parser.add_argument("-v",     default=0,            action="count",      help="increase output verbosity, default=0\n")
		parser.add_argument("-plain", default=not htmlmode, action="store_true", help=f"output in plain mode, default={not htmlmode}\n")
		parser.add_argument("-url",   default=url,          type=str,            help=f"url to prefix with, default={url}\n")
		args = parser.parse_args()
		
		assert isinstance(args.url, str)
		if args.url[-1]=='/':
			exit(-Usage("ERROR: no trailing '/' in url please"))
			
		tree = Find("./", ["git", "Old", "ipynb_checkpoints", "~", "__pycache"])
		
		if htmlmode:
			print("<!DOCTYPE html>\n<html>\n<body>\n")
			print("<h3>" + welcome + "</h3><br>\n")

		PrintTree(url, tree, not args.plain)
	
		if htmlmode:
			print("\n</body></html>")
	
	except Exception as e:
		PrettyPrintTracebackDiagnostics(e)