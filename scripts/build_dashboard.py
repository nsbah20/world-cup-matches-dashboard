from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "outputs" / "wc_matches_cleaned"
DIST = ROOT / "dist"


def records(name: str) -> list[dict]:
    df = pd.read_csv(DATA / f"{name}.csv")
    return json.loads(df.astype(object).where(pd.notna(df), None).to_json(orient="records"))


def build_payload() -> dict:
    matches = records("matches_clean")
    team_summary = records("team_summary")
    scorer_summary = records("scorer_summary")
    tournament_summary = records("tournament_summary")
    venue_summary = records("venue_summary")
    quality = records("data_quality")

    return {
        "matches": matches,
        "teams": team_summary,
        "scorers": scorer_summary[:250],
        "tournaments": tournament_summary,
        "venues": venue_summary[:150],
        "quality": quality,
        "meta": {
            "matchRows": len(matches),
            "teamRows": len(records("team_match_long")),
            "scorerRows": len(records("goal_scorers")),
            "source": "WCMatches.csv",
        },
    }


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>World Cup Matches Dashboard</title>
  <style>
    :root {
      --ink: #142536;
      --muted: #657384;
      --line: #d9e3ea;
      --paper: #f5f7f8;
      --panel: #ffffff;
      --teal: #21867a;
      --blue: #2f6f9f;
      --gold: #d89b36;
      --red: #c45b4b;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: var(--paper); }
    header { background: #102b45; color: white; padding: 24px clamp(16px, 3vw, 36px); }
    header h1 { margin: 0; font-size: clamp(1.6rem, 3vw, 2.5rem); letter-spacing: 0; }
    header p { margin: 8px 0 0; color: #d9e6ef; max-width: 920px; }
    main { padding: 20px clamp(14px, 3vw, 36px) 36px; }
    .filters, .grid, .wide, .table-panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
    .filters { display: grid; grid-template-columns: repeat(5, minmax(150px, 1fr)); gap: 12px; padding: 14px; position: sticky; top: 0; z-index: 3; box-shadow: 0 8px 20px rgba(16, 43, 69, .06); }
    label { display: grid; gap: 6px; font-size: .88rem; color: var(--muted); font-weight: 700; }
    select, input { width: 100%; padding: 10px 11px; border: 1px solid #cbd8e1; border-radius: 6px; background: white; color: var(--ink); font-size: 1rem; }
    .kpis { display: grid; grid-template-columns: repeat(6, minmax(130px, 1fr)); gap: 12px; margin: 16px 0; }
    .kpi { background: white; border: 1px solid var(--line); border-radius: 8px; padding: 14px; min-height: 92px; }
    .kpi span { display: block; color: var(--muted); font-weight: 700; font-size: .9rem; }
    .kpi strong { display: block; margin-top: 10px; font-size: clamp(1.45rem, 2vw, 2rem); color: #12314d; }
    .layout { display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; align-items: start; }
    .grid { padding: 16px; min-height: 340px; }
    .wide { padding: 16px; margin-top: 16px; }
    h2 { margin: 0 0 12px; font-size: 1.1rem; }
    .chart { width: 100%; min-height: 280px; }
    svg { width: 100%; height: 100%; overflow: visible; }
    .bar { fill: var(--blue); }
    .bar.alt { fill: var(--teal); }
    .axis text, .small { fill: var(--muted); color: var(--muted); font-size: 12px; }
    .line { fill: none; stroke: var(--gold); stroke-width: 3; }
    .line2 { fill: none; stroke: var(--teal); stroke-width: 3; }
    .dot { fill: var(--gold); }
    .tables { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
    .table-panel { padding: 14px; overflow: hidden; }
    table { width: 100%; border-collapse: collapse; font-size: .92rem; }
    th, td { padding: 9px 8px; border-bottom: 1px solid #e8eef2; text-align: left; white-space: nowrap; }
    th { color: var(--muted); font-size: .82rem; background: #eef5f8; position: sticky; top: 0; }
    td.num, th.num { text-align: right; }
    .scroll { max-height: 440px; overflow: auto; }
    .quality { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .badge { border: 1px solid var(--line); background: #f8fbfc; border-radius: 999px; padding: 7px 10px; font-size: .85rem; color: var(--muted); }
    .empty { padding: 36px; text-align: center; color: var(--muted); border: 1px dashed var(--line); border-radius: 8px; }
    @media (max-width: 1050px) {
      .filters, .kpis { grid-template-columns: repeat(2, 1fr); }
      .layout, .tables { grid-template-columns: 1fr; }
    }
    @media (max-width: 620px) {
      .filters, .kpis { grid-template-columns: 1fr; position: static; }
      th, td { white-space: normal; }
    }
  </style>
</head>
<body>
  <header>
    <h1>World Cup Matches Dashboard</h1>
    <p>Explore cleaned FIFA World Cup match results, tournament trends, team performance, scorers, venues, attendance, and data-quality checks from 1930 through 2022.</p>
  </header>
  <main>
    <section class="filters" aria-label="Dashboard filters">
      <label>Year <select id="year"></select></label>
      <label>Team <select id="team"></select></label>
      <label>Stage <select id="stage"></select></label>
      <label>Host <select id="host"></select></label>
      <label>Search <input id="search" placeholder="team, venue, scorer" /></label>
    </section>

    <section class="kpis" id="kpis"></section>

    <section class="layout">
      <div class="grid">
        <h2>Goals and Attendance by Tournament</h2>
        <div class="chart" id="trend"></div>
      </div>
      <div class="grid">
        <h2>Top Teams in Current View</h2>
        <div class="chart" id="teamsChart"></div>
      </div>
    </section>

    <section class="wide">
      <h2>Stage Mix</h2>
      <div class="chart" id="stageChart"></div>
    </section>

    <section class="tables">
      <div class="table-panel">
        <h2>Filtered Matches</h2>
        <div class="scroll"><table id="matchesTable"></table></div>
      </div>
      <div class="table-panel">
        <h2>Top Scorers</h2>
        <div class="scroll"><table id="scorersTable"></table></div>
      </div>
      <div class="table-panel">
        <h2>Venue Summary</h2>
        <div class="scroll"><table id="venuesTable"></table></div>
      </div>
      <div class="table-panel">
        <h2>Data Quality</h2>
        <div class="quality" id="quality"></div>
      </div>
    </section>
  </main>
  <script id="dashboard-data" type="application/json">__DATA__</script>
  <script>
    const data = JSON.parse(document.getElementById("dashboard-data").textContent);
    const els = {
      year: document.getElementById("year"),
      team: document.getElementById("team"),
      stage: document.getElementById("stage"),
      host: document.getElementById("host"),
      search: document.getElementById("search"),
      kpis: document.getElementById("kpis"),
      trend: document.getElementById("trend"),
      teamsChart: document.getElementById("teamsChart"),
      stageChart: document.getElementById("stageChart"),
      matchesTable: document.getElementById("matchesTable"),
      scorersTable: document.getElementById("scorersTable"),
      venuesTable: document.getElementById("venuesTable"),
      quality: document.getElementById("quality"),
    };

    const fmt = new Intl.NumberFormat("en-US");
    const by = (arr, key) => [...new Set(arr.map(d => d[key]).filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));

    function options(select, values, label) {
      select.innerHTML = `<option value="">All ${label}</option>` + values.map(v => `<option>${v}</option>`).join("");
    }

    options(els.year, by(data.matches, "wc_year"), "years");
    options(els.team, by([...data.matches.map(m => ({ team: m.home_team })), ...data.matches.map(m => ({ team: m.away_team }))], "team"), "teams");
    options(els.stage, by(data.matches, "stage"), "stages");
    options(els.host, by(data.matches, "host_country"), "hosts");

    function filteredMatches() {
      const y = els.year.value, t = els.team.value, s = els.stage.value, h = els.host.value, q = els.search.value.trim().toLowerCase();
      return data.matches.filter(m => {
        const text = `${m.home_team} ${m.away_team} ${m.venue} ${m.stage} ${m.host_country} ${m.home_goal_scorers || ""} ${m.away_goal_scorers || ""}`.toLowerCase();
        return (!y || String(m.wc_year) === y)
          && (!t || m.home_team === t || m.away_team === t)
          && (!s || m.stage === s)
          && (!h || m.host_country === h)
          && (!q || text.includes(q));
      });
    }

    function rollup(rows, key, measures) {
      const map = new Map();
      for (const row of rows) {
        const k = row[key] || "Unknown";
        if (!map.has(k)) map.set(k, { key: k, matches: 0, goals: 0, attendance: 0, wins: 0 });
        const r = map.get(k);
        r.matches += 1;
        r.goals += Number(row.total_goals || 0);
        r.attendance += Number(row.attendance || 0);
        if (measures?.winner && row.winner === k) r.wins += 1;
      }
      return [...map.values()];
    }

    function teamRollup(rows) {
      const map = new Map();
      for (const m of rows) {
        for (const side of ["home", "away"]) {
          const team = side === "home" ? m.home_team : m.away_team;
          const gf = Number(side === "home" ? m.home_score : m.away_score);
          const ga = Number(side === "home" ? m.away_score : m.home_score);
          if (!map.has(team)) map.set(team, { key: team, matches: 0, wins: 0, goals: 0, points: 0 });
          const r = map.get(team);
          r.matches += 1;
          r.goals += gf;
          const won = m.winner === team;
          const draw = m.winner === "Draw";
          r.wins += won ? 1 : 0;
          r.points += won ? 3 : draw ? 1 : 0;
        }
      }
      return [...map.values()].sort((a, b) => b.points - a.points || b.goals - a.goals).slice(0, 10);
    }

    function kpis(rows) {
      const goals = rows.reduce((a, b) => a + Number(b.total_goals || 0), 0);
      const attendance = rows.reduce((a, b) => a + Number(b.attendance || 0), 0);
      const teams = new Set(rows.flatMap(m => [m.home_team, m.away_team])).size;
      const shootouts = rows.filter(m => m.went_to_penalties === true || m.went_to_penalties === "True").length;
      const cards = [
        ["Matches", fmt.format(rows.length)],
        ["Goals", fmt.format(goals)],
        ["Goals / Match", rows.length ? (goals / rows.length).toFixed(2) : "0.00"],
        ["Attendance", fmt.format(attendance)],
        ["Teams", fmt.format(teams)],
        ["Penalty Shootouts", fmt.format(shootouts)],
      ];
      els.kpis.innerHTML = cards.map(([label, value]) => `<div class="kpi"><span>${label}</span><strong>${value}</strong></div>`).join("");
    }

    function svgBar(container, rows, valueKey, labelKey, colorClass = "bar") {
      if (!rows.length) return container.innerHTML = `<div class="empty">No data for this view</div>`;
      const w = 760, h = 300, left = 145, right = 20, top = 18, bottom = 34;
      const max = Math.max(...rows.map(r => Number(r[valueKey] || 0)), 1);
      const barH = Math.max(12, (h - top - bottom) / rows.length - 6);
      const items = rows.map((r, i) => {
        const y = top + i * ((h - top - bottom) / rows.length);
        const bw = (Number(r[valueKey] || 0) / max) * (w - left - right);
        return `<text x="${left - 8}" y="${y + barH * .75}" text-anchor="end" class="small">${r[labelKey]}</text>
          <rect class="${colorClass}" x="${left}" y="${y}" width="${bw}" height="${barH}" rx="3"></rect>
          <text x="${left + bw + 6}" y="${y + barH * .75}" class="small">${fmt.format(r[valueKey])}</text>`;
      }).join("");
      container.innerHTML = `<svg viewBox="0 0 ${w} ${h}" role="img">${items}</svg>`;
    }

    function svgLine(container, rows) {
      if (!rows.length) return container.innerHTML = `<div class="empty">No data for this view</div>`;
      const w = 780, h = 300, left = 46, right = 18, top = 20, bottom = 42;
      const years = rows.map(r => r.key).sort((a, b) => Number(a) - Number(b));
      const vals = years.map(y => rows.find(r => r.key === y));
      const maxA = Math.max(...vals.map(r => r.attendance / Math.max(r.matches, 1)), 1);
      const maxG = Math.max(...vals.map(r => r.goals / Math.max(r.matches, 1)), 1);
      const x = i => left + (i / Math.max(vals.length - 1, 1)) * (w - left - right);
      const yA = v => top + (1 - v / maxA) * (h - top - bottom);
      const yG = v => top + (1 - v / maxG) * (h - top - bottom);
      const pathA = vals.map((r, i) => `${i ? "L" : "M"}${x(i)},${yA(r.attendance / r.matches)}`).join(" ");
      const pathG = vals.map((r, i) => `${i ? "L" : "M"}${x(i)},${yG(r.goals / r.matches)}`).join(" ");
      const labels = vals.map((r, i) => i % 2 ? "" : `<text x="${x(i)}" y="${h - 12}" text-anchor="middle" class="small">${r.key}</text>`).join("");
      container.innerHTML = `<svg viewBox="0 0 ${w} ${h}" role="img">
        <line x1="${left}" y1="${h-bottom}" x2="${w-right}" y2="${h-bottom}" stroke="#d9e3ea"/>
        <line x1="${left}" y1="${top}" x2="${left}" y2="${h-bottom}" stroke="#d9e3ea"/>
        <path class="line" d="${pathA}"></path><path class="line2" d="${pathG}"></path>${labels}
        <text x="${left}" y="14" class="small">Orange: avg attendance | Green: goals per match</text>
      </svg>`;
    }

    function table(el, columns, rows) {
      if (!rows.length) return el.innerHTML = `<tbody><tr><td class="empty">No rows match the filters</td></tr></tbody>`;
      el.innerHTML = `<thead><tr>${columns.map(c => `<th class="${c.num ? "num" : ""}">${c.label}</th>`).join("")}</tr></thead>
        <tbody>${rows.map(row => `<tr>${columns.map(c => `<td class="${c.num ? "num" : ""}">${c.f ? c.f(row[c.key], row) : row[c.key] ?? ""}</td>`).join("")}</tr>`).join("")}</tbody>`;
    }

    function render() {
      const rows = filteredMatches();
      kpis(rows);
      const years = rollup(rows, "wc_year");
      svgLine(els.trend, years);
      svgBar(els.teamsChart, teamRollup(rows), "points", "key", "bar alt");
      svgBar(els.stageChart, rollup(rows, "stage_group").sort((a,b) => b.matches - a.matches), "matches", "key");
      table(els.matchesTable, [
        { label: "Date", key: "match_date" },
        { label: "Year", key: "wc_year", num: true },
        { label: "Stage", key: "stage" },
        { label: "Match", key: "home_team", f: (_, r) => `${r.home_team} ${r.scoreline} ${r.away_team}` },
        { label: "Venue", key: "venue_city" },
        { label: "Attendance", key: "attendance", num: true, f: v => fmt.format(v) },
      ], rows.slice(0, 200));
      const scorerTerm = els.search.value.trim().toLowerCase();
      table(els.scorersTable, [
        { label: "Scorer", key: "scorer" },
        { label: "Goals", key: "goals", num: true },
        { label: "Tournaments", key: "tournaments", num: true },
        { label: "Teams", key: "teams" },
      ], data.scorers.filter(s => !scorerTerm || `${s.scorer} ${s.teams}`.toLowerCase().includes(scorerTerm)).slice(0, 80));
      table(els.venuesTable, [
        { label: "Venue", key: "venue_name" },
        { label: "City", key: "venue_city" },
        { label: "Matches", key: "matches", num: true },
        { label: "Avg Attendance", key: "avg_attendance", num: true, f: v => fmt.format(v) },
      ], data.venues.slice(0, 80));
      els.quality.innerHTML = data.quality.map(q => `<span class="badge">${q.check}: ${q.value} (${q.status})</span>`).join("");
    }

    for (const el of [els.year, els.team, els.stage, els.host, els.search]) el.addEventListener("input", render);
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(build_payload(), ensure_ascii=False)
    (DIST / "index.html").write_text(HTML.replace("__DATA__", payload), encoding="utf-8")


if __name__ == "__main__":
    main()
