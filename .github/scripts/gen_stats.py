"""Generate assets/stats.svg from the GitHub GraphQL API.

Runs in Actions with GITHUB_TOKEN (public data only; private contribution
counts appear once 'Private contributions' is enabled on the profile).
The SVG uses prefers-color-scheme so one file renders correctly in both
GitHub themes with no <picture> tag.
"""
import datetime as dt
import json
import os
import subprocess
import urllib.request

USER = "varunk47"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes { stargazerCount }
    }
  }
}
"""


def token():
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["user"]


def main():
    u = fetch()
    c = u["contributionsCollection"]
    contribs = c["contributionCalendar"]["totalContributions"]
    commits = c["totalCommitContributions"] + c["restrictedContributionsCount"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    stats = [
        ("Contributions (year)", contribs),
        ("Commits (year)", commits),
        ("Pull requests", c["totalPullRequestContributions"]),
        ("Issues", c["totalIssueContributions"]),
        ("Stars earned", stars),
        ("Followers", u["followers"]["totalCount"]),
    ]
    today = dt.date.today().isoformat()

    rows = []
    for i, (label, value) in enumerate(stats):
        col, row = i % 2, i // 2
        x, y = 28 + col * 200, 62 + row * 30
        rows.append(
            f'<circle cx="{x}" cy="{y - 4}" r="3" class="dot"/>'
            f'<text x="{x + 12}" y="{y}" class="l">{label}</text>'
            f'<text x="{x + 152}" y="{y}" class="v" text-anchor="end">{value}</text>'
        )

    svg = f'''<svg width="420" height="178" viewBox="0 0 420 178" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats for {USER}">
<style>
  .card {{ fill: #ffffff; stroke: #d0d7de; }}
  .t {{ fill: #24292f; font: 600 16px 'Segoe UI', Ubuntu, Sans-Serif; }}
  .l {{ fill: #57606a; font: 400 12.5px 'Segoe UI', Ubuntu, Sans-Serif; }}
  .v {{ fill: #2F81F7; font: 700 13px 'Segoe UI', Ubuntu, Sans-Serif; }}
  .f {{ fill: #8b949e; font: 400 10px 'Segoe UI', Ubuntu, Sans-Serif; }}
  .dot {{ fill: #2F81F7; }}
  @media (prefers-color-scheme: dark) {{
    .card {{ fill: #0d1117; stroke: #30363d; }}
    .t {{ fill: #c9d1d9; }}
    .l {{ fill: #8b949e; }}
    .v {{ fill: #58a6ff; }}
    .dot {{ fill: #58a6ff; }}
  }}
</style>
<rect class="card" x="0.5" y="0.5" rx="6" width="419" height="177"/>
<text x="28" y="34" class="t">varunk47 on GitHub</text>
{"".join(rows)}
<text x="28" y="162" class="f">updated {today} by GitHub Actions</text>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/stats.svg", "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"assets/stats.svg written: contribs={contribs} commits={commits} "
          f"stars={stars}")


if __name__ == "__main__":
    main()
