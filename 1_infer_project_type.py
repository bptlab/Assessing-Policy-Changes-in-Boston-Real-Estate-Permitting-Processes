"""Step 1: infer missing project types and gross floor areas; remove projects where neither can be inferred."""

import re

from pm4py.objects.log.exporter.xes import exporter
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.log.obj import EventLog

LARGE = {"Project Notification Form (PNF)", "Project Notification Form", "Letter of Intent (LOI)", "LOI Submitted"}
SMALL = {"Small Project Review Application (SPRA)"}
GFA_BY_HAND = {
    5047: 196_000 + 129_000,  # 1725 Hyde Park Avenue, both phases
    1856: 31_361,  # 111 Terrace Street
}
SQFT = re.compile(r"(\d[\d,]*)\s*(?:gross\s+)?(?:square[- ]f(?:oo|ee)t|sq\.?\s?ft|g?sf)\b(.{0,60})", re.I)


def gfa_from(description):
    figures = [int(n.replace(",", "")) for n, after in SQFT.findall(description or "")
               if not re.search(r"\b(site|land)\b", after, re.I)]
    return max(figures, default=None)

log = importer.apply("boston_permitting.xes", variant=importer.Variants.ITERPARSE,
                     parameters={"show_progress_bar": False, "timestamp_sort": False})

kept, inferred, removed = [], 0, []
for trace in log:
    if trace.attributes.get("project_type") not in ("Large Project", "Small Project"):
        labels = {e["concept:name"] for e in trace}
        large, small = bool(labels & LARGE), bool(labels & SMALL)
        if large == small:
            removed.append(trace.attributes.get("name"))
            continue
        trace.attributes["project_type"] = "Large Project" if large else "Small Project"
        inferred += 1
    kept.append(trace)

print(f"{inferred} project types inferred, {len(removed)} projects removed: {removed}, {len(kept)} left")

with_gfa, gfa_inferred, gfa_missing = [], [], []
for trace in kept:
    a = trace.attributes
    if a["project_id"] in GFA_BY_HAND:
        a["gross_floor_area_sqft"] = GFA_BY_HAND[a["project_id"]]
    elif not a.get("gross_floor_area_sqft"):
        gfa = gfa_from(a.get("description"))
        if gfa is None:
            gfa_missing.append(a.get("name"))
            continue
        a["gross_floor_area_sqft"] = gfa
        gfa_inferred.append((a.get("name"), gfa))
    with_gfa.append(trace)

exporter.apply(EventLog(with_gfa, attributes=log.attributes, extensions=log.extensions), "boston_permitting_typed.xes",
               parameters={"show_progress_bar": False})
print(f"{len(GFA_BY_HAND)} gross floor areas set by hand, {len(gfa_inferred)} inferred: {gfa_inferred}")
print(f"{len(gfa_missing)} projects without a gross floor area removed: {gfa_missing}, {len(with_gfa)} left")
