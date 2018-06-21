graph: graph.py
	python3 graph.py --graph='$(g)'

face: main.py
	python3 face.py

clean:
	rm *.pyc
	rm *~
