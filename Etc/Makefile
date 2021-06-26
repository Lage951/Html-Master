F=mk_htlm_filetree.py
P=mk_course_plan.py

all: plan #itmal

test:
	@ $(F) 
	@ echo
	@ cd .. && Etc/$(F) -plain

plan:
	@ $(P) 
	
itmal:
	@ rm -f index.html
	cd .. && Etc/$(F) #> Etc/index.html 
	head -n 40 index.html

sync:
	scp index.html si:Itmal_E21/
	ssh  si "cd Itmal_E21 && git pull"
	
edit:
	joe $(P)
	
clean:
	@ rm -rf out.html index.html __pycache__ Utils/__pycache__