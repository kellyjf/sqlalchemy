

reset:
	rm -f portuguese.sqlite ;\
	./load.py ;\
	./dic.py ;\
	sqlite3 portuguese.sqlite < views.sql 

reload:
	./load.py -r


