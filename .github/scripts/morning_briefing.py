import os, re, json, glob, urllib.request, urllib.parse
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

# Specific clip overrides — when the task mentions a particular talk by name.
# Match the inline links in plan/weekly_schedule.md so the brief never surfaces a different URL.
SPECIFIC_CLIPS = [
    ("why good leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe (focus 5:30–8:30, the Swenson story — match his pauses)", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("why leaders make you feel safe", "▶️ Watch: Simon Sinek — Why Leaders Make You Feel Safe (focus 5:30–8:30, the Swenson story — match his pauses)", "https://www.youtube.com/watch?v=lmyZMtPVodo"),
    ("start with why", "▶️ Watch: Simon Sinek — Start With Why TED Talk", "https://www.youtube.com/watch?v=u4ZoJKF_VuA"),
    ("psychological safety", "▶️ Watch: Amy Edmondson — Psychological Safety TED Talk (focus 4:30–7:30, three-things signposting)", "https://www.youtube.com/watch?v=LhoLuui9gX8"),
    ("the circuit", "▶️ Watch: Sundar Pichai on The Circuit with Emily Chang (focus 12:00–15:00 — micro-pause + framing sentence)", "https://www.youtube.com/watch?v=5puu3kN9l7c"),
    ("dwarkesh", "▶️ Watch: Satya Nadella on Dwarkesh Patel (focus first 5 min — rephrasing the question into his own framing)", "https://www.dwarkesh.com/p/satya-nadella-2"),
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
specific_clip_added = False
for keyword, label, url in SPECIFIC_CLIPS:
    if keyword in task_lower and url not in seen_urls:
        resources.append(f'<a href="{url}">{label}</a>')
        seen_urls.add(url)
        specific_clip_added = True

# YouTube — extract `Search "X" on YouTube` patterns from task text
for query in re.findall(r'[Ss]earch ["\']([^"\']+)["\'][^.]*?[Yy]ou[Tt]ube', task):
    url = youtube_search_url(query)
    if url not in seen_urls:
        resources.append(f'<a href="{url}">▶️ Search: "{query}" on YouTube</a>')
        seen_urls.add(url)

# YouTube — fallback to leader's best clip ONLY if no specific clip already matched.
# (When the schedule embeds a specific clip URL, the brief should not surface a different one.)
if not specific_clip_added:
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

# Vocab targets reminder (Mon–Fri only). Monday = pick; Tue–Fri = use, with link to week file.
vocab_line = ""
if not is_weekend:
    if weekday == "Monday":
        vocab_line = (
            f'\n🎯 <b>Vocab targets:</b> Pick 3 phrases from '
            f'<a href="{REPO_BASE}/vocabulary/vocabulary_bank.md">vocabulary_bank.md</a> '
            f"to use this week — add them to this week's review file.\n"
        )
    else:
        review_matches = sorted(glob.glob(f"progress/weekly_reviews/week_{current_num:02d}_*.md"))
        if review_matches:
            review_path = review_matches[0].replace("\\", "/")
            vocab_line = (
                f'\n🎯 <b>Vocab targets:</b> Use your 3 vocab targets from '
                f'<a href="{REPO_BASE}/{review_path}">this week\'s review file</a> '
                f"today — even one out loud counts.\n"
            )

day_header = f"🎬 Weekend session | {weekday} {date_display}" if is_weekend else f"Day {day_num} / 130 | {weekday} {date_display}"

msg = f"""<b>Good morning, Tomo! 🌅</b>

{day_header}

<i>{motivation}</i>

<b>Today's task:</b>
{task}

⏱ {duration} min | {phase} | Focus: {focus}

<b>Resources:</b>
{resources_str}
{vocab_line}
Progress: {done_count} done, {skipped_count} skipped so far."""

data = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data=data, headers={"Content-Type": "application/json"}
)
print(urllib.request.urlopen(req).read().decode())
