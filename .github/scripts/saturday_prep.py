import os, re, json, urllib.request, urllib.parse
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

REPO_BASE = "https://github.com/Tomo2304/leader_speaking_learning/blob/main"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MELBOURNE = ZoneInfo("Australia/Melbourne")
now_mel = datetime.now(MELBOURNE)
if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and now_mel.hour != 9:
    raise SystemExit(0)
start = date(2026, 4, 25)  # first Saturday
today = now_mel.date()

with open("plan/weekly_schedule.md", encoding="utf-8") as f:
    schedule = f.read()
with open("progress/progress_log.md", encoding="utf-8") as f:
    progress = f.read()

week_headers = [(int(n), date.fromisoformat(d))
                for n, d in re.findall(r'### Week (\d+) \((\d{4}-\d{2}-\d{2})\)', schedule)]

# current_num = 0 if no week has started yet (e.g. first Saturday before Week 1)
current_num, current_start = 0, start
for num, wstart in week_headers:
    if wstart <= today:
        current_num, current_start = num, wstart

def get_week_content(num):
    pat = rf'### Week {num} \(\d{{4}}-\d{{2}}-\d{{2}}\)(.*?)(?=\n### Week |\Z)'
    m = re.search(pat, schedule, re.DOTALL)
    return m.group(1) if m else ""

this_content = get_week_content(current_num) if current_num > 0 else ""
next_num = current_num + 1
next_content = get_week_content(next_num)

def get_focus(content):
    m = re.search(r'\*\*Focus: ([^\*\n]+)\*\*', content)
    return m.group(1).strip() if m else "Leadership communication"

this_focus = get_focus(this_content) if this_content else "Plan starts Monday!"
next_focus = get_focus(next_content)

# This week's progress stats from Layer 1 (0 if no week started yet)
done_w = partial_w = skipped_w = 0
if current_num > 0:
    next_monday = current_start + timedelta(days=7)
    for row_date_str, status in re.findall(r'\|\s*(\d{4}-\d{2}-\d{2})\s*\|[^\|]+\|\s*([^\|]+)\|', progress):
        try:
            row_date = date.fromisoformat(row_date_str)
        except ValueError:
            continue
        if current_start <= row_date < next_monday:
            if '✅' in status or 'Done' in status:
                done_w += 1
            elif '〜' in status or 'Partial' in status:
                partial_w += 1
            elif '✗' in status or 'Skipped' in status:
                skipped_w += 1

# Next week dates: if no week started, next week = Week 1 (find its start from headers)
if current_num == 0:
    next_start = week_headers[0][1] if week_headers else (start + timedelta(days=2))
else:
    next_start = current_start + timedelta(days=7)
next_end = next_start + timedelta(days=4)
next_dates = f"{next_start.strftime('%a %d %b')} – {next_end.strftime('%a %d %b')}"

# Next week day-specific tasks (Mon-Fri + Weekend shadowing)
day_rows = re.findall(
    r'\|\s*(\*{0,2}(?:Mon|Tue|Wed|Thu|Fri|Weekend)[^\|]*\*{0,2})\s*\|([^\|]+)\|([^\|]*)\|?([^\|]*)\|?',
    next_content, re.IGNORECASE
)
tasks_lines = []
weekend_how = ""
for day, activity, how, time_col in day_rows:
    day_clean = day.strip().strip('*').strip()
    act_clean = activity.strip()
    if day_clean.lower().startswith('weekend'):
        dur = "20–30 min"
        tasks_lines.append(f"🎬 {day_clean} ({dur}): {act_clean}")
        weekend_how = how.strip()
    else:
        dur = "30 min" if ('⏱' in day or '30' in time_col) else "15 min"
        tasks_lines.append(f"• {day_clean} ({dur}): {act_clean}")
tasks_str = "\n".join(tasks_lines) if tasks_lines else f"Daily practice — {next_focus}"

# Resources for next week — auto-attach links
resources = []
content_lower = next_content.lower()
seen_urls = set()

# Podcasts (Apple Podcasts)
PODCASTS = [
    ("speak up", "🎙 Speak Up (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/speak-up-develop-your-executive-presence-leadership/id1368646965"),
    ("think fast, talk smart", "🎙 Think Fast, Talk Smart (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/think-fast-talk-smart-communication-techniques/id1494989268"),
    ("think fast talk smart", "🎙 Think Fast, Talk Smart (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/think-fast-talk-smart-communication-techniques/id1494989268"),
    ("the knowledge project", "🎙 The Knowledge Project (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/the-knowledge-project/id990149481"),
    ("masters of scale", "🎙 Masters of Scale (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/masters-of-scale/id1227971746"),
    ("hbr ideacast", "🎙 HBR IdeaCast (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/hbr-ideacast/id152022135"),
]
APPS = [
    ("elsa speak", "📱 ELSA Speak (App Store)", "https://apps.apple.com/us/app/elsa-speak-english-learning/id1083804886"),
    ("orai", "📱 Orai (App Store)", "https://apps.apple.com/us/app/orai-improve-public-speaking/id1203178170"),
]
SHADOW_BEST_CLIPS = [
    ("satya nadella", "▶️ Watch: Satya Nadella — WEF 2026 Interview", "https://www.youtube.com/watch?v=1co3zt3-r7I"),
    ("jensen huang", "▶️ Watch: Jensen Huang — Leadership lessons", "https://www.youtube.com/watch?v=ziL09IyS0cw"),
    ("sundar pichai", "▶️ Watch: Sundar Pichai — Google I/O 2025 Keynote", "https://www.youtube.com/watch?v=eIUqw3_YcCI"),
    ("simon sinek", "▶️ Watch: Simon Sinek — Start With Why", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("jacinda ardern", "▶️ Watch: Jacinda Ardern — On Leadership", "https://www.youtube.com/watch?v=iza9O91E4tk"),
    ("amy edmondson", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
]
# Match the inline links in plan/weekly_schedule.md so the brief never surfaces a different URL.
SPECIFIC_CLIPS = [
    ("why good leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe (focus 5:30–8:30, Swenson story — match his pauses)", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("why leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe (focus 5:30–8:30, Swenson story — match his pauses)", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("start with why", "▶️ Watch: Simon Sinek — Start With Why TED Talk", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("psychological safety", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk (focus 4:30–7:30, three-things signposting)", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
    ("the circuit", "▶️ Watch: Sundar Pichai on The Circuit with Emily Chang (focus 12:00–15:00 — micro-pause + framing sentence)", "https://www.youtube.com/watch?v=5puu3kN9l7c"),
    ("dwarkesh", "▶️ Watch: Satya Nadella on Dwarkesh Patel (focus first 5 min — rephrasing question into own framing)", "https://www.dwarkesh.com/p/satya-nadella-2"),
    ("sanna marin", "▶️ Watch: Ardern's response to the 'similar age' question (full ~1:30 — 2-second silence before the opening point)", "https://www.youtube.com/watch?v=yz9rg9m5dvU"),
    ("blackwell", "▶️ Watch: Jensen Huang GTC March 2024 keynote (focus 16:00–18:00, Blackwell reveal — bookended claim)", "https://www.youtube.com/watch?v=Y2F8yisiS6E"),
    ("minto pyramid", "▶️ Watch: Minto Pyramid Principle Explained with Examples (under 10 min, before/after rewrite)", "https://www.youtube.com/watch?v=j4Y3TdVVBCA"),
    ("pyramid principle explainer", "▶️ Watch: Minto Pyramid Principle Explained with Examples (under 10 min, before/after rewrite)", "https://www.youtube.com/watch?v=j4Y3TdVVBCA"),
    ("nvidia ai keynote", "▶️ Watch: Jensen Huang — NVIDIA AI Keynote", "https://www.youtube.com/watch?v=jpZ0dPsnIWw"),
    ("google i/o", "▶️ Watch: Sundar Pichai — Google I/O 2025 Keynote (focus 0:00–3:00, calm large-room pacing)", "https://www.youtube.com/watch?v=eIUqw3_YcCI"),
    # W9–W23 validated specific clips
    ("microsoft build opening", "▶️ Watch: Satya Nadella — Build 2020 opening (focus 0:30–2:30, headline-first pyramid)", "https://www.youtube.com/watch?v=S_wNRx7f7rU"),
    ("google i/o 2024", "▶️ Watch: Sundar Pichai — Google I/O 2024 opening (focus 0:00–2:00, single-sentence section leads)", "https://www.youtube.com/watch?v=uFroTufv6es"),
    ("king's fund interview", "▶️ Watch: Amy Edmondson — King's Fund on psychological safety (focus 0:30–2:30, one-line definition then stop)", "https://www.youtube.com/watch?v=eP6guvRt0U0"),
    ("nvidia's moat", "▶️ Watch: Jensen Huang on Dwarkesh — Will NVIDIA's moat persist? (focus 0:00–3:00, hold ground under challenge)", "https://www.youtube.com/watch?v=Hrbq66XqtCo"),
    ("hope, shame and infectious generosity", "▶️ Watch: Chris Anderson + Jon Ronson on Intelligence Squared (focus 5:00–10:00, master facilitator transitions)", "https://www.youtube.com/watch?v=zZNJIxRKEyI"),
    ("lockdown announcement press conference", "▶️ Watch: Ardern's NZ lockdown press conference (focus 15:00–20:00 Q&A, signal moving on without dismissing)", "https://www.youtube.com/watch?v=CAROtIqVgWk"),
    ("how microsoft thinks about agi", "▶️ Watch: Nadella on Dwarkesh — AGI strategy (focus 10:00–12:00, decisive falling-pitch closes)", "https://www.youtube.com/watch?v=8-boBsWcr5A"),
    ("ted's secret to great public speaking", "▶️ Watch: Chris Anderson — TED's secret to great public speaking (focus 0:00–5:00, open→frame→close arc)", "https://www.youtube.com/watch?v=-FOCpMAww28"),
    ("lex fridman", "▶️ Watch: Sundar Pichai on Lex Fridman #471 (focus 20:00–35:00, count fillers — silence, not 'uhh')", "https://www.youtube.com/watch?v=9V6tWC4CdFQ"),
    ("christchurch", "▶️ Watch: Ardern's Christchurch press conference (focus 0:00–3:00, falling pitch on every statement)", "https://www.youtube.com/watch?v=klL6Go-FC5Q"),
    ("gtc march 2025", "▶️ Watch: Jensen Huang — GTC March 2025 keynote (focus 5:00–8:00, repetition + gesture as non-native rhythm)", "https://www.youtube.com/watch?v=_waPvOwL9Z8"),
    ("cnbc's full interview with", "▶️ Watch: CNBC's full interview with Nadella (focus 8:00–10:00, reframing buys thinking time)", "https://www.youtube.com/watch?v=H7qQSbjT1E0"),
]

# Search the full next-week content (so weekend shadowing is included)
search_text = content_lower
for keyword, label, url in PODCASTS + APPS:
    if keyword in search_text and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

# YouTube — specific named clips (highest priority)
specific_clip_added = False
for keyword, label, url in SPECIFIC_CLIPS:
    if keyword in search_text and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)
        specific_clip_added = True

# YouTube — extract `Search "X" on YouTube` from weekend "How" text
for query in re.findall(r'[Ss]earch ["\']([^"\']+)["\'][^.]*?[Yy]ou[Tt]ube', next_content):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    if url not in seen_urls:
        resources.append(f'<a href="{url}">▶️ Search: "{query}" on YouTube</a>')
        seen_urls.add(url)

# YouTube — fallback to leader's best clip ONLY if no specific clip already matched.
# (When the schedule embeds a specific clip URL, the brief should not surface a different one.)
if not specific_clip_added:
    for keyword, label, url in SHADOW_BEST_CLIPS:
        if keyword in search_text and url not in seen_urls:
            resources.append(f'<a href="{url}">{label}</a>')
            seen_urls.add(url)

if 'vocabulary' in content_lower:
    resources.append(f'<a href="{REPO_BASE}/vocabulary/vocabulary_bank.md">📖 Vocabulary bank</a>')

resources_str = "\n".join(resources) if resources else "(see schedule for details)"

recap_section = (
    f"Plan hasn't started yet — Week 1 kicks off Monday! Get ready. 🚀"
    if current_num == 0
    else f"Focus: {this_focus}\nDays: {done_w} done / {partial_w} partial / {skipped_w} skipped"
)

msg = f"""<b>Weekly prep, Tomo! 📚</b>

<b>This week recap:</b>
{recap_section}

<b>Next week — {next_dates}:</b>
Focus: {next_focus}

<b>Tasks:</b>
{tasks_str}

<b>Resources:</b>
{resources_str}

<a href="{REPO_BASE}/plan/weekly_schedule.md">📅 Full schedule</a> | <a href="{REPO_BASE}/progress/progress_log.md">📊 Progress log</a>

Have a great weekend! 🎉"""

data = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data=data, headers={"Content-Type": "application/json"}
)
print(urllib.request.urlopen(req).read().decode())
