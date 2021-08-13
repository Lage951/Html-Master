#!/usr/bin/env python3

from Utils.dbg import ERR, WARN, isBool, isStr, isInt, isNatural, isTuple, isList, isDict
from Utils.colors import Col, ColEnd
from Utils.mkutils import HandleException, Dbg, MkHtmlPage, Outputfile, Str

from sys import argv, stderr
from os import listdir
from os.path import join, isfile, isdir
from argparse import ArgumentParser

from urllib.request import urlretrieve

if __name__ == '__main__':

	outputstr = ""

	def Print(msg, outputfile):
		global outputstr
		assert isStr(msg)
		outputstr += msg + "\n"
    
	def Find(root, excludepat):
		assert isList(excludepat)

		tree = {}
		tree['trees'] = []
		tree['files'] = []
				
		for i in listdir(Str(root)):
			if i is not None:				
				d = join(root, Str(i))
				if Str(d)[0:2]=="./":
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
			assert isNatural(level)
			assert isStr(tab)
			assert isBool(isDir)
			
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
				assert Str(linkurl).find("'") < 0

				if testurls:
					sfx = linkurl.split(".")[-1]
					if sfx!="py":
						#print(f"WEB GET test {linkurl}..")
						try:
							# wget: download(linkurl, bar=None)
							urlretrieve(linkurl, filename=None)
						except Exception as ex:
							#PrettyPrintTracebackDiagnostics(ex)
							print(f"{Col('LRED UNDERLINE')}EXCEPTION:{ColEnd()}{Col('LRED')} {ex}{ColEnd()}", stderr)
							WARN(f"ignore test on link {linkurl}")
				
				return linkurl
			
			assert isStr(url)
			assert isBool(isDir)
			assert isTuple(i)
			assert isBool(bsfileidmode)
			
			if isDir:
				return i[0]

			assert isStr(i[0])
			assert isStr(i[1])
			
			if bsfileidmode:
				filename = Str(i[1].replace("/","%2f").replace(" ","%20"))
				assert filename.find("'") < 0
				assert filename.find('"') < 0				
				#    <a href="/d2l/common/dialogs/quickLink/quickLink.d2l?ou={orgUnitId}&amp;type=coursefile&amp;fileId=Kursusfiler%2fEksamen%2fScreenshot_mathcad_navn-og-studienummer.jpg" target="_self">dsf</a>
				
				orgUnitId = "{orgUnitId}"
				if ouid > 0:
					orgUnitId = str(ouid)
				assert isStr(orgUnitId)
				
				r = '<a href="/d2l/common/dialogs/quickLink/quickLink.d2l?ou=' + orgUnitId + '&amp;type=coursefile&amp;fileId='+filename+'" target="_self">'+i[0]+'</a>'
			else:
				linkurl = CheckUrl(url + "/" + i[1])
				assert linkurl.find("'") < 0
				r = f"<a href='{linkurl}'>{i[0]}</a>"			
			return r

		assert isTuple(i)
		assert isStr(i[0])
		nbsp = "&nbsp;"
		
		tab  = Tab(4*level, nbsp if htmlmode else "  ")
		link = Link(i, isDir) if htmlmode else i[0]
		#pre  = "<code>"         if htmlmode else ""
		#post = "</code>"        if htmlmode else ""
		pre  = f"<span style=\"font-family: 'courier new', courier, sans-serif\">" if htmlmode else ""
		post = "</span>"         if htmlmode else ""
		
		assert isTuple(tab)
		r = pre + tab[0] + link + tab[1] + Newline() + post
		
		Print(r, outputfile)
		return r

	def PrintTree(tree, level=0):
		assert isDict(tree)	
		assert isStr(url)		
		assert isBool(htmlmode)

		files=0
		dirs=0
		
		for j in ['trees', 'files']:
			t = tree[j]
			assert isList(t)
			
			d = sorted(tree[j])
			assert isList(d)
	
			for i in d:
				isdict = isinstance(i[1], dict)
				assert isTuple(i)
				assert isdict == (j=='trees')
				PrintItem(i, level, isdict)
				files += 1
				if j=='trees':
					r = (PrintTree(i[1], level+1))
					assert isTuple(r)		
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
		outputfile = None
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
		
		assert isInt(args.v)
		verbose = int(args.v)
		
		testurls = args.t
		assert isBool(testurls)
		if testurls:
			WARN("test urls not implemented yet")

		htmlmode = not args.plain
		assert isBool(htmlmode)
	
		header = Str(args.header, False)

		url = Str(args.url)
		if url[-1]=='/':
			ERR("no trailing '/' in url, please remove")

		bsfileidmode = args.bsfileidmode
		assert isBool(bsfileidmode)
	
		ouid = Str(args.ouid, False)
		if len(ouid)>0:
			ouid = int(ouid)
		else:
			ouid = -1
		assert isInt(ouid)

		excludepath += "," + Str(args.excludepath)
		assert excludepath.find(" ") < 0
		if excludepath[-1]==",": 
			excludepath=excludepath[:-1]
		excludepat = excludepath.split(",")
	
		#if bsfileidmode and len(url)>0:
		#	ERR("cannot specify -url and -bsfileidmode at the same time")
		if ouid>0 and not bsfileidmode:
			ERR("canot specify -ouid without -bsfileidmode")
	
		root = "./"
		Dbg(verbose, f"{Col('PURPLE')}GENERATING html file tree from root '{root}'" + (("" if bsfileidmode else f", (url='{url}')")  if verbose > 0 else "") + f"..{ColEnd()}")

		tree = Find(root, excludepat)		
		
		outputfile = None
		#outputfile = Outputfile(args.o)
		
		if htmlmode and len(header)>0:
			Print("<h3>" + header + "</h3>\n", outputfile)

		(files, dirs) = PrintTree(tree)
		Dbg(verbose, f"  {Col('YELLOW')}FOUND  files={files},  dirs={dirs}{ColEnd()}")
	
		html = outputstr
		if htmlmode:
			html = MkHtmlPage(html)
		
		with Outputfile(args.o) as f:
			f.write(html)
				
		Dbg(verbose, f"{Col('PURPLE')}DONE{ColEnd()}")
			
	except Exception as ex:
		HandleException(ex)
