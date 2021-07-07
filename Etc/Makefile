PYCOURSE=mk_course.py

all:
	$(PYCOURSE) -v 

edit:
	joe $(PYCOURSE)

sync:
	scp L??.html si:Itmal_E21/
	ssh si "cd Itmal_E21 && git pull"	
	
clean:
	@ rm -f out.html L??.html

#JSFILES = $(wildcard JS/*.js)
#PYFILE  = $(wildcard Py/*.py) $(wildcard Py/Utils/*.py)

#PYFILETREE  = Py/mk_htlm_filetree.py
#PYPLAN      = Py/mk_course_plan.py
#TESTFILETREEDIR = ~/ASE/ITMAL/itmal

#PWD = $(shell pwd)

#testplan:
#	@ $(PYPLAN) -v -v -o index.html
#	@ colordiff -dw Refs/plan.ref index.html 
#
#testfiletree:
#	@ $(PYFILETREE) -o index.html
#	@ cd $(TESTFILETREEDIR) && $(PWD)/$(PYFILETREE) -plain -o $(PWD)/out.txt
#	@ echo DONE TREE
#
#itmal:
#	@ rm -f index.html
#	cd .. && Etc/$(F) #> Etc/index.html 
#	head -n 40 index.html
#
#sync:
#	scp index.html si:Itmal_E21/
#	ssh  si "cd Itmal_E21 && git pull"	
#
#pub: all
#	@ echo "nothing"
#	
#all: #$(JSFILES:.js=.okj)
#	@#$(foreach i, $(PHPFILES), php -l $i;)
#	@ $(foreach i, $(JSFILES), echo "node -c $i"; node -c $i;)
#	@ git commit -a -m update && git push 
#
#get:
#	wget https://gitlab.au.dk/au204573/brightspacemods/-/raw/master/JS/demo.js
#
#sshfs:
#	echo "not implemented yet"	
#	
#ae:
#	sudo tail -f /var/log/apache2/error.log

