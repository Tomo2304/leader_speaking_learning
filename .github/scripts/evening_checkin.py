import os, re, json, urllib.request
from datetime import date, timedelta

REPO_BASE = "https://github.com/Tomo2304/leader_speaking_learning/blob/main"
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

start = date(2026, 4, 27)
today = date.today()
day_num = sum(1 for i in range((today - start).days + 1)
             if (start + timedelta(days=i)).weekday() < 5)
weekday = today.strftime("%A")
date_display = today.strftime("%d %B")

tomorrow = today + timedelta(days=1)
while tomorrow.weekday() >= 5:
    tomorrow += timedelta(days=1)
tomorrow_day_num = day_num + 1

with open("plan/weekly_schedule.md", encoding="utf-8") as f:
    schedule = f.read()

week_headers = [(int(n), date.fromisoformat(d))
                for n, d in re.findall(r'### Week (\d+) \((\d{4}-\d{2}-\d{2})\)', schedule)]

def get_week_content(target):
    num, wstart = 1, start
    for n, ws in week_headers:
        if ws <= target:
            num, wstart = n, ws
    pat = rf'### Week {num} \(\d{{4}}-\d{{2}}-\d{{2}}\)(.*?)(?=\n### Week |\Z)'
    m = re.search(pat, schedule, re.DOTALL)
    return m.group(1) if m else ""

def get_task(target, week_content):
    day_abbr = target.strftime("%A")[:3]
    day_m = re.search(
        rf'\|\s*\*{{0,2}}{day_abbr}[^\|]{{0,15}}\*{{0,2}}\s*\|([^\|]+)\|([^\|]*)\|?([^\|]*)\|?',
        week_content, re.IGNORECASE
    )
    if day_m:
        activity = day_m.group(1).strip().strip('*')
        duration = "30" if ('⏱' in day_m.group(0) or '30' in day_m.group(3)) else "15"
        return activity, duration
    home_m = re.search(r'\|\s*\*?\*?Home\*?\*?\s*\|([^\|]+)\|', week_content, re.IGNORECASE)
    if home_m:
        return home_m.group(1).strip(), "15"
    focus_m = re.search(r'\*\*Focus: ([^\*\n]+)\*\*', week_content)
    return (focus_m.group(1).strip() if focus_m else "Practice today's focus"), "15"

today_task, _ = get_task(today, get_week_content(today))
tomorrow_task, tomorrow_dur = get_task(tomorrow, get_week_content(tomorrow))

msg = f"""<b>Evening check-in, Tomo! 🌙</b>

Day {day_num} / 130 | {weekday} {date_display}

<b>Today's task:</b> {today_task}
How did it go? Open Claude and tell me:
<i>"Day {day_num} done"</i> / <i>"Day {day_num} partial"</i> / <i>"Day {day_num} skipped"</i>

<b>Tomorrow — Day {tomorrow_day_num}:</b> {tomorrow_task} ({tomorrow_dur} min)
Set aside your {tomorrow_dur} minutes before the day starts.

<a href="{REPO_BASE}/progress/progress_log.md">📊 Progress log</a> | <a href="{REPO_BASE}/plan/weekly_schedule.md">📅 Schedule</a>"""

data = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
req = urllib.request.Request(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data=data, headers={"Content-Type": "application/json"}
)
print(urllib.request.urlopen(req).read().decode())
