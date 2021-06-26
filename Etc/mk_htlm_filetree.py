#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, PrettyPrintTracebackDiagnostics, DiagStdErr #, Diagnostics, isBool, isInt, isStr, isTuple, isList, isDict
from Utils.colors import Col, ColEnd

from sys import stderr
from os import listdir
from os.path import join, isfile, isdir
from argparse import ArgumentParser
from urllib.request import urlretrieve

if __name__ == '__main__':
	
	# https://gitlab.au.dk/au204573/itmal/-/raw/master/L01/modules_and_classes.ipynb
	#url = "https://gitlab.au.dk/au204573/itmal/-/raw/master"
	
	url = "https://itundervisning.ase.au.dk/itmal"
	welcome = "ITMAL Backend File Structure"
	htmlmode = True
	testurls = False

	def isTuple(t, n=2):
		return isinstance(t, tuple) and len(t)==n
		
	
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
					isDir = isdir(d)
					t = 'trees' if isDir else 'files'
					tree[t].append((i, Find(d, excludepat) if isDir else d))
					
		return tree

	def PrintItem(i, level, isDir):
		def Tab(level, tab):			
			assert isinstance(level, int) and level>=0
			assert isinstance(tab, str)
			assert isinstance(isDir, bool)
			
			#if htmlmode:
			#	return "", ""
			#	#return f"<p style='padding-left: {(level+1)*40}px;'>", "</p>"
		
			t = ""
			for n in range(level):
				t += tab
		
			return t, ""
			
		def Newline():
			return "<br>" if htmlmode else ""

		def Link(i, isDir):
			def CheckUrl(linkurl):
				assert isinstance(linkurl, str)
				assert linkurl.find("'") < 0

				if testurls:
					sfx = linkurl.split(".")[-1]
					if sfx!="py":
						#print(f"WEB GET test {linkurl}..")
						try:
							# wget: download(linkurl, bar=None)
							urlretrieve(linkurl, filename=None)
						except Exception as ex:
							#PrettyPrintTracebackDiagnostics(ex)
							print(f"{Col('LRED UNDERLINE')}EXCEPTION:{ColEnd()}{Col('LRED')} {ex}{ColEnd()}")
							WARN(f"ignore test on link {linkurl}")
				
				return linkurl
			
			assert isinstance(url, str)
			assert isinstance(isDir, bool)
			assert isTuple(i)
			
			if isDir:
				return i[0]

			assert isinstance(i[0], str)
			assert isinstance(i[1], str)		
			
			linkurl = CheckUrl(url + "/" + i[1])
			assert linkurl.find("'") < 0
			r = f"<a href='{linkurl}'>{i[0]}</a>"		
			
			
			return r

		assert isTuple(i)
		assert isinstance(i[0], str)		
		nbsp = "&nbsp;"
		
		tab  = Tab(4*level, nbsp if htmlmode else "  ")
		link = Link(i, isDir)    if htmlmode else i[0]
		#pre  = "<code>"         if htmlmode else ""
		#post = "</code>"        if htmlmode else ""
		pre  = f"<span style=\"font-family: 'courier new', courier, sans-serif\">" if htmlmode else ""
		post = "</span>"         if htmlmode else ""
		
		assert isTuple(tab)
		r = pre + tab[0] + link + tab[1] + Newline() + post
		
		print(r)
		return r

	def PrintTree(tree, level=0):
		assert isinstance(tree, dict)	
		assert isinstance(url, str)		
		assert isinstance(htmlmode, bool)

		for j in ['trees', 'files']:
			t = tree[j]
			assert isinstance(t, list)
			
			d = sorted(tree[j])
			assert isinstance(d, list)				
	
			for i in d:
				assert isTuple(i)
				assert isinstance(i[1], dict) == (j=='trees')
				PrintItem(i, level, isinstance(i[1], dict))
				if j=='trees':
					PrintTree(i[1], level+1)

	def Usage(msg=""):
		print("Usage: mk_html_filetree.py [-v] [-plain] [-url <url>]") 
		print("  version 0.1")
		print("Args:")
		print("  -v: verbose, default=0")
		print("  -url: url to prefix with with not trailing '/', default={url}")
		if len(msg)>0:
			WARN(msg)
		return 1
		
	try:			
		parser = ArgumentParser()
		parser.add_argument("-v",     default=0,            action="count",      help="increase output verbosity, default=0\n")
		parser.add_argument("-t",     default=testurls,     action="store_true", help=f"test link by url download, default={testurls}\n")
		parser.add_argument("-plain", default=not htmlmode, action="store_true", help=f"output in plain mode, default={not htmlmode}\n")
		parser.add_argument("-url",   default=url,          type=str,            help=f"url to prefix with, default={url}\n")
		args = parser.parse_args()
		
		htmlmode = not args.plain
		assert isinstance(htmlmode, bool)
		testurls = args.t
		assert isinstance(testurls, bool)			

		url = args.url
		assert isinstance(url, str)
		if url[-1]=='/':
			exit(-Usage("ERROR: no trailing '/' in url please"))	
			
		tree = Find("./", ["git", "Old", "ipynb_checkpoints", "~", "__pycache__"])
		
		if htmlmode:
			print("<!DOCTYPE html>\n<html>\n<body>\n")
			print("<h3>" + welcome + "</h3>\n")

		PrintTree(tree)
	
		if htmlmode:
			print("\n</body></html>")
	
	except Exception as e:
		DiagStdErr(stderr)
		PrettyPrintTracebackDiagnostics(e)
		exit(-1)