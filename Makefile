FILES_IPYNB=$(sort $(wildcard L??/*.ipynb) $(wildcard L??/*/*.ipynb))
FILES_PY=$(sort $(wildcard libitmal/*.py))
FILES_WEB=$(sort $(wildcard Html/*.html))

CHECK_FOR_TEXT=grep "$1" $(FILES_IPYNB) -R || echo "  OK, no '$1'.."

.PHONY:all
all:
	@ echo "Doing nothing!"
	@ echo "  This makefile just for parsing and checking,"
	@ echo "  enjoy .c"

.PHONY:check
check:
	@ echo "CHECKING (for various no-no's in .ipynb files).."
	@ echo "  FILES: $(FILES_IPYNB)"
	@ $(call CHECK_FOR_TEXT,itundervisining) 
	@ $(call CHECK_FOR_TEXT,BB-Cou-UUVA) 
	@ $(call CHECK_FOR_TEXT,blackboard.au.dk) 
	@ $(call CHECK_FOR_TEXT,blackboard) 
	@ $(call CHECK_FOR_TEXT,Blackboard) 
	@ $(call CHECK_FOR_TEXT,dk/GITMAL/)
	@ $(call CHECK_FOR_TEXT,27524)# E21
	@ $(call CHECK_FOR_TEXT,53939)# F22
	@ $(call CHECK_FOR_TEXT,70628)# E22
	@ $(call CHECK_FOR_TEXT,91157)# F23
	@ $(call CHECK_FOR_TEXT,91157)# F23
	@ $(call CHECK_FOR_TEXT,\\\\mbox)# mbox => mathrm og textrm
	@ $(call CHECK_FOR_TEXT,\\\\newcommand)# => newcommand => renewcommand
	@ $(call CHECK_FOR_TEXT,\\\\renewcommand)
	@ echo "DONE: all ok"

.PHONY:checkpages
checkpages:
	@ echo "CHECKING (for pages).."
	@ egrep --color "p\.\[\ ]+" $(FILES_WEB) $(FILES_IPYNB) || true
	@ egrep --color "[ ][p]+[ ]+[0-9]+" $(FILES_WEB) $(FILES_IPYNB) || true
	@ egrep --color "[ ][p]+[0-9]+" $(FILES_WEB) $(FILES_IPYNB) || true
	@ echo "WEBPAGES.."
	@ egrep --color "p\.[0-9]+" $(FILES_WEB) 
	@ echo "IPYNB FILES.."
	@ egrep --color "p\.[0-9]+" $(FILES_IPYNB)

.PHONY:test
test:
	@#for var in $(FILES_PY); do echo $$var $@; done
	@#libitmal/dataloaders.py
	libitmal/kernelfuns.py
	libitmal/utils.py
	libitmal/versions.py	
	libitmal/nbmerge.py L01/intro.ipynb L02/performance_metrics.ipynb L03/supergruppe_diskussion.ipynb -o testmerge.ipynb

.PHONY:pull
pull:
	@ echo "PULL" | tee -a log_pull.txt
	@ date        | tee -a log_pull.txt
	@ git pull 2>>log_pull.err | tee -a log_pull.txt

#PARSED=$(foreach f,$(FILES_IPYNB),$(shell (python -m json.tool $(f) 1>/dev/null 2>/dev/null && echo >&2 "OK $(f)")|| (echo >&2 $(f) && python -m json.tool $(f))))
#.PHONY:parsecheck
#parsecheck:
#	@#echo PARSE_ERRORS=$(PARSED)
#	@#cat $(PARSED) | tr ' ' '\n' # |  xargs -I % sh -c 'echo %;'

zoom:
	@# https://aarhusuniversity.zoom.us/j/4012595210
	@# /usr/bin/zoom https://aarhusuniversity.zoom.us/j/4012595210
	@# xdg-open "zoommtg://zoom.us/join?action=join&confno=401259521"
	xdg-open https://aarhusuniversity.zoom.us/j/4012595210

.PHONY:clean
clean:
	@ find . -iname ".ipynb_checkpoints" -exec rm -r {} \;
