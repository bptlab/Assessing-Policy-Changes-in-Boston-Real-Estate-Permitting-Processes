# Assessing Policy Changes in Boston Real Estate Permitting

Event log, MP-Declare formalizations, and analysis code for the paper *Assessing Policy Changes in Boston Real Estate Permitting Processes*.

## Contents

- `boston_permitting.xes`: event log of 942 development projects from the public project pages of the Boston Planning Department.
- `mp-declare-models/`: Articles 80 and 81 of the Boston Zoning Code in three versions, formalized as MP-Declare constraints.
- `amendments/`: text amendments 446, 483, and 484 that separate the versions.
- `1_infer_project_type.py`, `2_clean_event_log.py`: prepare the log for the analysis.
- `compliance_checking.ipynb`: checks the constraints of each version against the projects it governs and reports compliance rates overall and per version.
- `policy_change_assessment.ipynb`: checks the projects governed by the old version against both the old and the new constraint of three policy changes.

## Usage

Requires `pm4py`, `declare4py`, and `pandas`.

```
python 1_infer_project_type.py
python 2_clean_event_log.py
```

This produces `boston_permitting_clean.xes`, which both notebooks read.

## License

MIT, see `LICENSE`.
