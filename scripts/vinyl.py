"""Render GitHub's public contribution calendar as a spinning vinyl record."""
from datetime import date, timedelta
from html.parser import HTMLParser
from calendar import monthrange
from math import cos, sin, pi
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
    end = dates[-1]
    # Use twelve calendar months, including the current partial month.
    months = sorted({day.replace(day=1) for day in dates})[-12:]
    radii = {month: 125 - 6 * index for index, month in enumerate(months)}
    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 320" role="img">
<title>Contribution LP by Daunt-99</title>
<desc>A spinning vinyl record. The twelve grooves run from oldest month outside to newest inside. Each gold mark is an active day. Brighter marks indicate more activity.</desc>
<defs>
  <linearGradient id="sleeve" x2="1" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#173d3a"/><stop offset="1" stop-color="#0b2328"/></linearGradient>
  <radialGradient id="wax"><stop stop-color="#292a29"/><stop offset=".63" stop-color="#14171a"/><stop offset="1" stop-color="#24292a"/></radialGradient>
  <linearGradient id="gloss" x2="1" y2=".3"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".48" stop-color="#fff" stop-opacity="0"/><stop offset=".55" stop-color="#fff" stop-opacity=".15"/><stop offset=".64" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<style>.disc{animation:spin 10s linear infinite;transform-origin:0 0}@keyframes spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.disc{animation:none}}</style>
<rect width="840" height="320" rx="14" fill="url(#sleeve)"/>
<g fill="#efe5ce" font-family="monospace">
<text x="44" y="63" font-size="13" letter-spacing="2.4">DAUNT–99  /  STEREO</text>
<text x="40" y="134" font-family="Georgia,serif" font-size="54">Contribution LP</text>
<path d="M44 161H405" stroke="#73918a"/>
<text x="44" y="198" font-size="15">12 grooves · one per month</text>
<text x="44" y="222" font-size="15">Gold flecks mark active days</text>''',
           f'<text x="44" y="279" font-size="13" letter-spacing="1.2">{months[0]:%b %Y} — {end:%b %Y}</text></g>',
           '<g transform="translate(624 160)"><circle r="142" fill="#0a191b"/>',
           '<g class="disc"><circle r="137" fill="url(#wax)" stroke="#555d58"/>']
    for radius in radii.values():
        svg.append(f'<circle r="{radius}" fill="none" stroke="#555957" stroke-width=".85"/>')
    for day in dates:
        level = days[day]
        month = day.replace(day=1)
        if month not in radii or not level:
            continue
        angle = 2 * pi * (day.day - 1) / monthrange(day.year, day.month)[1] - pi / 2
        x, y = radii[month] * cos(angle), radii[month] * sin(angle)
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{1 + level * .42:.2f}" fill="#ffdc90" opacity="{.48 + .13 * level:.2f}"/>')
    svg.append('''<circle r="45" fill="#e6a85b"/>
<path d="M-39 -16 Q0 -49 39 -16 Q0 -32 -39 -16Z" fill="#943e32"/>
<text y="25" text-anchor="middle" font-family="monospace" font-size="9" letter-spacing="2" fill="#472b20">SIDE A</text>
</g><circle r="136" fill="url(#gloss)"/><circle r="4.2" fill="#101817" stroke="#f7d7a7"/></g>
<g stroke-linecap="round"><path d="M786 62L779 141L753 173" stroke="#0a1c1e" stroke-width="11" fill="none"/>
<path d="M785 58L778 137L752 169" stroke="#c0b49b" stroke-width="5" fill="none"/>
<circle cx="785" cy="58" r="11" fill="#5e6860" stroke="#d1c09e"/>
<path d="M756 164L747 175" stroke="#e5b66e" stroke-width="9"/></g></svg>''')
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    calendar = Calendar()
    calendar.feed(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(render(calendar.days))
