# Convert HookTheory json files to **kern leadsheets

This project uses **Python 3.10**.

To setup a virtual environment, you can for instance do:
```
python -m venv env 
pip install -r requirements.txt
source env/bin/activate
```

## File Organisation

This repository is organised as follows:

```
├── data
│   ├── fileExample.json
│   ├── img/                             % Some generated .png files
│   └── kern/                            % Some generated .krn files
├── src
│   ├── __init__.py
│   ├── chords.py                        % Processing related to chords and harmonic information
│   ├── converter.py                     % Main function to convert a json entry
│   ├── kernfilebuilder.py               % Core humdrum processing to generate the kern melody
│   ├── main.py                          % Script to process the dataset
│   ├── mode_formulas.py                 % Functions related to key signatures identification
│   └── util.py                          % General utility functions and constants
├── test                                 % Unit test files
│   ├── test_kernfilebuilder.py
│   ├── test_mode_formulas.py
│   └── test_util.py
├── verovio_script.sh
├── LICENSE
├── README.md
└── requirements.txt
```

## Testing

Unit tests were written using `pytest` to ensure that core functions are working properly.

To run the tests, use: 

```
PYTHONPATH=. pytest -v
```

All tests should pass!
