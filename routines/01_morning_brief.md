# Routine 1 — Daily morning brief

**Schedule:** Mon–Fri, 07:40 Australia/Melbourne
**Cron (enter in the Routines UI):** `40 7 * * 1-5`
**Repo attached:** `tomo2304/claude_code_playground`
**Connector required:** an email/notifications connector that can send to `t.yokote2304@gmail.com`

---

## Prompt to paste into the routine

You are sending the daily morning brief for Tomo's leadership communication learning plan.

Today's date is the current date in Australia/Melbourne. The plan started on 2026-04-20 and runs for 130 practice days (26 weeks × 5 days, Mon–Fri only).

Do the following in order:

1. Read `leader_speaking_learning/plan/weekly_schedule.md` and identify:
   - The current week number and phase name (dates on each week header tell you which week today falls in — each week starts on a Monday).
   - This week's focus theme (the bolded `**Focus: ...**` line under the current week).
   - Today's specific task. Weeks 1–2 use the `Home / Commute / Real-world challenge / Weekend shadowing` layout — pick the Home task as today's core. Weeks 3+ use per-day rows (Mon/Tue/Wed/Thu/Fri); pick today's row. If today is listed as a 30-min day, still pick the 15-min core action and treat the 30-min version as the stretch goal.

2. Read `leader_speaking_learning/progress/progress_log.md`. From the Layer 1 Daily Micro-Log table:
   - Count rows marked Done ✅ or Partial 〜 — call this X.
   - Check yesterday's row status: Done, Partial, Skipped, or missing.
   - Compute percent: round(X ÷ 130 × 100).

3. Apply the carry-forward rule for today's task:
   - If yesterday was Skipped or missing, today's task is the same one yesterday was meant to do.
   - If yesterday was Done or Partial, today's task is the next one in this week's schedule.

4. Send one push notification to `t.yokote2304@gmail.com` via the attached email/notifications connector. The message must be exactly these lines (no extras):

```
Good morning Tomo — <one-clause hook tied to today's focus>.
Core task (15 min): <specific actionable task from step 1, rewritten as an imperative sentence>.
Stretch (30 min): <the 30-min version of the same skill, or a stretch extension>.
Week <N> · <phase name> · Day <X> of 130 (<%>%)
```

Do not edit any files in the repo. Do not commit or push. Only read files and send the notification.
