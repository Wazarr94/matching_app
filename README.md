# Matching App

## Dependencies

To run this, you need Python 3.10.

## Installation

Clone the repository and open the repository on your terminal or IDE.

### Install with poetry

```bash
poetry install
```

### Install with pip

Use a virtual environment and install the dependencies with pip.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the dashboard

### Running with poetry

```bash
poetry shell
streamlit run src/page_streamlit.py
```

### Running with pip

```bash
python -m streamlit run src/page_streamlit.py
```

## TODO

- [x] Support other file formats (xlsx and parquet)
- [x] Add encoding option for csv
- [x] Indicate more clearly the ongoing process (especially for string cleaning)
- [x] Add new distances (with their options)
  - [x] Add all distances available in rapidfuzz
  - [x] Add the different functions from these distances
  - [x] ~~Show options for JaroWinkler (prefix weight) and Levenshtein (weights)~~
- [x] ~~Add JaccardModified distance~~
- [x] Add option to add a column id in addition to the column name
- [ ] Add possibility to remove company suffixes
- [ ] Add mapping functionality
- [ ] Interface to select the correct match directly on the dashboard
  - [ ] Add comments column to provide info on the matching for audit trail
- [ ] Create another sheet for metadata
- [ ] Be able to change the output filename
- [ ] Try to use polars str function for better performance when cleaning
- [ ] Figure out a process when we already have a mapping file
