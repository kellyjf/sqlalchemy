

reset:
	rm -f portuguese.sqlite ;\
	./load.py ;\
	./dic.py ;\
	./camb.py ;\
	sqlite3 portuguese.sqlite < views.sql 

quick:
	rm -f portuguese.sqlite ;\
	./load.py --quick ;\
	./dic.py ;\
	./camb.py ;\
	sqlite3 portuguese.sqlite < views.sql 

reload:
	./load.py -r


