#PYFILE  = $(wildcard *.py) $(wildcard Utils/*.py)

PYCOURSE    = mk_course.py
PYFILETREE  = mk_filetree.py
PYPLAN      = mk_plan.py

PWD = $(shell pwd)
COURSEFILES = ITMAL_E21
MKDIFF=printf "DIFF Ref/%-10s Test/  .. " $1 && colordiff -dw Refs/$1 Test/ && echo "DIFF OK" && rm Test/$1

build:
	@ $(PYCOURSE) -c $(COURSEFILES)/course.tex  -v  -o ../../Html/ 
	@ $(PYPLAN)   -p $(COURSEFILES)/plan.txt    -v  -o ../../Html/plan.html
	@ cd ../.. &&    $(PWD)/$(PYFILETREE)       -v  -o Html/filetree.html

sync: build
	@ echo "SYNC.."
	@ #nmap -T5  -p 22 si | grep -v "Note: Host seems down" >/dev/null
	@ ssh si "cd ITMAL_E21 && rm -f Html/*.html && git pull" 
	@ # cd ../../ && scp  -q -C -r Html si:ITMAL_E21/
	@ echo "SYNC..DONE"
	

TESTARGS=-v
test: clean
	@ cd Test && $(PWD)/$(PYCOURSE)   $(TESTARGS)
	@ cd Test && $(PWD)/$(PYPLAN)     $(TESTARGS) 
	@ cd Test && $(PWD)/$(PYFILETREE) $(TESTARGS) 
	@ $(call MKDIFF,L00.html)
	@ $(call MKDIFF,L01.html)
	@ $(call MKDIFF,plan.html)
	@ $(call MKDIFF,tree.html)

edit:
	joe $(COURSEFILES)/course.tex 
	
clean:
	@ rm -f Test/*.html ../Html/L??.html 
