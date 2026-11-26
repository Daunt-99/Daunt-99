"""Render GitHub's public contribution calendar as an animated star chart."""
from datetime import date, timedelta
from html.parser import HTMLParser
from itertools import groupby
from pathlib import Path
import sys


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        cell = dict(attrs)
        if tag == "td" and "data-date" in cell and "data-level" in cell:
            self.days[date.fromisoformat(cell["data-date"])] = int(cell["data-level"])


def render(days):
    dates = sorted(days)
    if len(dates) < 350 or (dates[-1] - dates[0]).days + 1 != len(dates):
        raise ValueError("Expected a full, continuous contribution calendar")
    start = dates[0] - timedelta(days=(dates[0].weekday() + 1) % 7)

    def position(day):
        week, row = divmod((day - start).days, 7)
        return 45 + 16 * week, 94 + 16 * row

    streaks = [list(run) for active, run in groupby(dates, key=lambda d: days[d] > 0) if active]
    longest = max(streaks, key=len, default=[])
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 930 244" role="img">',
           '<title>Contribution constellations</title>',
           '<desc>One star per active day. Consecutive days connect. Gold marks the longest streak.</desc>',
           '<defs><radialGradient id="sky"><stop stop-color="#1e294f"/><stop offset="1" stop-color="#090e20"/></radialGradient></defs>',
           '<style>text{font-family:monospace;fill:#abb9d6}.shine{animation:twinkle 4s ease-in-out infinite alternate}@keyframes twinkle{to{opacity:.4}}@media(prefers-reduced-motion:reduce){.shine{animation:none}.tracer{display:none}}</style>',
           '<rect width="930" height="244" rx="16" fill="url(#sky)"/>',
           '<text x="36" y="41" style="font:26px Georgia,serif;fill:#eef2ff">Contribution constellations</text>',
           f'<text x="892" y="39" text-anchor="end" font-size="12">{dates[0]:%b %Y} — {dates[-1]:%b %Y}</text>']
    for run in streaks:
        if len(run) > 1:
            points = " ".join(f"{x},{y}" for x, y in map(position, run))
            color = "#d8ac70" if run is longest else "#6184ae"
            svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" opacity=".68"/>')
    gold = set(longest)
    for day in dates:
        x, y = position(day)
        level = days[day]
        if day.day == 1 and x < 880:
            svg.append(f'<text x="{x}" y="72" font-size="10">{day:%b}</text>')
        radius = (0.9, 2.2, 2.9, 3.5, 4.1)[level]
        color = "#ffda98" if day in gold else ("#cadfff" if level else "#424f70")
        if level:
            delay = -(day.toordinal() % 7)
            svg.append(f'<circle class="shine" style="animation-delay:{delay}s" cx="{x}" cy="{y}" r="{radius+2.5}" fill="{color}" fill-opacity=".15"/>')
        svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')
    if len(longest) >= 2:
        route = "M " + " L ".join(f"{x} {y}" for x, y in map(position, longest))
        duration = min(10, max(3, len(longest) * 0.45))
        svg.extend([
            '<g class="tracer">',
            f'<animateMotion path="{route}" dur="{duration}s" repeatCount="indefinite"/>',
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.86;1" dur="{duration}s" repeatCount="indefinite"/>',
            '<circle r="10" fill="#ffbd51" opacity=".16"/>',
            '<circle r="6" fill="#ffbf58" opacity=".55"/>',
            '<path d="M0 -7 Q1 -1 6 0 Q1 1 0 7 Q-1 1 -6 0 Q-1 -1 0 -7Z" fill="#fff4c7"/>',
            '<circle r="2" fill="white"/></g>',
        ])
    svg.extend(['<circle cx="39" cy="221" r="3" fill="#ffda98"/>',
                f'<text x="51" y="225" font-size="11">Longest streak · {len(longest)} days</text>',
                '<text x="892" y="225" text-anchor="end" font-size="11">Larger stars mark busier days</text>', '</svg>'])
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    calendar = Calendar()
    calendar.feed(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(render(calendar.days))
