# Assessing Policy Changes in Boston Real Estate Permitting

Event log, MP-Declare formalizations, and analysis code for the paper *Assessing Policy Changes in Boston Real Estate Permitting Processes*.

## Contents

- `boston_permitting.xes`: event log of 942 development projects from the public project pages of the Boston Planning Department.
- `mp-declare-models/`: Articles 80 and 81 of the Boston Zoning Code in three versions, formalized as MP-Declare constraints.
- `amendments/`: text amendments 446, 483, and 484 that separate the versions.
- `1_infer_project_type.py`, `2_clean_event_log.py`: prepare the log for the analysis.
- `compliance_checking.ipynb`: checks the constraints of each version against the projects it governs and reports compliance rates overall and per version.
- `policy_change_assessment.ipynb`: checks the projects governed by the old version against both the old and the new constraint of three policy changes.

## Sources

- Article 80 and all other articles of the Boston Zoning Code: [Municode, Boston Zoning Code](https://library.municode.com/ma/boston/codes/redevelopment_authority/376755?nodeId=ART80DEREAP).
- Text amendments not included in `amendments/`: [Municode, Boston Zoning Code ordinances](https://library.municode.com/ma/boston/ordinances/redevelopment_authority).

## Event log

`boston_permitting.xes` contains 942 projects (traces) and 15,067 events from 1988 to 2026, with one trace per project and one event per entry in the project's review timeline, such as a filing, a comment period, a public meeting, or a Board decision.

- Project attributes: `project_id`, `name`, `address`, `neighborhood`, `project_type` (Large or Small Project), `gross_floor_area_sqft`, `land_sqft`, `phase`, `in_article_80`, `description`, and `url` of the project page.
- Event attributes: `concept:name` (the label as published), `time:timestamp`, `text`, and `url` of the linked document.

Some projects lack a project type or a gross floor area; `1_infer_project_type.py` infers them where possible, and `2_clean_event_log.py` merges label variants into the event types used in the MP-Declare models.

## Usage

Requires `pm4py`, `declare4py`, and `pandas`.

```
python 1_infer_project_type.py
python 2_clean_event_log.py
```

This produces `boston_permitting_clean.xes`, which both notebooks read.

## License

MIT, see `LICENSE`.
