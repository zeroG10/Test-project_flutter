#!/usr/bin/env python3
"""The combined internal report: iOS and Android side by side, every number a link into the platform reports.

It renders nothing of its own about a test: the platform reports (`build_summary.py`) hold every check, test, step,
screenshot and defect page, and this report links into them — a module row opens the combined module page (each
check with its iOS and Android verdicts), a verdict opens that check on the platform's module page, a defect opens
its report, a test that could not run opens its steps. Its verdict is the worse of the two platforms'.

Output: `automation/mobile/reports/mobile/internal/` (index.html + one page per module), beside
`…/ios/internal/` and `…/android/internal/`, which must be built first (`build_reports.py` does both).
"""

from __future__ import annotations

import html
from datetime import UTC, datetime
from pathlib import Path

import brand
import build_summary as bs
import report_data as rd

VCLASS = {"Passed": "pass", "Held red": "known", "Failed": "fail", "Blocked": "block", "Not automated": "idle"}


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


class Combined:
    """`to_root`: from the page to the reports root ("../../" from mobile/internal/; "" for the copy at the root
    that a published site opens on); `here`: from the root to the combined report's own folder."""

    def __init__(self, platforms: list[rd.Platform], to_root: str = "../../", here: str = "") -> None:
        self.ps = platforms
        self.slice = brand.slice_("mobile")
        self.now = datetime.now(UTC)
        self.end = max(p.end for p in platforms)
        self.to_root = to_root
        self.here = here

    # --- links into the platform reports --------------------------------------------------

    def base(self, p: rd.Platform) -> str:
        return f"{self.to_root}{p.key}/internal/"

    def module_link(self, p: rd.Platform, m: bs.Module, anchor: str = "") -> str:
        return f"{self.base(p)}{m.page}{anchor}"

    def bug_href(self, bug: bs.Bug) -> str:
        """A filed defect's page in the report of a platform it holds red, else one it was reproduced on."""
        holding = [p for p in self.ps if p.r.held_by(bug)]
        where = holding or [p for p in self.ps if p.key in rd.bug_platforms(bug)] or self.ps
        return f"{self.base(where[0])}bugs/{bug.bug_id}.html"

    def test_href(self, p: rd.Platform, run: bs.TestRun) -> str:
        m = p.r.module_of_run(run)
        return f"{self.base(p)}{m.page if m else 'index.html'}#t-{run.uid}"

    def verdict_cell(self, p: rd.Platform, m: bs.Module, chk: str) -> str:
        v = p.verdict_of.get(chk, "Not automated")
        return (f"<a class='v {VCLASS.get(v, 'idle')}' href='{esc(self.module_link(p, m, '#' + chk))}' "
                f"title='{esc(p.name)}: open the check'>{esc(v)}</a>")

    # --- shell ---------------------------------------------------------------------------

    def document(self, title: str, body: str) -> str:
        return (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'>"
            f"<title>{esc(title)}</title>{bs.FONTS}<style>{bs.CSS}"
            "a.v{text-decoration:none}a.v:hover{outline:1px solid currentColor}"
            ".os{font:600 12px/1 var(--mono);padding:4px 7px;border-radius:5px;background:var(--accent-soft);"
            "color:var(--accent);white-space:nowrap;text-decoration:none}"
            "table.both{table-layout:fixed;min-width:620px}table.both col.c1{width:132px}table.both col.c3{width:132px}"
            "tr.total td{font-weight:700}.ok{color:var(--pass);font-weight:700}.warn{color:var(--known);font-weight:700}"
            f"</style></head><body>{body}</body></html>"
        )

    def os_link(self, p: rd.Platform, href: str = "index.html") -> str:
        return f"<a class='os' href='{esc(self.base(p) + href)}'>{esc(p.name)}</a>"

    # --- index ---------------------------------------------------------------------------

    def index(self) -> str:
        ps = self.ps
        a, b = ps
        label, cls = rd.worst(ps)
        run_date = self.end.strftime("%Y-%m-%d")
        both = rd.passed_on_both(a, b)
        o: list[str] = []
        w = o.append
        w("<div class='wrap'><header>")
        w(brand.brandbar("internal"))
        w(f"<div class='eyebrow'>Test completion report · Mobile regression · {' & '.join(p.name for p in ps)}</div>")
        w(f"<h1>{esc(self.slice.product)} — Test Completion Report <span class='tag'>Internal</span> "
          f"<span class='pill {cls}'>{esc(label)}</span></h1>")
        w("<p class='muted' style='margin:0'>The verdict is the worse of the two platforms'. "
          + " ".join(f"{p.name}: {esc(p.verdict[0])} — {p.unexpected} unexpected, {p.tc['Failed']} red tests held by known "
                     f"defects, {p.tc['Blocked']} could not run." for p in ps) + "</p>")
        w("<p style='margin:4px 0 0'><b>Checklist now</b> (each platform's reported run): "
          + " · ".join(f"<b>{p.name}</b> {p.c['Passed']} green, {p.c['Held red']} red with a known cause, "
                       f"{p.c['Blocked']} blocked, {p.c['Failed']} red and unexplained" for p in ps)
          + f" · <b>passed on both</b> {both} of {a.s.total}.</p>")
        facts = [
            *((f"{p.name} run finished", f"{p.end:%Y-%m-%d %H:%M} UTC · harness {p.r.env.get('Harness commit', '?')}") for p in ps),
            *((f"{p.name} device", f"{p.facts['device']} · {p.facts['os']}") for p in ps),
            ("App build", f"{a.facts['app']} · {a.facts['build']}"),
            ("App type", a.facts["app_type"]),
            ("App source", a.r.env.get("App source", "not recorded")),
            ("Report generated", f"{self.now:%Y-%m-%d %H:%M} UTC"),
        ]
        w("<dl class='facts'>" + "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in facts) + "</dl>")
        online = (f"<a href='{esc(self.slice.internal_url)}'>{esc(self.slice.internal_url)}</a>"
                  if self.slice.internal_url else "—")
        runs = " and ".join(f"{p.name} run of {p.run_date}" for p in ps)
        w(f"<p class='docinfo'><b>Document.</b> Version of {run_date} ({runs}) · Source: "
          "<code>automation/mobile/reports/mobile/internal/index.html</code> · Online: " + online + " · PDF: "
          f"<code>{esc(self.slice.pdf_name('TestCompletionReport_INTERNAL', run_date))}</code> · "
          f"{esc(brand.CONFIDENTIALITY)}, {esc(brand.COMPANY)} internal.</p>")
        w("<nav class='layer' aria-label='Report layers'>" + "".join(
            f"<a href='#{k}'>{t}</a>" for k, t in (
                ("summary", "Summary"), ("modules", "By module"), ("defects", "Open defects"), ("blocked", "Could not run"),
                ("not-automated", "Not automated"), ("exit", "Exit criteria"), ("history", "Run history"),
                ("technical", "Technical detail")))
          + "".join(f"<a href='{esc(self.base(p))}index.html'>{esc(p.name)} report →</a>" for p in ps) + "</nav></header>")

        # summary
        w("<section id='summary'><h2>Summary</h2>")
        w(f"<p class='lead'>Both platforms run the same QA checklist of <b>{a.s.total}</b> checks across "
          f"{len(a.r.modules)} modules against the same app build. "
          + " ".join(f"<b>{p.name}</b>: {p.s.automated} automated ({rd.pct(p.s.automated, p.s.total)}), <b>{p.c['Passed']}</b> "
                     f"passed, {p.c['Held red']} red with a known cause, {p.c['Blocked']} could not run (run of "
                     f"{rd.day(p.end)})." for p in ps)
          + f" <b>{both}</b> checks passed on both platforms.</p>")
        w("<div class='kpis'>"
          f"<div class='kpi'><b>{a.s.total}</b><span>checks in the QA checklist</span></div>"
          + "".join(f"<div class='kpi pass'><b>{p.c['Passed']}</b><span>passed on {p.name} · of {p.s.automated} automated</span></div>"
                    for p in ps)
          + f"<div class='kpi pass'><b>{both}</b><span>passed on both platforms</span></div></div>")
        rows = "".join(
            f"<tr><td>{self.os_link(p)}</td><td class=num>{p.s.total}</td><td class=num>{p.s.automated}</td>"
            f"<td class=num><a href='{esc(self.base(p))}index.html#summary'>{p.c['Passed']}</a></td>"
            f"<td class=num><a href='{esc(self.base(p))}index.html#defects'>{p.c['Held red']}</a></td>"
            f"<td class=num><a href='{esc(self.base(p))}index.html#blocked'>{p.c['Blocked']}</a></td>"
            f"<td class=num><a href='{esc(self.base(p))}index.html#not-automated'>{p.c['Not automated']}</a></td>"
            f"<td><span class='pill {p.verdict[1]}'>{esc(p.verdict[0])}</span></td></tr>" for p in ps)
        tot = lambda k: sum(p.c[k] for p in ps)  # noqa: E731
        rows += (f"<tr class='total'><td>Total</td><td class=num>{sum(p.s.total for p in ps)}</td>"
                 f"<td class=num>{sum(p.s.automated for p in ps)}</td><td class=num>{tot('Passed')}</td>"
                 f"<td class=num>{tot('Held red')}</td><td class=num>{tot('Blocked')}</td><td class=num>{tot('Not automated')}</td>"
                 f"<td><span class='pill {cls}'>{esc(label)}</span></td></tr>")
        w("<h3>By platform</h3><div class='scroll'><table><thead><tr><th>Platform</th><th class=num>Checks</th>"
          "<th class=num>Automated</th><th class=num>Passed</th><th class=num>Held red</th><th class=num>Blocked</th>"
          f"<th class=num>Not automated</th><th>Verdict</th></tr></thead><tbody>{rows}</tbody></table></div>")
        w(f"<p class='note'>The total counts each check once per platform ({a.s.total} × 2); a check passes for the app "
          f"only when it passed on both: {both} of {a.s.total}. Every number opens the platform report.</p>")
        asks = self.decisions()
        w("<div class='box' style='margin-top:22px'><h3>What needs a decision</h3><ul>"
          + ("".join(f"<li>{x}</li>" for x in asks) or "<li>Nothing is waiting on the owner.</li>") + "</ul></div></section>")

        # by module
        w("<section id='modules'><h2>By module</h2><div class='scroll'><table class='mods'><thead><tr><th>Module</th>"
          "<th class=num>Checks</th>" + "".join(f"<th class=num>{p.name} passed / automated</th><th class=num>{p.name} held red</th>"
                                                 for p in ps)
          + "<th class=num>Passed on both</th></tr></thead><tbody>")
        for ma, mb in zip(a.r.modules, b.r.modules, strict=True):
            ids = [row.item.chk_id for row in ma.rows]
            cells = ""
            for p, m in ((a, ma), (b, mb)):
                c = p.r.counts(m.rows)
                cells += (f"<td class=num><a href='{esc(self.module_link(p, m))}'>{c['Passed']} / "
                          f"{len(m.rows) - c['Not automated']}</a></td><td class=num>{c['Held red'] + c['Failed']}</td>")
            w(f"<tr><td><a href='{esc(self.here + ma.page)}'>{esc(ma.label)}</a></td><td class=num>{len(ma.rows)}</td>{cells}"
              f"<td class=num>{rd.passed_on_both(a, b, ids)}</td></tr>")
        w("</tbody></table></div><p class='note'>A module opens every check with its verdict on each platform; a "
          "platform's number opens that platform's module page (every test, step and screen).</p></section>")

        # defects
        bugs: dict[str, tuple[bs.Bug, list[rd.Platform]]] = {}
        for p in ps:
            for x in p.bugs:
                bugs.setdefault(x.bug_id, (x, []))[1].append(p)
        w(f"<section id='defects'><h2>Open defects · {len(bugs)}</h2>")
        w("<div class='scroll'><table><thead><tr><th>Defect</th><th>Module</th><th>What is wrong</th><th>Platform</th>"
          "<th>Severity</th><th>Priority</th><th>Checks held red</th></tr></thead><tbody>")
        for x, plats in sorted(bugs.values(), key=lambda t: (rd.SEVERITY_ORDER.get(t[0].severity, 9), t[0].bug_id)):
            held = "<br>".join(
                f"{p.name}: " + ", ".join(
                    f"<a href='{esc(self.module_link(p, p.r.module_of_chk[c], '#' + c))}'>{esc(c.removeprefix('CHK-'))}</a>"
                    for c in p.r.held_by(x)) for p in ps if p.r.held_by(x)) or "<span class='muted'>—</span>"
            where = "Both" if len(plats) == len(ps) else plats[0].name
            pri = esc(x.priority) + (" <span class='muted'>proposed</span>" if x.priority_proposed else "")
            w(f"<tr><td class='mono id'><a href='{esc(self.bug_href(x))}'>{esc(x.bug_id)}</a></td>"
              f"<td>{esc(self.module_name(x.module_dir))}</td><td>{esc(x.title)}</td><td><span class='os'>{where}</span></td>"
              f"<td><span class='sev {esc(x.severity)}'>{esc(x.severity)} {esc(rd.SEVERITY_WORD.get(x.severity, ''))}</span></td>"
              f"<td class='mono'>{pri}</td><td class='mono'>{held}</td></tr>")
        w("</tbody></table></div>")
        drafts: dict[str, tuple[bs.Bug, list[rd.Platform]]] = {}
        for p in ps:
            for x in p.accepted:
                drafts.setdefault(x.bug_id, (x, []))[1].append(p)
        if drafts:
            w(f"<h3 style='margin-top:22px'>Known, not filed · {len(drafts)}</h3><p>The owner triaged these as the app's "
              "behaviour and decided not to file them; their tests stay red and count as held red by a known defect.</p>"
              "<div class='scroll'><table><thead><tr><th>Draft</th><th>Module</th><th>What is wrong</th><th>Platform</th>"
              "<th>Checks held red</th></tr></thead><tbody>")
            for x, plats in drafts.values():
                held = "<br>".join(
                    f"{p.name}: " + ", ".join(
                        f"<a href='{esc(self.module_link(p, p.r.module_of_chk[c], '#' + c))}'>{esc(c.removeprefix('CHK-'))}</a>"
                        for c in p.r.held_by(x)) for p in plats)
                w(f"<tr><td class='mono id'>{esc(x.bug_id)}</td><td>{esc(self.module_name(x.module_dir))}</td>"
                  f"<td>{esc(x.title)}</td><td><span class='os'>{' & '.join(p.name for p in plats)}</span></td>"
                  f"<td class='mono'>{held}</td></tr>")
            w("</tbody></table></div>")
        w("</section>")

        # could not run
        blocked = [(p, x) for p in ps for x in p.blocked]
        w(f"<section id='blocked'><h2>Could not run · {len(blocked)}</h2>")
        if blocked:
            w("<div class='scroll'><table><thead><tr><th>Platform</th><th>Test</th><th>Why</th></tr></thead><tbody>")
            for p, x in blocked:
                w(f"<tr><td>{self.os_link(p)}</td><td><a href='{esc(self.test_href(p, x))}'>{esc(x.title)}</a></td>"
                  f"<td>{esc(bs._reason(x.detail))}</td></tr>")
            w("</tbody></table></div>")
        else:
            w("<p>Every test ran on both platforms.</p>")
        w("</section>")

        # not automated
        kinds: dict[str, str] = {}
        for p in ps:
            kinds.update({k: v.title for k, v in p.r.kinds.items()})
        counts = [p.kind_counts() for p in ps]
        order = sorted({k for c in counts for k in c}, key=lambda k: -sum(c.get(k, 0) for c in counts))
        w("<section id='not-automated'><h2>Why checks are not automated · "
          + " / ".join(f"{p.name} {p.c['Not automated']}" for p in ps) + "</h2>")
        w("<div class='scroll'><table><thead><tr><th>Reason</th>" + "".join(f"<th class=num>{p.name}</th>" for p in ps)
          + "</tr></thead><tbody>")
        for k in order:
            w(f"<tr><td><b>{esc(kinds.get(k, k or 'No reason written'))}</b></td>" + "".join(
                f"<td class=num><a href='{esc(self.base(p))}index.html#not-automated'>{c.get(k, 0)}</a></td>" if c.get(k)
                else "<td class=num>—</td>" for p, c in zip(ps, counts, strict=True)) + "</tr>")
        w("</tbody></table></div><p class='note'>Each platform's records: "
          + ", ".join(f"<code>{esc(p.r.reasons_file)}</code>" for p in ps) + "; every check with its reason is in the "
          "platform reports' technical detail.</p></section>")

        # exit criteria
        import client_report as cr  # noqa: PLC0415 — one definition of the criteria for both audiences

        ea, eb = (cr.exit_criteria(p) for p in ps)
        w("<section id='exit'><h2>Exit criteria</h2><div class='scroll'><table><thead><tr><th>Criterion</th>"
          + "".join(f"<th>{p.name}</th>" for p in ps) + "<th>Detail</th></tr></thead><tbody>")
        for x, y in zip(ea, eb, strict=False):
            w(f"<tr><td>{esc(x[0])}</td><td>{cr.yes(x[1])}</td><td>{cr.yes(y[1])}</td>"
              f"<td>{esc(a.name)}: {esc(x[2])} · {esc(b.name)}: {esc(y[2])}</td></tr>")
        w("</tbody></table></div></section>")

        # history
        w("<section id='history'><h2>Run history</h2><div class='scroll'><table><thead><tr><th>Platform</th><th>Run</th>"
          "<th>Finished (UTC)</th><th>Harness</th><th class=num>Tests</th><th class=num>Red</th><th class=num>Blocked</th>"
          "<th class=num>Unexpected</th><th class=num>Checks passed</th></tr></thead><tbody>")
        for p in ps:
            for h in p.r.history:
                w(f"<tr><td>{self.os_link(p, 'index.html#stability')}</td><td class='mono'>{esc(h.label)}</td>"
                  f"<td class='mono'>{h.finished:%Y-%m-%d %H:%M}</td><td class='mono'>{esc(h.harness)}</td>"
                  f"<td class=num>{h.tests}</td><td class=num>{h.counts.get('Failed', 0)}</td>"
                  f"<td class=num>{h.counts.get('Blocked', 0)}</td><td class=num>{h.unexpected}</td>"
                  f"<td class=num>{h.checks.passed}</td></tr>")
            w(f"<tr class='total'><td>{self.os_link(p)}</td><td class='mono'>{esc(p.slice.run.name if p.slice.run else '')} "
              f"(reported)</td><td class='mono'>{p.end:%Y-%m-%d %H:%M}</td>"
              f"<td class='mono'>{esc(p.r.env.get('Harness commit', ''))}</td><td class=num>{len(p.r.runs)}</td>"
              f"<td class=num>{p.tc['Failed']}</td><td class=num>{p.tc['Blocked']}</td><td class=num>{p.unexpected}</td>"
              f"<td class=num>{p.c['Passed']}</td></tr>")
        w("</tbody></table></div><p class='note'>"
          + " ".join(esc(p.slice.history_note) for p in ps if p.slice.history_note) + "</p></section>")

        # technical
        w("<section id='technical' class='divider'><div class='eyebrow'>For the technical team</div>"
          "<h2 style='margin-top:6px'>Technical detail</h2><div class='scroll'><table><thead><tr><th></th>"
          + "".join(f"<th>{p.name}</th>" for p in ps) + "</tr></thead><tbody>")
        for label_, get in (
            ("Operating system", lambda p: p.facts["os"]),
            ("Device", lambda p: p.facts["device"]),
            ("App build", lambda p: f"{p.facts['app']} · {p.facts['build']}"),
            ("App type", lambda p: p.facts["app_type"]),
            ("Harness commit", lambda p: p.r.env.get("Harness commit", "")),
            ("Tools", lambda p: p.r.tools or bs.tool_versions(p.key)),
            ("Reported run", lambda p: bs.rel_to_repo(p.slice.run) if p.slice.run else "—"),
        ):
            w(f"<tr><td><b>{esc(label_)}</b></td>" + "".join(f"<td>{esc(get(p))}</td>" for p in ps) + "</tr>")
        w("</tbody></table></div><div class='grid2' style='margin-top:14px'><div class='box'><h3>How this report is "
          "built</h3><ul><li>Numbers: each platform's reported run (setup/project.yaml → report.slices), read the same way "
          "as the platform reports — nothing here is computed differently.</li><li>Verdict: the worse of the two "
          "platforms'. A check passes for the app only when it passed on both.</li><li>Tools versions: as installed on "
          "the QA machine when the report was built.</li><li>This page: <code>automation/tools/mobile_report.py</code>; "
          "all reports at once: <code>automation/tools/build_reports.py</code>.</li></ul></div><div class='box'><h3>Where "
          "to look</h3><ul>" + "".join(
              f"<li>{esc(p.name)}: <a href='{esc(self.base(p))}index.html'>the {esc(p.name)} report</a> — every check, test, "
              f"step and screen; traceability <code>qa/mobile/{p.key}/final-traceability.md</code>.</li>" for p in ps)
          + "<li>Owner rulings: <code>docs/notes/decisions.md</code>.</li></ul></div></div></section>")
        w(f"<p class='note' style='margin-top:34px'>Generated by <code>automation/tools/mobile_report.py</code>, "
          f"{self.now:%Y-%m-%d %H:%M} UTC, from the platform runs, the checklists, the bug reports and the reasons files.</p>")
        w("</div>")
        return "\n".join(o)

    def module_name(self, module_dir: str) -> str:
        return next((m.label for m in self.ps[0].r.modules if m.key == module_dir), module_dir)

    def decisions(self) -> list[str]:
        asks = []
        proposed = {b.bug_id: b for p in self.ps for b in p.bugs if b.priority_proposed}
        if proposed:
            asks.append(f"The priority of {len(proposed)} open defects is QA's proposal — the owner / PM decide: "
                        + ", ".join(f"<a href='{esc(self.bug_href(b))}'>{esc(i)}</a>" for i, b in sorted(proposed.items())))
        for p in self.ps:
            missing = [f"{d} ({o})" for d, o, covered in p.p0() if not covered]
            if missing:
                asks.append(f"{esc(p.name)}: P0 devices of the device matrix not tested — {esc(', '.join(missing))}. "
                            "Test them, or confirm they are not P0 for this release.")
        return asks

    # --- module pages ----------------------------------------------------------------------

    def module_page(self, i: int) -> str:
        a, b = self.ps
        ma, mb = a.r.modules[i], b.r.modules[i]
        mods = a.r.modules
        o: list[str] = ["<div class='wrap'>" + brand.brandbar("internal") + "<nav class='top' style='margin-top:16px'>"
                        "<a href='index.html'>← Summary</a><a href='index.html#defects'>Open defects</a>"]
        w = o.append
        if i > 0:
            w(f"<a href='{esc(mods[i - 1].page)}'>← {esc(mods[i - 1].label)}</a>")
        if i + 1 < len(mods):
            w(f"<a href='{esc(mods[i + 1].page)}'>{esc(mods[i + 1].label)} →</a>")
        w("".join(f"<a href='{esc(self.module_link(p, m))}'>{esc(p.name)}: tests and screens →</a>"
                  for p, m in ((a, ma), (b, mb))) + "</nav>")
        ids = [row.item.chk_id for row in ma.rows]
        w(f"<p class='eyebrow'>Module {esc(ma.number)} · iOS & Android · {esc(self.slice.product)}</p><h1>{esc(ma.name)}</h1>")
        ca, cb = a.r.counts(ma.rows), b.r.counts(mb.rows)
        w("<div class='cards'>" + "".join(f"<div class='card'><b>{n}</b><span>{esc(t)}</span></div>" for n, t in (
            (len(ma.rows), "checks"), (ca["Passed"], f"passed on {a.name}"), (cb["Passed"], f"passed on {b.name}"),
            (rd.passed_on_both(a, b, ids), "passed on both"))) + "</div>")
        w("<p class='note'>Each verdict opens the check on that platform's module page — its test, steps, screens and, "
          "for a red check, its defect; a check not automated shows its written reason there.</p>")
        section = None
        for row in ma.rows:
            if row.item.section != section:
                if section is not None:
                    w("</tbody></table></div>")
                section = row.item.section
                w(f"<p class='sect'>{esc(section)}</p><div class='scroll'><table class='both'><colgroup><col class='c1'>"
                  f"<col><col class='c3'><col class='c3'></colgroup><thead><tr><th>Check</th><th>What</th>"
                  f"<th>{a.name}</th><th>{b.name}</th></tr></thead><tbody>")
            chk = row.item.chk_id
            w(f"<tr id='{esc(chk)}'><td class='mono id'>{esc(chk)}</td><td>{esc(a.r.red.text(row.item.text))}</td>"
              f"<td class='nowrap'>{self.verdict_cell(a, ma, chk)}</td><td class='nowrap'>{self.verdict_cell(b, mb, chk)}</td></tr>")
        if section is not None:
            w("</tbody></table></div>")
        w("</div>")
        return "\n".join(o)


def write(platforms: list[rd.Platform], root: Path = bs.REPORTS, entry: bool = False) -> Path:
    """`root`/mobile/internal/ — and with `entry`, `root`/internal.html: the same summary at the root, where a
    published site opens."""
    report = Combined(platforms)
    title = f"{report.slice.product_short} QA Report"
    out = root / "mobile" / "internal"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(report.document(title, report.index()), encoding="utf-8")
    for i, m in enumerate(platforms[0].r.modules):
        (out / m.page).write_text(report.document(f"{m.name} — iOS & Android", report.module_page(i)), encoding="utf-8")
    if entry:
        top = Combined(platforms, to_root="", here="mobile/internal/")
        (root / "internal.html").write_text(top.document(title, top.index()), encoding="utf-8")
    return out / "index.html"
