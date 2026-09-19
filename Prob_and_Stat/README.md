# Choosing and Running a Test

Companion code for Section 5 of *Probability and Statistics: A Concise Guide* by Stephen Fratini.

This directory contains a Jupyter notebook that helps a reader choose a hypothesis test and then run it. The notebook asks how the data were collected, names the test those answers commit the reader to, states the assumptions, and carries out the analysis. The tests themselves are computed by SciPy and statsmodels. The reader does not write any statistical code.

Stable location:

<https://github.com/sfratini33/art-of-managing-things-external/tree/master/Prob_and_Stat>

## What is here

- `choose_and_run_test.ipynb` — the program the reader runs
- `test_chooser/` — questionnaire, tests, and book-style reports
- `examples/batteries.csv` and `examples/ping_pong.csv` — the Section 4.6 examples
- `requirements.txt` — Python packages, already present in a typical Anaconda install

## How to run

1. Install [Anaconda](https://www.anaconda.com/) if it is not already installed.
2. Download or clone this folder.
3. Open **Anaconda Prompt**, start Jupyter,

   ```text
   jupyter notebook
   ```

   or `jupyter lab`, and open `choose_and_run_test.ipynb`.
4. Run the cells in order. The questionnaire cell displays dropdowns. Later cells replay the battery, ping-pong, material-strength, and proportion examples from Section 4.

If a package is missing:

```text
conda install scipy statsmodels pandas openpyxl ipywidgets
```

Use the Anaconda kernel, not a generic `python` command from the Windows Store.
