run: main.py
	python3 main.py --graph='$(g)'

clean:
	rm *.pyc
	rm *~
