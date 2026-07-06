# How I Prompt Fable — A Working Guide

Distilled from Matt Shumer's *"How I Prompt Fable"* (July 3, 2026). It's the
same model everyone has. Results look different not because of secret, elaborate
prompts, but because of *how* the model is used. Prompt a next-generation model
the way you prompt the current ones and you get current-generation results.
Change how you prompt it — and how you think about what it can take on — and the
door opens.

This guide is meant to be reusable. Hand it to your model along with your task
and let it help you write the prompt.

---

## The core shift

Stop spooling out the *how*. Hand over a goal, fence it with rules it can't
cross, give it a hard bar for "done," and loop it against that bar until it gets
there. Everything below is that idea, broken into the parts you can actually put
in a prompt.

---

## 1. Give it the goal, not the steps

**Takeaway:** Describe the outcome you want, not the procedure to get there.

**Why it works:** With older models you had to specify each step or they'd
wander. This is the opposite — the more room you give it, the better it does.
It's often better at figuring out the "how" than you are. Every step you dictate
is you overriding its judgment with yours, and yours is usually worse.

**What to do:** Hand it big, sweeping, underspecified work — the way you'd hand a
goal to a brilliant person you trust and let them find the best path. This feels
risky when you're used to controlling the details. What makes it safe is the next
two sections.

---

## 2. Set house rules so you can trust it

**Takeaway:** An underspecified goal is safe when you fence it with a few rules
it can't cross.

**Why it works:** House rules are the handful of things you always want to be
true, no matter how the model reaches the goal. They let you run wide open on the
goal without worrying it'll ship something that breaks what you care about.

**What to do:** State your standing rules explicitly. A recurring one: models love
to over-engineer — they'll reach for a regex filter to catch one specific case
when what you actually want is a prompt that *describes* the behavior and lets the
model reason. So: *don't hard-code special cases; describe the behavior in the
agent's system prompt and let the agent handle it.*

For extra protection, give a sub-agent one job: **check the work against the house
rules before anything is pushed.**

```
House rules (never violate, however you reach the goal):
- Don't hard-code special cases. Describe the desired behavior in prose/system
  prompt and let the model reason about it.
- <your rule>
- <your rule>

Before pushing anything, spin up a separate sub-agent whose only job is to check
the output against these house rules. If it fails any of them, do not push.
```

---

## 3. Give it a real bar for "done"

**Takeaway:** Don't use adjectives. Give it a hard, checkable bar — and make it
hard.

**Why it works:** Tell it to make something "high quality" and it stops at *its*
idea of good enough, which is usually lower than yours. A concrete bar removes
the ambiguity it would otherwise resolve in its own favor.

**What to do:** Write a test it can check itself against — something concrete like
*"a stranger can't tell our render from the real photo."* If you don't know how to
measure the thing you want, hand *that* problem to the model too.

> A friend cloning a component library was stuck for two reasons. First, he was
> building on top of ShadCN and trying to clone ShadCN's components — so the model
> was fighting ShadCN's conventions instead of just building. Second, he had no
> way to say when it was done; he was only saying "clone this." The fix: throw out
> ShadCN and start from scratch (a component library is completely buildable from
> nothing, and the existing code was just baggage), then ask the model to invent
> the measure of "done." It took a screen recording of the real components in use,
> turned it into a heat map of where everything moved, and worked until its version
> matched. Nobody told it *how* — just what "done" meant.

**The rule you never break:** *Whatever builds something never gets to grade it.*
The build agent is biased — it carries a whole trajectory of "why I made these
decisions" it can use to justify that it's finished. Always spin up a **separate
sub-agent with a fresh context window**, point it at the *real* output (the actual
pixels, the actual running app), and have it try to **prove the thing is not
passing.**

```
Definition of done (the bar):
- <concrete, checkable test — e.g. "a stranger can't tell our render from the
  real photo">

If you can't measure this yet, first design the measuring stick, then build to it.

Grading rule: the agent that builds this does NOT grade it. When you think you're
done, spawn a separate sub-agent with a fresh context window, point it at the real
output, and have it try to PROVE the work is not passing. Only stop when that
adversarial check can't break it.
```

---

## 4. Loop it until it hits the bar

**Takeaway:** Once there's a bar, put the model on a loop against it and let it
run. It never gets to decide it's finished.

**Why it works:** The loop builds, checks itself, finds the biggest gap, closes
it, and goes again — for hours, sometimes days. There's always a next gap. It
stops when you say so, or when it genuinely can't find anything left to fix (rare,
if you've set this up right). This is especially strong on creative work, where
there's always something concrete to keep measuring against.

**What to do:** Use `/loop`. Keep the bar in front of it every iteration.

**One trick for long runs:** have it build a small HTML status page, deploy it
somewhere, and keep updating it as it works — screenshots, notes, whatever shows
where things stand. Then you can glance at your phone and see progress without
touching anything.

```
Loop against the bar above. Each pass: measure against the bar, find the single
biggest gap, close it, repeat. You do not get to declare yourself done — keep
going until the bar is met or you truly cannot find another gap.

Keep a live status page: build a small HTML page, deploy it, and update it each
pass with screenshots and notes so I can check progress from my phone.
```

---

## 5. Let it build on what you've already done

**Takeaway:** Your old work is fuel for the new work. The model gets better at
something the more of it you've already done.

**Why it works:** The first hard thing takes real effort to get right — the first
build (a photorealistic 3D forest) needed the most carefully written prompt,
because there was no reference point for the quality wanted. But once one great
result exists, everything after it gets easier: point the model at the prior work
as both the code to reuse *and* the quality bar to beat.

**What to do:** Reference prior work directly — *"here's the code, here's the
quality bar, match this and go beyond it."* It goes further than reusing code: the
model can read the **traces of your old sessions** — what it actually tried, what
worked and what didn't. So instead of dictating an approach ("use a separate
sub-agent for each object in the scene"), you can say *"read the forest traces and
learn what worked"* and it picks up the approach on its own. (The Hogwarts demo
came together far faster than the forest, mostly because of this.)

```
Build on prior work: here is <path to previous result>. Use it as the code to
reuse and as the quality bar — match it and go beyond it. Also read the traces of
that session and learn what worked and what didn't; carry the good approaches
forward. Don't make me re-explain any of it.
```

---

## 6. Get out of its way

**Takeaway:** Every time it has to stop and ask you something, you lose time.
Clear the obstacles up front.

**Why it works:** Autonomy up front means it makes its own calls instead of
blocking on you. The main exception is planning — and only for huge,
consequential builds.

**What to do:** Hand it a budget instead of approving each spend. Tell it where
keys and credentials live. Tell it, in writing, to make its own calls and only
come back if it's truly blocked or hits something only you can decide.

```
Autonomy: make your own decisions and keep moving. Only come back to me if you're
truly blocked or the decision is one only I can make.
- Budget: you may spend up to <amount> on <service> without asking.
- Credentials: keys live at <location>.
- Don't ask permission for reversible actions inside the goal and house rules.
```

**The exception — plan first, but only for big, consequential builds:**

```
This is a large, consequential build. Before writing any code, produce a plan and
ask me everything you're unsure about up front. Once we settle the plan, run to
completion without stopping.
```

---

## Two ways to run it

The principles above are the same whether you're shipping features or building a
world. What changes is the setup around them.

### Engineering — run a team

Several sessions working at once, pulling tasks from a list, a board, or handed
out directly. Each does its task, triple-checks its own work with sub-agents
(remember: builder ≠ grader), and opens a PR with the evidence. Then **one more
session does nothing but integrate**: it merges the PRs, runs everything, tests
like a real user, and keeps the whole thing green. When two features overlap, tell
one session to watch the other's traces as it's built and stay compatible — they
work in parallel, one keeping an eye on the other and integrating as it lands.

### Creative — momentum and detail

Same loop, same hard bar, but **fan out sub-agents to nail individual pieces**
instead of making one session do all of it — e.g. a separate sub-agent perfecting
each kind of tree in a forest. Sometimes run a few completely separate attempts at
once, keep the best one, and carry what worked into the next round.

Mix these however you want; it depends on what you're building.

---

## When to spend on ultracode

There's a heavier mode called **ultracode** that costs a lot more. Use it rarely —
a good loop with an ambitious enough goal usually gets you there without it.

Where it earns its cost is **foundations**: a new system you'll be building on for
months — the core of a business or a codebase. There you want the base right from
day one. It's the same reason for throwing out ShadCN: a good foundation makes
everything on top of it easier, and a bad one makes everything harder forever. For
that kind of work — and pretty much only that kind — the extra cost is worth it.

---

## The whole thing in one breath

Don't spoon-feed it. Hold it to a bar it can't talk its way out of. Let it build
on everything it's already made.

1. **Goal, not steps** — hand over the outcome, not the procedure.
2. **House rules** — a few lines it can never cross; have a sub-agent enforce them.
3. **A hard bar for done** — concrete and checkable; if you can't measure it, have
   it invent the measure.
4. **Builder ≠ grader** — a fresh-context sub-agent grades the real output and
   tries to prove it's *not* done.
5. **Loop to the bar** — it never declares itself finished; keep a live status
   page for long runs.
6. **Build on prior work** — reuse the code, the bar, and the session traces.
7. **Get out of its way** — budget, credentials, autonomy up front; plan first
   only for the big, consequential builds.

If this is a lot to hold in your head, you don't have to: hand this guide to your
model along with your task and tell it to help you write your prompts from here on.
