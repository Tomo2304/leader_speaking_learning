import os, re, json, urllib.request, urllib.parse
from datetime import date, timedelta

REPO_BASE = "https://github.com/Tomo2304/leader_speaking_learning/blob/main"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

start = date(2026, 4, 25)  # first Saturday
today = date.today()

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
SPECIFIC_CLIPS = [
    ("why good leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("why leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("start with why", "▶️ Watch: Simon Sinek — Start With Why TED Talk", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("psychological safety", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
    ("nvidia ai keynote", "▶️ Watch: Jensen Huang — NVIDIA AI Keynote", "https://www.youtube.com/watch?v=jpZ0dPsnIWw"),
    ("google i/o", "▶️ Watch: Sundar Pichai — Google I/O 2025 Keynote", "https://www.youtube.com/watch?v=eIUqw3_YcCI"),
]

# Search the full next-week content (so weekend shadowing is included)
search_text = content_lower
for keyword, label, url in PODCASTS + APPS:
    if keyword in search_text and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

# YouTube — specific named clips
for keyword, label, url in SPECIFIC_CLIPS:
    if keyword in search_text and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

# YouTube — extract `Search "X" on YouTube` from weekend "How" text
for query in re.findall(r'[Ss]earch ["\']([^"\']+)["\'][^.]*?[Yy]ou[Tt]ube', next_content):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    if url not in seen_urls:
        resources.append(f'<a href="{url}">▶️ Search: "{query}" on YouTube</a>')
        seen_urls.add(url)

# YouTube — fallback to leader's best clip
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
