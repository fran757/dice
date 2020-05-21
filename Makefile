QUEST = 1e 1h 2a 2b 2c
OUT = $(foreach Q, $(QUEST), data/output-$Q.txt)
PYTHON = src/.venv/bin/python
N = 10000

all: math/rapport.tex data/output-1c.txt $(OUT)
	pdflatex -output-directory math rapport.tex

data/output-1c.txt: %: data/game-1e.yaml src
	$(PYTHON) -m src -g data/game-1e.yaml -o $@ $N passive basic

$(OUT): data/output-%.txt: data/game-%.yaml src
	$(PYTHON) -m src -g data/game-$*.yaml -o $@ -d $N passive basic optimal_$* dynamic

clean:
	rm data/output* || true
