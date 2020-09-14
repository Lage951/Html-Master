DAV = /mnt/Dav/ITMAL
DIR = $(DAV)/Fildeling
TEXDIR=/home/cef/ASE/ITMAL/TeX
EXCLUDEPAT=--exclude='*~' --exclude='.ipynb*' --exclude='__pycache__'

pub: clean
	@ echo "CP lessons, local.."
	@ #cp -v -u $(TEXDIR)/lesson01.pdf L01/lesson01.pdf
	@ #cp -v -u $(TEXDIR)/lesson02.pdf L02/lesson02.pdf
	@ cp -v -u $(TEXDIR)/lesson03.pdf L03/
	@ echo "CP lessons, remote.."
	@ cp -v -u -r L?? $(DIR)
	@ #echo  cp -v -u -r `ls L??| grep -v ".ipynb" | grep -v "__pychache__"` $(DIR)
	@ echo "CP libitmal, remote.."
	@ cp -v -u -r Etc libitmal $(DIR)

update:
	@ git status
	@ echo -n "Server itu git pull.." && (ssh itu "cd F20_itmal && git pull") || echo "failed"
	@ echo "ALL OK"

check:
	@ grep itundervisining L??/* -R || echo "OK, no itundervisining.."
	@#grep "blackboard.au.dk" L??/* -R	
	grep "p\." L02/*.ipynb -R

hasDAV:
	@ cat /proc/mounts | grep $(DAV) >/dev/null || mount $(DAV) 
	@# cat /proc/mounts | grep $(DAV) >/dev/null || (echo "ERROR: DAV dir $(DAV) not mounted" && false)	

diff: hasDAV
	diff -dwqr -x '*~' -x '.git*' -x 'Makefile' -x 'Solutions' -x 'Old' -x 'Src' -x 'datasets' . $(DIR) || echo "DIFFS(1)!"
	@#diff  $(TEXDIR)/lesson01.pdf L01/lesson01.pdf || echo "DIFFS(2)!"
	@#diff  $(TEXDIR)/lesson02.pdf L02/lesson02.pdf || echo "DIFFS(3)!"
	@ echo "OK"

cleanremote: hasDAV
	@ find $(DIR) -iname '.ipynb_checkpoints' -exec rm -rf {} \; || true
	@ find $(DIR) -iname '__pycache__' -exec rm -rf {} \; || true
	@ find $(DIR) -iname '*~' -exec rm -rf {} \; || true

clean: cleanremote
	@ find . -iname '.ipynb_checkpoints' -exec rm -rf {} \; || true
	@ find . -iname '__pycache__' -exec rm -rf {} \; || true
	@ find . -iname '*~' -exec rm -rf {} \; || true
		