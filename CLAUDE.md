# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Project Is

A structured 6-month self-directed leadership communication learning plan for Tomo — a Japanese-born Technical Data Analytics Lead based in Melbourne. Start date: 2026-04-20. Target: 2026-10-19. 130 learning days total (26 weeks × 5 weekdays).

**Core goal:** Communicate like a confident, capable native English-speaking leader — especially in the AI Steering Committee, executive meetings, and unprepared moments.

**Key habits being built:**
- Conclusion first (BLUF / Pyramid Principle) — breaking the Japanese bottom-up pattern
- PREP framework for spontaneous responses (Point → Reason → Example → Point)
- Executive-level brevity and meeting facilitation
- Deliberate delivery: pace, pause, intonation

---

## File Structure

```
overview.md                        — 9 tasks, milestones, key deliverables index
plan/
  weekly_schedule.md               — 26-week daily schedule (the primary operational file)
  task_breakdown.md                — Skills, knowledge, and how Claude helps per task
resources/
  resources.md                     — Books, apps, podcasts, YouTube, shadowing targets
vocabulary/
  vocabulary_bank.md               — Leadership phrases; auto-updated during reviews
progress/
  progress_log.md                  — 3-layer monitoring: daily log, weekly check-in, monthly milestones
  weekly_reviews/
    week_NN_[topic].md             — One file per week (23 files); stores examples and vocabulary additions
```

---

## How Claude Assists in This Project

### During communication reviews
Whenever Tomo shares a sentence, email, spoken response, or any wording for review — automatically add worthwhile improvements to **both**:
1. `vocabulary/vocabulary_bank.md` — "Entries Added from Reviews" table
2. The current week's file in `progress/weekly_reviews/` — "Examples from Practice" table and "Vocabulary Additions" table

Format: `| Date | Original phrasing | Improved phrasing | Why it's stronger |`

To find the correct week file: count weeks from 2026-04-20 (Week 1 = 2026-04-20 to 2026-04-25).

### PREP mock sessions
When Tomo says "run a PREP mock session" — ask 5 unexpected senior-leader-style questions one at a time. After each response, give structured feedback: what the Point was, whether the structure held, and one specific improvement.

### Meeting facilitation roleplays
When Tomo says "run a meeting facilitation roleplay" — play a realistic participant (rambling, going off-topic, or challenging). Let Tomo practise redirecting and closing. Debrief after.

### Weekly check-ins
When Tomo reports a week's activity, assess against the milestone targets in `overview.md`, suggest one focus for the coming week, and update the Layer 2 section of `progress/progress_log.md`.

---

## Scheduling Rules for Daily Tasks

- Default task time: **15 min**
- 30-min tasks: **maximum 2 per week**, **Tuesday / Wednesday / Thursday only**
- Monday and Friday: **always 15 min**

These constraints are already built into `plan/weekly_schedule.md`. Do not suggest 30-min tasks on Mon or Fri.

---

## Key Resources (for context)

- **Books (start here):** *The Pyramid Principle* (Minto), *Exactly What to Say* (Jones), *Think Faster, Talk Smarter* (Abrahams 2023)
- **Apps (start here):** Orai (filler words/pace), ELSA Speak (pronunciation — trained on Japanese-speaker patterns)
- **Podcast (start here):** *Think Fast, Talk Smart* (Stanford GSB) — directly covers spontaneous speaking under pressure
- **Primary shadowing targets:** Satya Nadella, Jensen Huang (most relevant — AI/data, non-native speaker), Sundar Pichai, Simon Sinek, Jacinda Ardern, Amy Edmondson

---

## Automated Agents (Scheduled)

Three remote agents are configured to run on schedule (times in Melbourne AEST/AEDT):
- **7:40am Mon–Fri** — sends today's specific learning task and progress counter (X/130 days)
- **9:30pm Mon–Fri** — evening check-in; asks for Done/Partial/Skipped; previews tomorrow's task
- **9:00pm Saturday** — weekly resource prep notification; includes next week's theme, resources to prepare, and this week's recap

These agents read `plan/weekly_schedule.md` and `progress/progress_log.md` from the GitHub repo. Progress updates written by these agents must also be reflected in the local copy.
