#!/usr/bin/env python3

from Utils.colors import Col, ColEnd
from Utils.mkutils import *

from sys import argv, stderr
from os import listdir
from os.path import join, isfile, isdir
from argparse import ArgumentParser

from urllib.request import urlretrieve

if __name__ == '__main__':

	outputstr = ""

	def CheckTuple(t, secondisstr=False):
		Check(len(Tuple(t)) ==2, "not a tuple with len=2")
		Check(len(Str(t[0], False))>=0, "tuple first not of string type")
		Check(isinstance(t[1], str) or (not secondisstr and isinstance(t[1], dict)), f"tuple second not of expected type(s), type={type(t[1])}") 
		return True

	def Print(msg, outputfile):
		global outputstr
		outputstr += Str(msg) + "\n"
    
	def Find(root, excludepat):
		tree = {}
		tree['trees'] = []
		tree['files'] = []
				
		for i in listdir(Str(root)):
			if i is not None:				
				d = join(root, Str(i))
				if Str(d)[0:2]=="./":
					d = d[2:]
				
				skip = False
				for j in List(excludepat):
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
			t = ""
			for n in range(Int(level)):
				t += Str(tab)
		
			return t, ""
			
		def Newline():
			return "<br>" if htmlmode else ""

		def Link(i, isDir):
			def CheckUrl(linkurl):
				assert Str(linkurl).find("'") < 0
				if Bool(testurls):
					sfx = linkurl.split(".")[-1]
					if sfx!="py":
						#print(f"WEB GET test {linkurl}..")
						try:
							# wget: download(linkurl, bar=None)
							urlretrieve(linkurl, filename=None)
						except Exception as ex:
							#PrettyPrintTracebackDiagnostics(ex)
							Warn(f"{Col('LRED UNDERLINE')}EXCEPTION:{ColEnd()}{Col('LRED')} {ex}{ColEnd()}")
							Warn(f"ignore test on link {linkurl}")
				
				return linkurl
			
			CheckTuple(i)
						
			if Bool(isDir):
				return Str(i[0])

			if Bool(bsfileidmode):
				filename = UrlQuote(Str(i[1]))
	
				orgUnitId = Str(str(ouid) if Int(ouid>0) else "{orgUnitId}")
			
				# From BS:   <a href="/d2l/common/dialogs/quickLink/quickLink.d2l?ou={orgUnitId}&amp;type=coursefile&amp;fileId=Kursusfiler%2fEksamen%2fScreenshot_mathcad_navn-og-studienummer.jpg" target="_self">dsf</a>
				
				r = '<a href="/d2l/common/dialogs/quickLink/quickLink.d2l?ou=' + orgUnitId + '&amp;type=coursefile&amp;fileId='+filename+'" target="_self">'+i[0]+'</a>'
			else:
				linkurl = CheckUrl(Str(url) + "/" + i[1])
				assert linkurl.find("'") < 0
				r = f"<a href='{linkurl}'>{i[0]}</a>"			
			return r

		CheckTuple(i)
		nbsp = "&nbsp;"
		
		tab  = Tab(4*level, nbsp if htmlmode else "  ")
		link = Link(i, isDir) if htmlmode else i[0]
		#pre  = "<code>"         if htmlmode else ""
		#post = "</code>"        if htmlmode else ""
		pre  = f"<span style=\"font-family: 'courier new', courier, sans-serif\">" if htmlmode else ""
		post = "</span>"         if htmlmode else ""
		
		CheckTuple(tab, True)
		r = pre + tab[0] + link + tab[1] + Newline() + post
		
		Print(r, outputfile)
		return r

	def PrintTree(tree, level=0):
		files=0
		dirs=0
		
		for j in ['trees', 'files']:
			t = List(Dict(tree)[j])
			d = List(sorted(tree[j]))
	
			for i in d:
				CheckTuple(i, False)
				isdict = isinstance(i[1], dict)
				assert isdict == (j=='trees')
				PrintItem(i, level, isdict)
				files += 1
				if j=='trees':
					r = Tuple((PrintTree(i[1], level+1)))
					files += r[0]
					dirs  += 1 + r[1]
		
		return (files, dirs)

	try:	
		# https://gitlab.au.dk/au204573/itmal/-/raw/master/L01/modules_and_classes.ipynb
		#url = "https://gitlab.au.dk/au204573/itmal/-/raw/master"
	
		verbose = 0	
		testurls = False
		htmlmode = True		
		header = "Backend file structure"
		url = "https://itundervisning.ase.au.dk/ITMAL_E21"		
		outputfile = "tree.html"
		bsfileidmode = False
		ouid = ""
		excludepath = "git,Old,ipynb_checkpoints,~,__pycache__"
		
		parser = ArgumentParser(prog=argv[0],  description="", epilog="version 0.1")
		parser.add_argument("-v",            default=verbose,      action="count",      help=f"increase output verbosity, default={verbose}\n")
		parser.add_argument("-t",            default=testurls,     action="store_true", help=f"test link by url download, default={testurls}\n")
		parser.add_argument("-plain",        default=not htmlmode, action="store_true", help=f"output in plain mode, default={not htmlmode}\n")
		parser.add_argument("-header",       default=header,       type=str,            help=f"header for output page, default='{header}'\n")
		parser.add_argument("-url",          default=url,          type=str,            help=f"url to prefix with (ending in '/'), default='{url}'\n")
		parser.add_argument("-o",            default=outputfile,   type=str,            help=f"output to this file (stdout==None), default='{outputfile}'\n")
		parser.add_argument("-bsfileidmode", default=bsfileidmode, action="store_true", help=f"anchor is Brightspace fileid link, default='{bsfileidmode}'\n")
		parser.add_argument("-ouid",         default=ouid,         type=str,            help=f"couse id when in bsfileidmode, default='{ouid}'\n")
		parser.add_argument("-excludepath",  default=excludepath,  type=str,            help=f"excludepath pattern, default='{excludepath}'\n")				
				
		args = parser.parse_args()
		
		verbose = Int(args.v)
		
		testurls = Bool(args.t)
		Check(not testurls, "test urls not implemented yet")

		htmlmode = not Bool(args.plain)
	
		header = Str(args.header, False)

		url = Str(args.url)
		Check(url[-1]!='/',"no trailing '/' in url, please remove")

		outputfile = Str(args.o)

		bsfileidmode = Bool(args.bsfileidmode)
	
		ouid = Str(args.ouid, False)
		ouid = Int(Int(int(ouid)) if len(ouid)>0 else -1, -1)

		excludepath += "," + Str(args.excludepath)
		assert excludepath.find(" ") < 0
		if excludepath[-1]==",": 
			excludepath=excludepath[:-1]
		excludepat = excludepath.split(",")
	
		#if bsfileidmode and len(url)>0:
		#	ERR("cannot specify -url and -bsfileidmode at the same time")
		Check( not( ouid>0 and not bsfileidmode), "canot specify -ouid without -bsfileidmode")
	
		root = "./"
		Dbg(verbose, f"{Col('PURPLE')}GENERATING html file tree from root '{root}'" + (("" if bsfileidmode else f", (url='{url}')")  if verbose > 0 else "") + f"..{ColEnd()}")

		tree = Find(root, excludepat)		
		
		if htmlmode and len(header)>0:
			Print("<h3>" + header + "</h3>\n", outputfile)

		(files, dirs) = PrintTree(tree)
		Dbg(verbose, f"  {Col('YELLOW')}FOUND  files={files},  dirs={dirs}{ColEnd()}")
	
		html = outputstr
		if htmlmode:
			html = MkHtmlPage(html)
		
		with Outputfile(outputfile) as f:
			f.write(html)
				
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
			
	except Exception as ex:
		HandleException(ex)
