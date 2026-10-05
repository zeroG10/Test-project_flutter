#!/usr/bin/env python3
"""The client's report: a test completion report (ISTQB / ISO/IEC/IEEE 29119-3 shape), one per slice — iOS,
Android, or both — from the same records as the internal reports.

What the client gets (owner, 2026-10-05, after the web project's 2026-09-28 ruling): the end and the results of
testing in plain terms — scope, environment, numbers, what could not run and why, what is not automated (groups
with counts), open defects by title, module and severity, the exit criteria, residual risks and recommendations,
sign-off. None of the kitchen: no ids, no repository paths or links, no test accounts, no run history or triage.
Nothing material is left out: an open defect, a behaviour the owner accepted, an untested area and a residual risk
are all here — the client decides on facts, not on what reads well. The owner approves it before it is sent.

Output: `automation/mobile/reports/<slice>/client/test-completion-report.html`.
"""

from __future__ import annotations

import argparse
import html
from datetime import UTC, datetime
from pathlib import Path

import mobile_brand as brand
import mobile_summary as bs
import mobile_report_data as rd

CSS = (
    brand.TOKENS_CSS
    + """
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.6 var(--body);-webkit-font-smoothing:antialiased}
.wrap{max-width:900px;margin:0 auto;padding-inline:20px;padding-block:26px 64px}
a{color:var(--accent)} a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
h1,h2,h3{font-family:var(--display);font-weight:700;line-height:1.2;text-wrap:balance;margin:0}
h1{font-size:30px;letter-spacing:-.01em}
h2{font-size:20px;margin:36px 0 12px;padding-top:16px;border-top:1px solid var(--line)}
h3{font-size:15px;margin:16px 0 6px}
p{margin:0 0 10px;max-width:72ch}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:22px 0 8px}
.pill{display:inline-flex;align-items:center;gap:6px;font:700 12px/1 var(--mono);letter-spacing:.05em;
  text-transform:uppercase;padding:6px 10px;border-radius:999px;vertical-align:middle}
.pill.pass{background:var(--pass-soft);color:var(--pass)} .pill.fail{background:var(--fail-soft);color:var(--fail)}
.pill.known{background:var(--known-soft);color:var(--known)} .pill.block{background:var(--block-soft);color:var(--block)}
.pill::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px 22px;margin:16px 0 0;padding:0}
.facts div{display:grid;gap:2px}
.facts dt{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.facts dd{margin:0;font:500 14px/1.4 var(--body);overflow-wrap:anywhere}
.lead{font-size:17px;line-height:1.6;max-width:72ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:16px 0 14px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:4px}
.kpi b{font:700 30px/1 var(--display);font-variant-numeric:tabular-nums;color:var(--figure)}
.kpi span{color:var(--muted);font-size:13px}
.kpi.pass b{color:var(--pass)} .kpi.known b{color:var(--known)} .kpi.block b{color:var(--block)}
.bar{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--idle);margin-top:4px}
.bar i{display:block;height:100%} .bar .p{background:var(--pass)} .bar .k{background:var(--known)} .bar .b{background:var(--block)}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:8px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px} .legend i{width:10px;height:10px;border-radius:2px;display:inline-block}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
th{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}
td.num,th.num{text-align:right} tr.total td{font-weight:700}
.sev{font:700 12px/1 var(--mono);padding:4px 7px;border-radius:5px;white-space:nowrap}
.sev.S1,.sev.S2{background:var(--fail-soft);color:var(--fail)} .sev.S3{background:var(--known-soft);color:var(--known)}
.sev.S4{background:var(--accent-soft);color:var(--accent)}
.os{font:600 12px/1 var(--mono);padding:4px 7px;border-radius:5px;background:var(--accent-soft);color:var(--accent);white-space:nowrap}
.ok{color:var(--pass);font-weight:700} .warn{color:var(--known);font-weight:700}
.draft{margin:0 0 14px;padding:10px 14px;border-radius:8px;background:var(--fail-soft);color:var(--fail)}
.note{font-size:13px;color:var(--muted)}
ul{margin:6px 0 10px;padding-left:20px} li{margin:4px 0;max-width:72ch}
.signoff{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px 22px;margin-top:8px}
.signoff dt{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)} .signoff dd{margin:0}
footer{margin-top:40px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--muted);
  display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media (max-width:560px){h1{font-size:24px}.kpi b{font-size:24px}.wrap{padding-inline:16px}.facts{grid-template-columns:1fr 1fr}}
@media print{
  body{background:#fff;color:#122E52;font-size:12px} .wrap{max-width:none;padding:0}
  h2{break-after:avoid;margin-top:22px} h3{break-after:avoid}
  tr,.kpis,.kpi,.facts,.docinfo{break-inside:avoid} a{color:#122E52;text-decoration:none}
}
"""
)


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


def table(head: list[str], rows: list[list[object]], nums: tuple[int, ...] = (), total: bool = False) -> str:
    th = "".join(f"<th{' class=num' if i in nums else ''}>{h}</th>" for i, h in enumerate(head))
    body = []
    for n, r in enumerate(rows):
        cls = " class=total" if total and n == len(rows) - 1 else ""
        body.append(f"<tr{cls}>" + "".join(f"<td{' class=num' if i in nums else ''}>{v}</td>" for i, v in enumerate(r)) + "</tr>")
    return f"<div class='scroll'><table><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"


def yes(met: bool) -> str:
    return "<span class='ok'>Yes</span>" if met else "<span class='warn'>No</span>"


def os_tag(name: str) -> str:
    return f"<span class='os'>{esc(name)}</span>"


def sev(code: str) -> str:
    return f"<span class='sev {esc(code)}'>{esc(rd.SEVERITY_WORD.get(code, code))}</span>"


def exit_criteria(p: rd.Platform) -> list[tuple[str, bool, str]]:
    critical = [b for b in p.bugs if b.severity == "S1"]
    major = [b for b in p.bugs if b.severity == "S2"]
    accepted_major = [b for b in p.accepted if b.severity == "S2"]
    p0 = p.p0()
    missing = [f"{d} ({o})" for d, o, covered in p0 if not covered]
    rows = [
        ("Every planned test executed", p.tc["Blocked"] == 0,
         f"{sum(p.tc.values())} tests, {p.tc['Blocked']} could not run (section 4)"),
        ("No unexpected test failure", p.unexpected == 0, f"{p.unexpected} unexpected"),
        ("Every red check has a known cause", p.c["Failed"] == 0, f"{p.c['Failed']} unexplained"),
        ("No open critical defect", not critical, f"{len(critical)} open"),
        ("No open major defect", not major, f"{len(major)} open" + (
            f"; {len(accepted_major)} major-severity behaviours accepted by the product owner (section 6)"
            if accepted_major else "")),
    ]
    if p0:
        rows.append(("P0 devices of the device matrix covered", not missing,
                     "all covered" if not missing else "not tested: " + ", ".join(missing)))
    return rows


def render(key: str, platforms: list[rd.Platform]) -> str:
    slc = brand.slice_(key)
    combined = len(platforms) > 1
    now = datetime.now(UTC)
    end = max(p.end for p in platforms)
    start = min(p.start for p in platforms)
    run_date = end.strftime("%Y-%m-%d")
    label, cls = rd.worst(platforms)
    o: list[str] = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'>",
        f"<title>{esc(slc.product_short)} Test Completion</title>", brand.FONTS_LINK, f"<style>{CSS}</style></head><body>",
        "<div class='wrap'>",
    ]
    w = o.append
    missing = brand.unset(slc)
    if missing:
        w("<p class='draft'><b>Draft — not for sending.</b> Not set in <code>setup/project.yaml → report</code>: "
          + ", ".join(f"<code>{esc(k)}</code>" for k in missing) + ".</p>")

    # ---- header ----
    w("<header>" + brand.brandbar("client"))
    w(f"<div class='eyebrow'>Test completion report · Mobile regression · {' & '.join(p.name for p in platforms)}</div>")
    w(f"<h1>{esc(slc.product)} — Test Completion Report <span class='pill {cls}'>{esc(label)}</span></h1>")
    facts = [
        ("Test cycle", rd.cycle(start, end)),
        ("Environment", brand.ENVIRONMENT),
        ("Device" + ("s" if combined else ""), " · ".join(
            f"{p.facts['device'].replace(' — ', ' ')} ({p.facts['os']})" for p in platforms)),
        ("App build", platforms[0].facts["build"]),
        ("Report date", rd.day(now)),
        ("Prepared by", brand.PREPARED_BY),
        ("Client", brand.CLIENT),
    ]
    w("<dl class='facts'>" + "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in facts) + "</dl>")
    runs = " and ".join(f"{p.name} run of {p.run_date}" for p in platforms)
    online = f"<a href='{esc(slc.client_url)}'>{esc(slc.client_url)}</a>" if slc.client_url else "—"
    w(f"<div class='docinfo'><b>Document.</b> Version of {run_date} ({runs}) · Online version: {online} · "
      f"PDF: <code>{esc(slc.pdf_name('TestCompletionReport', run_date))}</code> · {esc(brand.CONFIDENTIALITY)}.</div>")
    w("</header>")

    # ---- 1. summary ----
    w("<h2>1. Summary</h2>")
    if not combined:
        p = platforms[0]
        c, s = p.c, p.s
        held = f"<b>{c['Held red']}</b> are red because of {len(p.held_by_bugs)} known, reported defects" + (
            f" and {len(p.accepted)} behaviours accepted by the product owner" if p.accepted else "")
        majors = [b for b in p.bugs if b.severity in ("S1", "S2")]
        outcome = "with <b>no unexpected failures</b>" if not p.unexpected else f"with <b>{p.unexpected} unexpected failures</b>, under analysis"
        w(f"<p class='lead'>Regression testing of the {esc(slc.product)} finished on {rd.day(p.end)} {outcome}. "
          f"Of the <b>{s.total}</b> checks in the QA checklist, <b>{s.automated}</b> ({rd.pct(s.automated, s.total)}) are "
          f"automated: <b>{c['Passed']}</b> passed, {held}, and <b>{c['Blocked']}</b> could not run on the test "
          f"environment for agreed reasons. <b>{len(p.bugs)}</b> defects are open, "
          + ("none of them critical or major." if not majors else f"{len(majors)} of them critical or major — see section 8.")
          + f" The other <b>{c['Not automated']}</b> checks are not automated, each for a written reason (section 5).</p>")
    else:
        a, b = platforms
        both = rd.passed_on_both(a, b)
        union = {x.bug_id for p in platforms for x in p.bugs}
        majors = {x.bug_id for p in platforms for x in p.bugs if x.severity in ("S1", "S2")}
        outcome = ("<b>no unexpected failures on either platform</b>" if label != "Failed"
                   else "<b>unexpected failures</b>, under analysis")
        w(f"<p class='lead'>Regression testing of the {esc(slc.product)} finished with {outcome}. Both platforms run "
          f"the same QA checklist of <b>{a.s.total}</b> checks against the same app build ({esc(a.r.env.get('Build', ''))}). "
          + " ".join(f"<b>{p.name}</b>: {p.c['Passed']} of {p.s.automated} automated checks passed (run of {rd.day(p.end)})." for p in platforms)
          + f" <b>{both}</b> checks passed on both platforms. <b>{len(union)}</b> defects are open across the two "
          "platforms, " + ("none of them critical or major." if not majors else f"{len(majors)} of them critical or major.") + "</p>")

    # ---- 2. scope ----
    w("<h2>2. Scope</h2>")
    w(f"<p>Automated functional regression of the field technicians' mobile app ({' and '.join(p.name for p in platforms)}) "
      f"through its user interface, on the test environment ({esc(brand.ENVIRONMENT)}). The checklist covers "
      f"{len(platforms[0].r.modules)} modules:</p><ul>" + "".join(f"<li>{esc(m.name)}</li>" for m in platforms[0].r.modules)
      + "</ul>")
    if brand.OUT_OF_SCOPE:
        w("<h3>Out of scope</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in brand.OUT_OF_SCOPE) + "</ul>")

    # ---- 3. environment ----
    w("<h2>3. Test environment</h2>")
    w(table(["", *(p.name for p in platforms)], [
        ["Operating system", *(esc(p.facts["os"]) for p in platforms)],
        ["Device", *(esc(p.facts["device"]) for p in platforms)],
        ["App build", *(esc(p.facts["build"]) for p in platforms)],
        ["App type", *(esc(p.facts["app_type"]) for p in platforms)],
        ["Backend", *(esc(brand.ENVIRONMENT) for _ in platforms)],
        ["Test automation", *("Appium + pytest, through the app's interface" for _ in platforms)],
        ["Run finished", *(f"{p.end:%-d %B %Y, %H:%M} UTC" for p in platforms)],
    ]))

    # ---- 4. results ----
    w("<h2>4. Results</h2>")
    if not combined:
        p = platforms[0]
        c, s = p.c, p.s
        w("<div class='kpis'>"
          f"<div class='kpi'><b>{s.total}</b><span>checks in the QA checklist</span></div>"
          f"<div class='kpi'><b>{s.automated}</b><span>automated · {rd.pct(s.automated, s.total)}</span></div>"
          f"<div class='kpi pass'><b>{c['Passed']}</b><span>passed</span></div>"
          f"<div class='kpi known'><b>{c['Held red']}</b><span>red — known cause</span></div>"
          f"<div class='kpi block'><b>{c['Blocked']}</b><span>could not run</span></div></div>")
        width = lambda n: f"{100 * n / s.total:.2f}%" if s.total else "0"  # noqa: E731
        w(f"<div class='bar' role='img' aria-label='{c['Passed']} passed, {c['Held red']} red with a known cause, "
          f"{c['Blocked']} could not run, {c['Not automated']} not automated, of {s.total}'>"
          f"<i class='p' style='width:{width(c['Passed'])}'></i><i class='k' style='width:{width(c['Held red'])}'></i>"
          f"<i class='b' style='width:{width(c['Blocked'])}'></i></div>"
          "<div class='legend'><span><i style='background:var(--pass)'></i>passed</span>"
          "<span><i style='background:var(--known)'></i>red — known cause</span>"
          "<span><i style='background:var(--block)'></i>could not run</span>"
          "<span><i style='background:var(--idle)'></i>not automated (section 5)</span></div>")
        rows = []
        for m in p.r.modules:
            mc = p.r.counts(m.rows)
            rows.append([esc(m.name), len(m.rows), len(m.rows) - mc["Not automated"], mc["Passed"], mc["Held red"],
                         mc["Blocked"], mc["Not automated"]])
        rows.append(["Total", s.total, s.automated, c["Passed"], c["Held red"], c["Blocked"], c["Not automated"]])
        w("<h3>By module</h3>" + table(["Module", "Checks", "Automated", "Passed", "Red (known)", "Could not run",
                                        "Not automated"], rows, nums=(1, 2, 3, 4, 5, 6), total=True))
    else:
        a, b = platforms
        both = rd.passed_on_both(a, b)
        w("<div class='kpis'>"
          f"<div class='kpi'><b>{a.s.total}</b><span>checks in the QA checklist</span></div>"
          + "".join(f"<div class='kpi pass'><b>{p.c['Passed']}</b><span>passed on {p.name} · of {p.s.automated} automated</span></div>"
                    for p in platforms)
          + f"<div class='kpi pass'><b>{both}</b><span>passed on both platforms</span></div></div>")
        rows = [[os_tag(p.name), p.s.total, p.s.automated, p.c["Passed"], p.c["Held red"], p.c["Blocked"],
                 p.c["Not automated"], f"<span class='pill {p.verdict[1]}'>{esc(p.verdict[0])}</span>"] for p in platforms]
        rows.append(["Total", *(sum(p.s.total for p in platforms), sum(p.s.automated for p in platforms),
                                sum(p.c["Passed"] for p in platforms), sum(p.c["Held red"] for p in platforms),
                                sum(p.c["Blocked"] for p in platforms), sum(p.c["Not automated"] for p in platforms)),
                     f"<span class='pill {cls}'>{esc(label)}</span>"])
        w("<h3>By platform</h3>" + table(["Platform", "Checks", "Automated", "Passed", "Red (known)", "Could not run",
                                          "Not automated", "Verdict"], rows, nums=(1, 2, 3, 4, 5, 6), total=True))
        w(f"<p class='note'>The total counts each check once per platform ({a.s.total} × 2). A check passes for the "
          f"app only when it passed on both platforms: {both} of {a.s.total}.</p>")
        rows = []
        for ma, mb in zip(a.r.modules, b.r.modules, strict=True):
            ca, cb = a.r.counts(ma.rows), b.r.counts(mb.rows)
            ids = [row.item.chk_id for row in ma.rows]
            rows.append([esc(ma.name), len(ma.rows), f"{ca['Passed']} / {len(ma.rows) - ca['Not automated']}",
                         f"{cb['Passed']} / {len(mb.rows) - cb['Not automated']}", rd.passed_on_both(a, b, ids)])
        rows.append(["Total", a.s.total, f"{a.c['Passed']} / {a.s.automated}", f"{b.c['Passed']} / {b.s.automated}", both])
        w("<h3>By module</h3>" + table(["Module", "Checks", f"{a.name} passed / automated",
                                        f"{b.name} passed / automated", "Passed on both"], rows, nums=(1, 2, 3, 4), total=True))
    blocked = [(p.name, x) for p in platforms for x in p.blocked]
    if blocked:
        w(f"<h3>Could not run · {len(blocked)} {'test' if len(blocked) == 1 else 'tests'}</h3>")
        w(table((["Platform"] if combined else []) + ["Test", "Why"],
                [([os_tag(n)] if combined else []) + [esc(rd.without_tc(x.title)),
                 esc(brand.CLIENT_BLOCKED.get(x.tc, "The test environment could not provide what the test needs."))]
                 for n, x in blocked]))

    # ---- 5. not automated ----
    na = " / ".join(f"{p.name} {p.c['Not automated']}" for p in platforms) if combined else str(platforms[0].c["Not automated"])
    w(f"<h2>5. Checks not automated · {na}</h2>")
    w("<p>Each of these has a written reason in the QA records. They are not failures: they are checks automation does "
      "not decide, grouped by why.</p>")
    groups = [p.client_groups() for p in platforms]
    names = sorted({g for gs in groups for g in gs}, key=lambda g: -sum(gs.get(g, 0) for gs in groups))
    w(table(["Reason", *((p.name for p in platforms) if combined else ["Checks"])],
            [[esc(g), *(gs.get(g, 0) or "—" for gs in groups)] for g in names], nums=tuple(range(1, len(platforms) + 1))))

    # ---- 6. defects ----
    modules = {m.key: m.name for m in platforms[0].r.modules}
    bugs: dict[str, tuple[bs.Bug, set[str]]] = {}
    for p in platforms:
        for x in p.bugs:
            bugs.setdefault(x.bug_id, (x, set()))[1].add(p.name)
    w(f"<h2>6. Open defects · {len(bugs)}</h2>")
    by_sev: dict[str, int] = {}
    for x, _ in bugs.values():
        by_sev[x.severity] = by_sev.get(x.severity, 0) + 1
    if bugs:
        w("<p>" + " · ".join(f"{sev(k)} {n}" for k, n in sorted(by_sev.items(), key=lambda kv: rd.SEVERITY_ORDER.get(kv[0], 9)))
          + ". Severity as assessed by QA; priority is decided by the product owner.</p>")
        rows = []
        for x, plats in sorted(bugs.values(), key=lambda t: (rd.SEVERITY_ORDER.get(t[0].severity, 9), t[0].title)):
            where = "Both" if len(plats) == len(platforms) and combined else " & ".join(sorted(plats))
            rows.append([esc(x.title), esc(modules.get(x.module_dir, x.module_dir)), *([os_tag(where)] if combined else []),
                         sev(x.severity), "Open"])
        w(table(["Defect", "Module", *(["Platform"] if combined else []), "Severity", "Status"], rows))
    else:
        w("<p>No defects are open.</p>")
    accepted: dict[str, tuple[bs.Bug, set[str]]] = {}
    for p in platforms:
        for x in p.accepted:
            accepted.setdefault(x.bug_id, (x, set()))[1].add(p.name)
    if accepted:
        w(f"<h3>Known behaviour accepted by the product owner · {len(accepted)}</h3>")
        w("<p>QA reported these against the requirements; the product owner reviewed them and decided not to raise them "
          "as defects. Their checks stay red and are counted above as “red — known cause”.</p>")
        w(table(["Behaviour", "Module", *(["Platform"] if combined else []), "QA severity", "Status"],
                [[esc(x.title), esc(modules.get(x.module_dir, x.module_dir)),
                  *([os_tag(" & ".join(sorted(pl)))] if combined else []), sev(x.severity), "Accepted"]
                 for x, pl in accepted.values()]))

    # ---- 7. exit criteria ----
    w("<h2>7. Exit criteria</h2>")
    if not combined:
        w(table(["Criterion", "Met", "Detail"], [[esc(n), yes(m), esc(d)] for n, m, d in exit_criteria(platforms[0])]))
    else:
        ea, eb = (exit_criteria(p) for p in platforms)
        w(table(["Criterion", *(p.name for p in platforms), "Detail"],
                [[esc(x[0]), yes(x[1]), yes(y[1]), esc(f"{platforms[0].name}: {x[2]} · {platforms[1].name}: {y[2]}")]
                 for x, y in zip(ea, eb, strict=False)]))

    # ---- 8. risks and recommendations ----
    w("<h2>8. Residual risks and recommendations</h2><ul>")
    majors_open = [x for x, _ in bugs.values() if x.severity in ("S1", "S2")]
    if majors_open:
        w(f"<li><b>Fix the {len(majors_open)} critical or major defects before release:</b> "
          + "; ".join(esc(x.title) for x in majors_open) + ".</li>")
    minors = [x for x, _ in bugs.values() if x.severity in ("S3", "S4")]
    if minors:
        w(f"<li>The {len(minors)} minor and cosmetic defects can follow in a later release.</li>")
    for x, _ in accepted.values():
        w(f"<li><b>Accepted behaviour ({esc(rd.SEVERITY_WORD.get(x.severity, x.severity))} by QA's assessment):</b> "
          f"{esc(x.title)}. The product owner decided not to raise it; we recommend confirming with the client that "
          "this is intended.</li>")
    manual = sum(p.kind_counts().get(k, 0) for p in platforms for k in ("person", "simulator"))
    if manual:
        w(f"<li>{manual} checks stay outside automation (visual judgement, real-device behaviour): a short manual pass "
          "over them on a real device is recommended before release.</li>")
    if blocked:
        w(f"<li>{len(blocked)} {'test' if len(blocked) == 1 else 'tests'} could not run on the test environment "
          "(section 4); re-run when the environment allows.</li>")
    covered = ", ".join(f"{p.facts['device'].replace(' — ', ' ')} ({p.facts['os']})" for p in platforms)
    w(f"<li>Only {esc(covered)} and the test environment were covered: behaviour on real devices, other OS versions "
      "and production is not asserted by this report.</li>")
    if combined:
        older = min(platforms, key=lambda p: p.end)
        newer = max(platforms, key=lambda p: p.end)
        if older.end.date() != newer.end.date():
            w(f"<li>The {older.name} results are from {rd.day(older.end)}, the {newer.name} results from "
              f"{rd.day(newer.end)}; the shared test code was extended after the {older.name} run. A fresh "
              f"{older.name} run is recommended before release.</li>")
    w("</ul>")

    # ---- 9. sign-off ----
    w("<h2>9. Sign-off</h2>")
    w(f"<dl class='signoff'><div><dt>Prepared by</dt><dd>{esc(brand.PREPARED_BY)}</dd></div>"
      f"<div><dt>Approved by</dt><dd>{esc(brand.APPROVED_BY)}</dd></div><div><dt>Date</dt><dd>{rd.day(now)}</dd></div></dl>")
    w(f"<footer><span>{esc(brand.COMPANY)} · {esc(brand.CONFIDENTIALITY)}</span>"
      f"<span>{esc(slc.product)} · run of {run_date}</span></footer>")
    w("</div></body></html>")
    return "\n".join(o)


def write(key: str, platforms: list[rd.Platform], root: Path = bs.REPORTS) -> Path:
    out = root / key / "client" / "test-completion-report.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(key, platforms), encoding="utf-8")
    return out


def write_entry(platforms: list[rd.Platform], root: Path) -> Path:
    """`root`/client.html — the combined client report, where a published client site opens, with the two
    platform reports one click away."""
    page = render("all", platforms)
    links = (
        "<p class='note' style='margin-top:14px'>Per platform: "
        + " · ".join(f"<a href='{p.key}/client/test-completion-report.html'>{esc(brand.slice_(p.key).product)} — "
                     "Test Completion Report</a>" for p in platforms)
        + "</p>"
    )
    page = page.replace("</header>", links + "</header>", 1)
    out = root / "client.html"
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("slice", choices=brand.SLICES)
    args = parser.parse_args(argv)
    keys = ["ios", "android"] if args.slice == "all" else [args.slice]
    platforms = [rd.Platform(k, rd.load_report(k)) for k in keys]
    print(f"client: {write(args.slice, platforms)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
