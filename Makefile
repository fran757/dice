QUEST = 1c 1e 1h 2a 2b 2c 2d1 2d2 2e
OUT = $(foreach Q, $(QUEST), data/output-$Q.txt)

# replace with appropriate python executable, or see the `setup` directive below
PYTHON = src/.venv/bin/python
RUN = $(PYTHON) -m src -g $< -o $@
N = 100000

# compile the rapport, including code output
all: math/rapport.tex $(OUT)
	pdflatex -output-directory math $<

# directives for specific questions

data/output-1c.txt: %: data/game-1e.yaml
	$(RUN) --simulate -n $N passive basic

data/output-2d1.txt: %: data/game-2a.yaml
	$(RUN) --liquidate --dynamic --clock

data/output-2d2.txt: %: data/game-2d.yaml
	$(RUN) --dynamic --clock

data/output-2e.txt: %: data/game-2d.yaml
	$(RUN) --liquidate

# run script with specific game file for each question
data/output-%.txt: data/game-%.yaml
	$(RUN) -dsn $N passive basic optimal_$* dynamic

# setup the python environment (assuming python >= 3.7)
setup:
	[ -d src/.venv ] || python -m venv src/.venv
	. src/.venv/bin/activate
	pip install -r src/requirements.txt

# remove output files (e.g. to force code execution directives)
clean:
	rm data/output* || true
