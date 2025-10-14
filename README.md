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

## Usage

A single `json` representation of a song from HookTheory can be processed using `src.converter.convert`.

It is also possible to run the main script with the command below, from the root of the project.

```
python -m src.main
```

:warning: This script expects [this file](https://github.com/chrisdonahue/sheetsage-data/blob/main/hooktheory/Hooktheory.json.gz) to be unzipped in the `data` folder and simply called `Hooktheory.json`. 
You can tweak the `src/main.py` file if you want a different behaviour.

The resulting `.krn` files will be written in `data/kern` until an error is thrown.

### Testing

Unit tests were written using `pytest` to ensure that core functions are working properly.

To run the tests, use: 

```
PYTHONPATH=. pytest -v
```

All tests should pass!

## Limitations

Currently there are still a few issues with the code in this repo:

- Support for more chords need to be added manually in `src/chords.py`.
- Enharmonic note names are not always chosen correctly, the current heuristic is to favour sharps or flats if it reduces the global number of accidentals.
- There are still a few issues with tied notes in specific situations and the interaction with chords, some files cannot be processed because of that.
- The resulting scores can be ugly because the beams need to be specified manually in humdrum, and proper beaming require to look at the current meter and is currently out-of-scope.
- Some scores might look like they are missing chords in the graphical rendering, usually it's due to the fact that the `**text` representation used to write the chords in humdrum hides the text on rest notes. If you check the `krn` files, all chords are written properly.
