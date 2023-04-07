

reset:
	rm -f portuguese.sqlite ;\
	./load.py ;\
	sqlite3 portuguese.sqlite < views.sql 

cached:
	rm -f portuguese.sqlite ;\
	./load.py --cached ;\
	sqlite3 portuguese.sqlite < views.sql 



