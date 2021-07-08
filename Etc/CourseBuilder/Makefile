#PYFILE  = $(wildcard *.py) $(wildcard Utils/*.py)

PYCOURSE    = mk_course.py
PYFILETREE  = mk_filetree.py
PYPLAN      = mk_plan.py

PWD = $(shell pwd)
COURSEFILES = ITMAL_E21
MKDIFF=colordiff -dw Refs/$1 $1 && echo "DIFF OK" && rm $1

build:
	@ $(PYCOURSE) -c $(COURSEFILES)/course.tex  -v  -o ../../Html/
	@ $(PYPLAN)   -p $(COURSEFILES)/plan.txt    -v  -o ../../Html/plan.html
	@ cd ../.. && $ $(PWD)/$(PYFILETREE)        -v  -o Html/filetree.html

TESTARGS=-v -v
test:
	@ $(PYCOURSE) -c Test/course.tex   $(TESTARGS) -o ./
	@ $(call MKDIFF,L00.html)
	@ $(call MKDIFF,L01.html)
	@ $(PYPLAN) -p Test/plan.txt       $(TESTARGS) -o plan.html
	@ $(call MKDIFF,plan.html)
	@ cd Test && $(PWD)/$(PYFILETREE)  $(TESTARGS) -o $(PWD)/tree.html
	@ $(call MKDIFF,tree.html)

sync: build
	cd .. && scp -r Html/*.html si:ITMAL_E21/Html
	ssh si "cd ITMAL_E21 && git pull"

edit:
	joe $(PYCOURSE)

	
clean:
	@ rm -f index.html out.html test.html ../Html/L??.html 

#get:
#	wget https://gitlab.au.dk/au204573/brightspacemods/-/raw/master/JS/demo.js
#
#sshfs:
#	echo "not implemented yet"	
#	
#ae:
#	sudo tail -f /var/log/apache2/error.log

