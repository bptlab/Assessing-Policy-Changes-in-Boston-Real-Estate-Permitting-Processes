"""Step 2: merge label variants, remove labels outside Article 80 review, and order "Period Open" events last within a day."""

from collections import defaultdict

from pm4py.objects.log.exporter.xes import exporter
from pm4py.objects.log.importer.xes import importer
from pm4py.objects.log.obj import EventLog, Trace

MERGE = {
    "Project Notification Form (PNF)": ["Project Notification Form"],
    "Draft Project Impact Report (DPIR)": ["Draft Project Impact Report"],
    "Final Project Impact Report (FPIR)": ["Final Project Impact Report"],
    "Preliminary Adequacy Determination (PAD)": ["Preliminary Adequacy Determination"],
    "Institutional Master Plan Notification Form (IMPNF)": ["IMPNF"],
    "Institutional Master Plan Amendment": ["Institutional Master Plan Amendment (IMP Amendment)", "IMP Amendment"],
    "Impact Advisory Group (IAG)": ["Impact Advisory Group"],
    "DPIR Comment Period End": ["DPIR Comment End"],
    "FPIR Comment Period End": ["FPIR Comment End"],
    "BPDA Board Approval": ["BPDA Board Approved", "Board Approved", "BPDA Board New Project Approved"],
    "Letter of Intent (LOI)": ["LOI Submitted"],
    "Notice of Public Hearing": ["Notice of Public Hearing (Translations)"],
    "Community Advisory Committee (CAC)": ["Citizens Advisory Committee (CAC)"],
    "Supplemental Filing": ["Additional Information"],
    "Contract Document Approval": ["Contract Document Approval Approved"],
    "Comment Period End": ["Comment Period Conclusion"],
    "Supplemental Filing Comment Period Open": ["Additional Information Comment Period Open"],
    "Supplemental Filing Comment Period End": ["Additional Information Comment Period End"],
    "Boston Civic Design Commission": [
        "Boston Civic Design Commission (BCDC) Design Committee Presentation",
        "Boston Civic Design Commission (BCDC) Monthly Meeting Presentation",
        "Boston Civic Design Commission (BCDC)",
        "Boston Civic Design Commission (BCDC) Approved",
        "Boston Civic Design Commission (BCDC) Other Approved",
    ],
    "Notice of Project Change (NPC)": ["Notice of Project Alteration"],
    "BPDA Board Notice of Project Change Approved": ["BPDA Board Notice of Project Alteration Approved"],
    "Project Fact Sheet": ["Planned Development Area (PDA) Development Plan Fact Sheet"],
    "Community Benefits Agreement": ["Public Benefit Contribution Agreement", "Community Contribution Agreement"],
}

EXCLUDE = {
    "Chapter 121A Application",
    "Chapter 121A Application Comment Period Open",
    "Chapter 121A Application Comment Period End",
    "Chapter 121A Regulatory Agreement",
    "Chapter 121A Regulatory Agreement - Report and Decision",
    "Article 85 Application",
    "Conservation Commission Hearing",
    "Zoning Board of Appeal (ZBA)",
    "Zoning Board of Appeal (ZBA) Approved",
    "Deed",
    "Order of Taking",
    "Land Disposition Agreement",
    "Sale and Construction Agreement",
    "Discharge of Mortgage and Security Agreement and Release of Assignment of Leases and Rents",
    "Presentation",
    "Video",
    "Boston Civic Design Commission (BCDC) Recording",
    "Meeting Agenda",
    "Meeting Notes",
    "Guidance for Permitting Off-campus Spaces for Temporary Institutional Uses",
}


def plain(label):
    return " ".join(label.replace("(", "").replace(")", "").replace(" - ", " ").split())


def period_open_last(events):
    days = defaultdict(list)
    for i, e in enumerate(events):
        days[e["time:timestamp"].date()].append(i)
    for slots in days.values():
        ordered = sorted((events[i] for i in slots), key=lambda e: "Period Open" in e["concept:name"])
        for i, e in zip(slots, ordered):
            events[i] = e


merges = {plain(v): plain(c) for c, variants in MERGE.items() for v in [c, *variants]}
exclude = {plain(label) for label in EXCLUDE}

log = importer.apply("boston_permitting_typed.xes", variant=importer.Variants.ITERPARSE,
                     parameters={"show_progress_bar": False, "timestamp_sort": False})

traces, before, removed = [], 0, 0
for trace in log:
    events = []
    for e in trace:
        before += 1
        label = plain(e["concept:name"])
        if label in exclude:
            removed += 1
            continue
        e["concept:name"] = merges.get(label, label)
        events.append(e)
    period_open_last(events)
    traces.append(Trace(events, attributes=trace.attributes))

exporter.apply(EventLog(traces, attributes=log.attributes, extensions=log.extensions), "boston_permitting_clean.xes",
               parameters={"show_progress_bar": False})
print(f"{before} events, {removed} removed, {before - removed} left")
