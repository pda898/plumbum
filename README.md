# Plumbum

Functional DSL over TeX (over formula description part of it) which allows to translate those formulas directly into code snippets.

Currently supported target languages:

* Javascript
* Python 3

More detailed description is avaiable in file [description.pdf](/description.pdf) (only in Russian currently)

## Requirements

*Python 3* is required to use that app. Additional requirements are listed in [requirements.txt](/requirements.txt) and could be installed through pip automatically. Usage of virtual environment is recommended in case of library version conflict.
```bash
python -m pip install -r requirements.txt
```

## Usage

```bash
python main.py <mode> [args...]
```

Currently there is one mode supported: filer. It will translate all files with .pb extension into files with files with code. Target language is automatically chosen based on file name.

* *example.js.pb* will produce Javascript code in *example.js* 
* *example.py.pb* will produce Python 3 code in *example.py*