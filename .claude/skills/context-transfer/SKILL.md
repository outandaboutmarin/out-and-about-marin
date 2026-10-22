---
name: context-transfer
description: Package everything important from the current conversation into one copy-and-paste text block, so a brand-new chat can continue the work with no other context. Use when the user says "context transfer", "hand off", "move this to a new chat", "summarize for a new thread", or the conversation is getting long.
---

# Context Transfer

You are an expert at context summary. Your sole job is to package all key information from this
conversation so the user can paste it into a new chat and continue without missing anything.

Write ONE single text block (one fenced code block, so it copies cleanly on a phone) with these
sections, in this order:

1. **Goals, task, key decisions and reasoning.** What we are trying to do, what was decided, and
   why. Include decisions the user made and options they turned down, so the new chat does not
   re-ask or re-propose them.
2. **Progress update.** Three lists: Finished / In progress / Not started.
3. **Every important file, link, name, figure or detail.** Full file paths, URLs, ids, dates,
   times, prices, people's names, commit hashes, account or tool names. Copy them exactly; never
   shorten a path or link.
4. **Where we left off and next steps.** The last thing the user asked, whether it was answered,
   and the concrete next step(s), in order.
5. **Any other key details.** Standing preferences and rules the user stated, open questions,
   assumptions still to confirm, things that went wrong and how they were fixed. Be as granular
   as needed.

Rules:
- The new chat must be able to continue seamlessly with nothing but this block. If something is
  only implied in the conversation, state it outright.
- Facts only. Do not invent details; if something is unknown, say "unknown" or "not yet confirmed".
- No commentary before or after the block beyond one short line saying it is ready to copy.
- Start the block with a one-line instruction to the new chat, e.g.
  "Context from a previous conversation. Read it all, then continue from 'Where we left off'."
