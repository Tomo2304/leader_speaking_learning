import os, re, json, urllib.request
from datetime import date, timedelta

REPO_BASE = "https://github.com/Tomo2304/leader_speaking_learning/blob/main"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

start = date(2026, 4, 24)
today = date.today()

with open("plan/weekly_schedule.md", encoding="utf-8") as f:
    schedule = f.read()
with open("progress/progress_log.md", encoding="utf-8") as f:
    progress = f.read()

week_headers = [(int(n), date.fromisoformat(d))
                for n, d in re.findall(r'### Week (\d+) \((\d{4}-\d{2}-\d{2})\)', schedule)]

current_num, current_start = 1, start
for num, wstart in week_headers:
    if wstart <= today:
        current_num, current_start = num, wstart

def get_week_content(num):
    pat = rf'### Week {num} \(\d{{4}}-\d{{2}}-\d{{2}}\)(.*?)(?=\n### Week |\Z)'
    m = re.search(pat, schedule, re.DOTALL)
    return m.group(1) if m else ""

this_content = get_week_content(current_num)
next_content = get_week_content(current_num + 1)

def get_focus(content):
    m = re.search(r'\*\*Focus: ([^\*\n]+)\*\*', content)
    return m.group(1).strip() if m else "Leadership communication"

this_focus = get_focus(this_content)
next_focus = get_focus(next_content)

# This week's progress stats from Layer 1
next_monday = current_start + timedelta(days=7)
done_w = partial_w = skipped_w = 0
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

# Next week dates
next_start = current_start + timedelta(days=7)
next_end = next_start + timedelta(days=4)
next_dates = f"{next_start.strftime('%a %d %b')} – {next_end.strftime('%a %d %b')}"

# Next week day-specific tasks
day_rows = re.findall(
    r'\|\s*(\*{0,2}(?:Mon|Tue|Wed|Thu|Fri)[^\|]*\*{0,2})\s*\|([^\|]+)\|([^\|]*)\|?([^\|]*)\|?',
    next_content, re.IGNORECASE
)
tasks_lines = []
for day, activity, how, time_col in day_rows:
    day_clean = day.strip('*').strip()
    act_clean = activity.strip()
    dur = "30 min" if ('⏱' in day or '30' in time_col) else "15 min"
    tasks_lines.append(f"• {day_clean} ({dur}): {act_clean}")
tasks_str = "\n".join(tasks_lines) if tasks_lines else f"Daily practice — {next_focus}"

# Resources for next week
resources = []
if 'vocabulary' in next_content.lower():
    resources.append(f'<a href="{REPO_BASE}/vocabulary/vocabulary_bank.md">📖 Vocabulary bank</a>')
externals = re.findall(r'\b(?:ELSA Speak|Orai|Think Fast[^,\n]*|Speak Up[^,\n]*|YouTube[^,\n]*)\b', next_content)
for ext in list(dict.fromkeys(externals))[:3]:
    resources.append(f'• {ext.strip()}')
resources_str = "\n".join(resources) if resources else "(see schedule for details)"

msg = f"""<b>Weekly prep, Tomo! 📚</b>

<b>This week recap:</b>
Focus: {this_focus}
Days: {done_w} done / {partial_w} partial / {skipped_w} skipped

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
