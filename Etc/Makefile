PYFILE  = $(wildcard *.py) $(wildcard Utils/*.py)
PYCOURSE = mk_course.py
TESTFILETREEDIR = ~/ASE/ITMAL/itmal
PWD = $(shell pwd)

testplan:
	@ $(PYCOURSE) -v -v -o index.html
	@# colordiff -dw Refs/plan.ref index.html 

edit:
	joe $(PYCOURSE)

clean:
	@ rm -f log.txt out.txt index.html 
