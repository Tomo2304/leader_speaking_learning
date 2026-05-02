import os, re, json, urllib.request, urllib.parse
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

REPO_BASE = "https://github.com/Tomo2304/leader_speaking_learning/blob/main"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MELBOURNE = ZoneInfo("Australia/Melbourne")
now_mel = datetime.now(MELBOURNE)
# Two crons (AEST + AEDT) both fire daily; only one matches Melbourne 7am.
# Skip silently if scheduled run is off-target. Manual runs always proceed.
if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and now_mel.hour != 7:
    raise SystemExit(0)
start = date(2026, 4, 27)
today = now_mel.date()
day_num = sum(1 for i in range((today - start).days + 1)
             if (start + timedelta(days=i)).weekday() < 5)
weekday = today.strftime("%A")
date_display = today.strftime("%d %B")

with open("plan/weekly_schedule.md", encoding="utf-8") as f:
    schedule = f.read()
with open("progress/progress_log.md", encoding="utf-8") as f:
    progress = f.read()

# Progress stats
done_m = re.search(r'Days completed[^\|]*\|\s*(\d+)', progress)
skip_m = re.search(r'Days skipped[^\|]*\|\s*(\d+)', progress)
done_count = done_m.group(1) if done_m else "0"
skipped_count = skip_m.group(1) if skip_m else "0"

# Find current week
week_headers = [(int(n), date.fromisoformat(d))
                for n, d in re.findall(r'### Week (\d+) \((\d{4}-\d{2}-\d{2})\)', schedule)]
current_num, current_start = 1, start
for num, wstart in week_headers:
    if wstart <= today:
        current_num, current_start = num, wstart

# Extract week section
week_pat = rf'### Week {current_num} \(\d{{4}}-\d{{2}}-\d{{2}}\)(.*?)(?=\n### Week |\Z)'
week_m = re.search(week_pat, schedule, re.DOTALL)
week_content = week_m.group(1) if week_m else ""

# Focus
focus_m = re.search(r'\*\*Focus: ([^\*\n]+)\*\*', week_content)
focus = focus_m.group(1).strip() if focus_m else "Leadership communication"

# Phase (find the most recent phase heading before this week)
week_pos = schedule.find(f'### Week {current_num}')
phase_m = re.search(r'## (Phase \d+[^\n]+)', schedule[:week_pos])
phase = re.sub(r'\s*\(Weeks[^\)]+\)', '', phase_m.group(1)).strip() if phase_m else "Phase 1 – Foundation"

is_weekend = today.weekday() >= 5  # Sat or Sun

# Today's task - look for day-specific row first
if is_weekend:
    day_m = re.search(
        r'\|\s*\*{0,2}Weekend[^\|]*\*{0,2}\s*\|([^\|]+)\|([^\|]*)\|',
        week_content, re.IGNORECASE
    )
else:
    day_abbr = weekday[:3]
    day_m = re.search(
        rf'\|\s*\*{{0,2}}{day_abbr}[^\|]{{0,15}}\*{{0,2}}\s*\|([^\|]+)\|([^\|]*)\|?([^\|]*)\|?',
        week_content, re.IGNORECASE
    )
if day_m:
    activity = day_m.group(1).strip().strip('*')
    how = day_m.group(2).strip()
    if is_weekend:
        duration = "20–30"
    else:
        duration = "30" if ('⏱' in day_m.group(0) or '30' in day_m.group(3)) else "15"
    task = activity + (f"\n{how}" if how else "")
else:
    home_m = re.search(r'\|\s*\*?\*?Home\*?\*?\s*\|([^\|]+)\|([^\|]*)\|', week_content, re.IGNORECASE)
    if home_m:
        task = home_m.group(1).strip()
        how = home_m.group(2).strip()
        if how:
            task += f"\n{how}"
    else:
        task = f"Practise this week's focus: {focus}"
    duration = "20–30" if is_weekend else "15"

# Resources — auto-attach links for resources mentioned in today's task
resources = []
task_lower = task.lower() if isinstance(task, str) else ""

# Podcasts (Apple Podcasts — preferred)
PODCASTS = [
    ("speak up", "🎙 Speak Up (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/speak-up-develop-your-executive-presence-leadership/id1368646965"),
    ("think fast, talk smart", "🎙 Think Fast, Talk Smart (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/think-fast-talk-smart-communication-techniques/id1494989268"),
    ("think fast talk smart", "🎙 Think Fast, Talk Smart (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/think-fast-talk-smart-communication-techniques/id1494989268"),
    ("the knowledge project", "🎙 The Knowledge Project (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/the-knowledge-project/id990149481"),
    ("masters of scale", "🎙 Masters of Scale (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/masters-of-scale/id1227971746"),
    ("hbr ideacast", "🎙 HBR IdeaCast (Apple Podcasts)", "https://podcasts.apple.com/us/podcast/hbr-ideacast/id152022135"),
]

# Apps (App Store — iOS preferred)
APPS = [
    ("elsa speak", "📱 ELSA Speak (App Store)", "https://apps.apple.com/us/app/elsa-speak-english-learning/id1083804886"),
    ("orai", "📱 Orai (App Store)", "https://apps.apple.com/us/app/orai-improve-public-speaking/id1203178170"),
]

# Shadow targets — best clip from resources.md (specific video) for each leader
SHADOW_BEST_CLIPS = [
    ("satya nadella", "▶️ Watch: Satya Nadella — WEF 2026 Interview", "https://www.youtube.com/watch?v=1co3zt3-r7I"),
    ("jensen huang", "▶️ Watch: Jensen Huang — Leadership lessons", "https://www.youtube.com/watch?v=ziL09IyS0cw"),
    ("sundar pichai", "▶️ Watch: Sundar Pichai — Google I/O 2025 Keynote", "https://www.youtube.com/watch?v=eIUqw3_YcCI"),
    ("simon sinek", "▶️ Watch: Simon Sinek — Start With Why", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("jacinda ardern", "▶️ Watch: Jacinda Ardern — On Leadership", "https://www.youtube.com/watch?v=iza9O91E4tk"),
    ("amy edmondson", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
]

# Specific clip overrides — when the task mentions a particular talk by name
SPECIFIC_CLIPS = [
    ("why good leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("why leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("start with why", "▶️ Watch: Simon Sinek — Start With Why TED Talk", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("psychological safety", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
    ("nvidia ai keynote", "▶️ Watch: Jensen Huang — NVIDIA AI Keynote", "https://www.youtube.com/watch?v=jpZ0dPsnIWw"),
    ("google i/o", "▶️ Watch: Sundar Pichai — Google I/O 2025 Keynote", "https://www.youtube.com/watch?v=eIUqw3_YcCI"),
]

def youtube_search_url(query):
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)

# Question bank
if 'question_bank' in task_lower or 'question bank' in task_lower:
    resources.append(f'<a href="{REPO_BASE}/plan/question_bank.md">❓ Question bank</a>')

# Match podcasts / apps — dedupe by URL
seen_urls = set()
for keyword, label, url in PODCASTS + APPS:
    if keyword in task_lower and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

# YouTube — specific named clips first (highest priority match)
for keyword, label, url in SPECIFIC_CLIPS:
    if keyword in task_lower and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

# YouTube — extract `Search "X" on YouTube` patterns from task text
for query in re.findall(r'[Ss]earch ["\']([^"\']+)["\'][^.]*?[Yy]ou[Tt]ube', task):
    url = youtube_search_url(query)
    if url not in seen_urls:
        resources.append(f'<a href="{url}">▶️ Search: "{query}" on YouTube</a>')
        seen_urls.add(url)

# YouTube — fallback to leader's best clip if their name appears
for keyword, label, url in SHADOW_BEST_CLIPS:
    if keyword in task_lower and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)

if 'vocabulary' in week_content.lower():
    resources.append(f'<a href="{REPO_BASE}/vocabulary/vocabulary_bank.md">📖 Vocabulary bank</a>')
resources.append(f'<a href="{REPO_BASE}/plan/weekly_schedule.md">📅 This week\'s schedule</a>')
resources_str = "\n".join(resources)

# Motivational sentence (rotates daily)
motivations = [
    "Jensen Huang left Taiwan at age 9 and built NVIDIA into a trillion-dollar company — clarity of thought, not accent, commands a room.",
    "Satya Nadella grew up in Hyderabad learning English as a second language; today he is one of tech's most respected communicators.",
    "Sundar Pichai moved from Chennai to the US at 22 — within two decades he became CEO of Google by communicating with precision and calm.",
    "The goal isn't perfect English — it's clear thinking expressed with confidence.",
    "Every great communicator was once an average one who kept practising daily.",
    "Jensen Huang: 'I would rather be too direct than too vague.' Directness is a learnable skill.",
    "Non-native speakers often communicate more carefully than native speakers — that precision is your strength.",
]
motivation = motivations[today.toordinal() % len(motivations)]

day_header = f"🎬 Weekend session | {weekday} {date_display}" if is_weekend else f"Day {day_num} / 130 | {weekday} {date_display}"

msg = f"""<b>Good morning, Tomo! 🌅</b>

{day_header}

<i>{motivation}</i>

<b>Today's task:</b>
{task}

⏱ {duration} min | {phase} | Focus: {focus}

<b>Resources:</b>
{resources_str}

Progress: {done_count} done, {skipped_count} skipped so far."""

data = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data=data, headers={"Content-Type": "application/json"}
)
print(urllib.request.urlopen(req).read().decode())
