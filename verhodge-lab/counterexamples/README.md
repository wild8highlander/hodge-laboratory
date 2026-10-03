# The near-miss corpus

Every file is a COMPUTED counterexample to a tempting but false
shortcut of the implementation.  The corpus is the falsification
layer of the program (the chess-dynamics-lab honesty ladder,
transplanted): each entry records the claim falsified, the exact
computed data, and the lesson absorbed into the code.

| id | wave | shortcut falsified |
|----|------|--------------------|
| NE01 | v1.5 | float precision can replace the exact cyclotomic layer |
| NE02 | v1.6 | diagonalization alone computes the Smith normal form |
| NE03 | v1.5-pre | the two census schemes agree without edge cases |
| NE04 | v1.8 | any rational psi gives a smooth Dwork pencil |
| NE05 | v1.9 | a Laurent psi-target without the singular poles is the PF operator |

Re-run the corpus: `python -m pytest tests/test_verhodge.py -k near_miss`
