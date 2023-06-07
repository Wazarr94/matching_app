# Matching App

## Dependencies

To run this, you need Python 3.10.

## Installation

Clone the repository:

```bash
git clone https://gitlab-dogen.group.echonet/gf/csr/methodology_data/c2a/matching_app
```

Then, open the repository on your terminal or IDE.

### Install with pdm

I recommend using pdm for all python projects. This is very useful in order to share a project and make sure we have the correct dependencies.

You will find instructions in the [README_PDM.md file](README_PDM.md) in order to install this tool.

```bash
pdm install
```

### Install with pip

```bash
pip install -r requirements.txt
```

## Running the dashboard

### Running with pdm

```bash
pdm run dashboard
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
