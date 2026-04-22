# Routine 3 — Saturday evening weekly resource prep

**Schedule:** Saturdays, 21:00 Australia/Melbourne
**Cron (enter in the Routines UI):** `0 21 * * 6`
**Repo attached:** `tomo2304/claude_code_playground`
**Connector required:** an email/notifications connector that can send to `t.yokote2304@gmail.com`

---

## Prompt to paste into the routine

You are preparing the weekly resource brief for Tomo's leadership communication learning plan. Run time: every Saturday 21:00 Australia/Melbourne — i.e. at the end of the current practice week, previewing the week that starts Monday.

Do the following in order:

1. Read `leader_speaking_learning/plan/weekly_schedule.md`. Identify NEXT week's row (the week whose date header is the upcoming Monday) and extract:
   - Next week's number — call it N+1.
   - Its focus theme (the bolded `**Focus: ...**` line).
   - Every activity that references external material: a book or book chapter, an app, a podcast episode, a YouTube clip or search term, a shadowing target (e.g. a specific leader or talk). Also note any scheduled 30-min day.

2. Read `leader_speaking_learning/resources/resources.md`. For each external-material activity from step 1, match it to a specific item in the resource library (book title + author + likely page/chapter range, app name + where it's used, podcast name + episode if known, YouTube search term or channel). Prefer items marked "Start here" or "High" priority when the plan is ambiguous.

3. Read this week's weekly review file inside `leader_speaking_learning/progress/weekly_reviews/`. The file to read is the one numbered with the week that is just ending — e.g. if next week is Week 4, read `week_03_*.md`. Pull 2–3 bullets summarising what was practised and any pattern worth carrying into next week.

4. Send one push notification to `t.yokote2304@gmail.com` via the attached connector.
   - Subject: `Week <N+1> prep — <next week's focus theme>`
   - Body, in this exact structure:

```
Theme next week: <focus theme>.

Prepare:
- <resource type>: <specific item, with page/chapter/episode/URL or search term>
- <resource type>: <specific item, ...>
- <resource type>: <specific item, ...>   (2–4 bullets total; only include what's actually needed)

Bring: <phone, notebook, headphones, etc. — or "nothing extra" if none>.
Estimated prep time: <N> min (hard cap 15).

This week's recap:
- <bullet 1>
- <bullet 2>
- <bullet 3>   (3rd bullet optional)
```

Do not edit any files in the repo. Do not commit or push. Only read files and send the notification.
