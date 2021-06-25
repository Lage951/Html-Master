F=mk_htlm_filetree.py

test:
	@$(F) 
	@ echo
	@cd .. && Etc/$(F) -plain

itmal:
	@ rm -f index.html
	@ cd .. && Etc/$(F)  > Etc/index.html 
	head index.html
	scp index.html si:Itmal_E21/
	ssh  si "cd Itmal_E21 && git pull"
	
edit:
	joe $(F)
	
clean:
	@ rm -rf index.html __pycache__ Utils/__pycache__