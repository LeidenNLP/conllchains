# Extracting coreference chains from the CONLL dataset

The code in this repository serves as a starting point for students of the course Python for Linguists at Leiden University. The scripts download and unpack the corpus found at https://data.mendeley.com/datasets/zmycy7t9h9/2, and extract coreference chains. 

## How to use these tools

In PyCharm, you can create a new project from this git url directly. Any requirements should be automatically installed, or PyCharm should at least offer it.

Alternatively, manually clone (or download and unzip) this repository to a local directory, and then either open it in PyCharm, or manually [create a virtual environment based on requirements.txt](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-a-requirements-file).

Subsequently, on the command line (in PyCharm, or outside, but with the virtual environment activated), first do:

```
python download.py
```

And then do something like:

```
python extract_chains.py > coref_chains.jsonl
```

You can also specify which subset of the data to use (e.g., arabic); the help will tell you how:

```
python extract_chains.py --help
```
