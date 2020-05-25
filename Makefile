QUEST = 1c 1e 1h 2a 2b 2c 2d1 2d
OUT = $(foreach Q, $(QUEST), data/output-$Q.txt)

# replace with appropriate python executable, or see the `setup` directive below
PYTHON = src/.venv/bin/python
N = 10000

# compile the rapport, including code output
all: math/rapport.tex $(OUT)
	pdflatex -output-directory math $<

# directives for specific questions
data/output-1c.txt: %: data/game-1e.yaml
	$(PYTHON) -m src -g $< -o $@ -sn $N passive basic

data/output-2d1.txt: %: data/game-2a.yaml
	$(PYTHON) -m src -g $< -o $@ -kd

# run script with specific game file for each question
data/output-%.txt: data/game-%.yaml
	$(PYTHON) -m src -g $< -o $@ -dsn $N passive basic optimal_$* dynamic

# setup the python environment (assuming python >= 3.7)
setup:
	[ -d src/.venv ] || python -m venv src/.venv
	. src/.venv/bin/activate
	pip install -r src/requirements.txt

# remove output files (e.g. to force code execution directives)
clean:
	rm data/output* || true
