# Routine 2 — Daily evening check-in

**Schedule:** Mon–Fri, 21:30 Australia/Melbourne
**Cron (enter in the Routines UI):** `30 21 * * 1-5`
**Repo attached:** `tomo2304/claude_code_playground`
**Connector required:** an email/notifications connector that can send to `t.yokote2304@gmail.com`

---

## Prompt to paste into the routine

You are sending the daily evening check-in for Tomo's leadership communication learning plan.

Today's date is the current date in Australia/Melbourne. The plan runs Mon–Fri only.

Do the following in order:

1. Read `leader_speaking_learning/plan/weekly_schedule.md`. Identify tomorrow's planned 15-min core task. If tomorrow is a weekend day, treat the preview as "next Monday's task" instead. Remember the carry-forward rule: if Tomo replies Skipped to today, tomorrow carries today's task forward; if Done or Partial, tomorrow advances to the next scheduled task. Include both versions in the preview so the rule is visible.

2. Read `leader_speaking_learning/progress/progress_log.md` only to confirm the structure of the Layer 1 table — you are not logging anything in this routine. Logging happens in a separate conversation when Tomo replies.

3. Send push notification #1 to `t.yokote2304@gmail.com` via the attached connector.
   - Subject: `Evening check-in — <today's date, YYYY-MM-DD>`
   - Body, exactly three lines:

```
How did today go? Reply: Done / Partial / Skipped.
Plus one line about what happened — what you practised, what you noticed.
I'll log it when you reply and roll tomorrow's task accordingly.
```

4. Send push notification #2 (a separate message) to the same address.
   - Subject: `Tomorrow — <tomorrow's date, YYYY-MM-DD>`
   - Body, exactly three lines:

```
If today was Done or Partial → tomorrow's task: <next scheduled 15-min core task>.
If today was Skipped → tomorrow carries forward: <today's task>.
Default plan: 15 min. (Stretch to 30 min only on Tue/Wed/Thu and max 2×/week.)
```

Do not edit any files in the repo. Do not commit or push. Only read files and send the two notifications.
