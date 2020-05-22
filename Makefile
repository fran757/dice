QUEST = 1e 1h 2a 2b 2c
OUT = $(foreach Q, $(QUEST), data/output-$Q.txt)

# replace with appropriate python executable, or see the `setup` directive below
PYTHON = src/.venv/bin/python
N = 10000

# compile the rapport, including code output
all: math/rapport.tex data/output-1c.txt $(OUT)
	pdflatex -output-directory math rapport.tex

# specific directive for this question
data/output-1c.txt: %: data/game-1e.yaml src
	$(PYTHON) -m src -g data/game-1e.yaml -o $@ -n $N passive basic

# run script with specific game file for each question
$(OUT): data/output-%.txt: data/game-%.yaml src
	$(PYTHON) -m src -g data/game-$*.yaml -o $@ -dn $N passive basic optimal_$* dynamic

# setup the python environment (assuming python >= 3.7)
setup:
	[ -d src/.venv ] || python -m venv src/.venv
	. src/.venv/bin/activate
	pip install -r src/requirements.txt

# remove output files (e.g. to force code execution directives)
clean:
	rm data/output* || true
