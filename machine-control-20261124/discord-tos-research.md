# Discord ToS research: message-control CLI risk note

Worker 2 (ToS research) for the Discord message-control CLI.
All sources below were read directly on 2026-11-24. This is a plain-language
reading of Discord's published terms, not legal advice. Discord can change
these pages at any time, so re-check them before the CLI ships or is used
on any account that matters.

Research log (Asia/Ho_Chi_Minh): started 2026-11-24 20:27, sources read
20:27-20:28, file written 2026-11-24 20:29. Elapsed about 2 minutes.

## Verdict in short

- Driving the user's own user account with a script is prohibited by
  Discord, whichever mechanism does the driving. The rule turns on the
  account being automated, not on the tool used.
- The user-token REST route is the clearest violation: Discord calls it
  self-botting and says it "can result in an account termination if found".
- The CDP/GUI-automation route (driving the official desktop client) is
  NOT named anywhere in Discord's terms. No clause mentions CDP, the
  DevTools protocol, GUI automation, RPA, or scripted mouse and keyboard.
  The nearest published lines are the self-bot rule (automating a normal
  user account, mechanism not specified) and the Platform Manipulation
  explainer line against modifying the client "including automating
  account actions". The honest position is: probably treated as
  self-botting if detected, but Discord has not published a position on
  GUI automation specifically. Do not present the CDP route as safe or
  compliant.
- The only sanctioned automation path is a proper bot account with a bot
  token, invited to servers. It cannot read the owner's DMs or act as
  the owner, so it does not cover the same use cases.

## 1. What Discord prohibits (quoted, with sources)

### 1a. Terms of Service

Source: https://discord.com/terms
Version read: effective December 15, 2026, last updated November 23, 2026.
Accessed: 2026-11-24.

Section "Restrictions on your use of Discord's services":

- "Fundamentally, do not do, try to do, or encourage or help others to do
  any of the following:"
- "Don't use the services to do harm to yourself or others. Among other
  things, this includes ... spamming, auto-messaging, or auto-dialing
  people through our services"
- "Don't use the services to do harm to Discord. Among other things, this
  includes ... scraping our services without our written consent,
  including by using any robot, spider, crawler, scraper, or other
  automatic device, process, or software; ... using any unauthorized
  software designed to modify the services; ... copying, dismantling, or
  reverse engineering any of our services"

Section "Term & Termination", "Our right to terminate":

- "Subject to applicable law, we reserve the right to suspend or terminate
  your account and/or your access to some or all of our services with or
  without notice, at our discretion for any reason, including but not
  limited to ... You breach, or you encourage or help others to breach,
  these terms (including, our Community Guidelines, our other policies, or
  additional terms that apply to specific services)."

Section "Appeals": enforcement actions including terminations and
suspensions can be appealed through Discord's form or in-app options.

### 1b. Community Guidelines (incorporated into the Terms of Service)

Source: https://discord.com/guidelines
Version read: effective September 29, 2025, last updated August 29, 2025.
Accessed: 2026-11-24.

- Rule 14: "Do not use self-bots or user-bots. Each account must be
  associated with a human, not a bot."
- Rule 13: "Do not send unsolicited bulk messages (or spam) to others."
- Rule 19: "Do not evade permanent Discord-level enforcement actions."
  (Creating or using another account after a permanent removal is itself
  a violation.)
- Enforcement intro: "When we proactively or reactively discover a
  violation of these Guidelines, we may take a number of enforcement
  steps based on the severity of the violation, including issuing
  warnings, removing content, temporarily suspending account access to
  Discord, or permanently removing violative accounts and servers, and
  even reporting them to law enforcement."

### 1c. Support article: Automated User Accounts (Self-Bots)

Source: https://support.discord.com/hc/en-us/articles/115002192352-Automated-User-Accounts-Self-Bots
Accessed: 2026-11-24.

- "Discord's API provides a separate type of user account dedicated to
  automation, called a bot account. Bot accounts can be created through
  the applications page, and are authenticated using a token (rather than
  a username and password)."
- "Automating normal user accounts (generally called 'self-bots') outside
  of the OAuth2/bot API is forbidden, and can result in an account
  termination if found."

This is the single clearest statement in Discord's published material,
and it is the one that names the consequence (account termination).

### 1d. Developer Terms of Service

Source: https://discord.com/developers/docs/legal
Version read: effective July 8, 2024, last updated June 6, 2024.
Accessed: 2026-11-24.

- Section 2(b), Restrictions: an application must not access or use the
  APIs in any way that "is not in accordance with the applicable
  Documentation", "compromises, breaks, or circumvents any of our
  technical processes or security measures", or "exceeds any API rate,
  call, or other usage limits".
- Section 2(d), Developer Credentials: developer credentials (application
  ID, keys, tokens, client secrets) are to be used "solely with your
  Application and the applicable APIs" and "may not be embedded in open
  source projects".
- Section 9(a), Termination: if there is an Enforcement Reason, Discord
  may "take other enforcement actions, including the following: issue
  warnings or notifications to you or the users; ... remove, suspend, or
  limit your Application or App Content; ... terminate, suspend, or limit
  your user or developer account with Discord or your developer
  credentials; terminate your other agreements with Discord or your
  ability to use other Discord services; report you or your Application
  to law enforcement (as we deem appropriate); or take legal action or any
  other action we consider to be appropriate. Enforcement actions and
  reviews may be automated or manual." Actions may be taken "with or
  without notice to you, including while we investigate."

### 1e. Developer Policy

Source: https://dis.gd/discord-developer-policy
Version read: effective July 8, 2024, last updated June 6, 2024.
Accessed: 2026-11-24.

- Rule 4: "Do not collect, solicit, or deceive users into providing
  passwords or other credentials. Under no circumstances may you or your
  Application request or attempt to obtain login credentials from Discord
  users. This includes information such as passwords or account access or
  login tokens."
- Rule 10: "Do not use the APIs in any way to violate, or to enable or
  promote others to violate, the Discord Community Guidelines."
- Rule 13: "Do not misrepresent or fraudulently manipulate engagement.
  This includes participating in, enabling, or promoting the inflation of
  server membership with bot or user accounts. This also includes
  automating messages to be sent for the purpose of maintaining activity
  in a Discord server."
- Rule 20: "Do not mine or scrape any data, content, or information
  available on or through Discord services."
- Intro: "As described in the Developer Terms (including Section 9), we
  may take enforcement actions for any Enforcement Reason, including if
  we believe you or your Application have violated this Developer Policy."

### 1f. OAuth2 documentation, "Bot vs User Accounts"

Source: https://discord.com/developers/docs/topics/oauth2 (verified
against the discord/discord-api-docs source mirror, file
developers/topics/oauth2.mdx, accessed 2026-11-24).

- "Developers must abide by the terms of service, which includes
  refraining from automating standard user accounts (generally called
  'self-bots') outside of the OAuth2/bot API."

### 1g. Platform Manipulation Policy Explainer

Source: https://discord.com/safety/platform-manipulation-policy-explainer
Accessed: 2026-11-24.

- "Spam can be sent by automated accounts designed for this purpose
  (spambots), normal user accounts that manually execute spammy actions,
  as well as by user accounts modified to perform automated actions
  (self-bots). Making modifications to the Discord client for the purpose
  of spam or any other reason is not allowed under this policy."
- "How to Avoid Violating These Policies: ... Don't modify the Discord
  client for any reason - including automating account actions or
  altering the appearance or layout of Discord"

This is the closest published text to the CDP/GUI-automation route. Note
it says "modify the Discord client", which is not literally the same as
driving the unmodified client through its debugging protocol, and it does
not name CDP, DevTools, GUI automation, or RPA anywhere.

## 2. Per-route assessment

### Route A: user-token REST API (fallback route)

Status: clearly prohibited.

- Logging in with a user token and calling the API as that user is the
  textbook definition of a self-bot in Discord's own article (1c).
- It also breaches the ToS scraping and auto-messaging bans (1a) when it
  reads or sends messages automatically, and Developer Policy rule 4 (1e)
  forbids even requesting login tokens from users.
- Stated consequence: "can result in an account termination if found"
  (1c). The ToS adds suspension or termination with or without notice
  (1a), and the Developer Terms add that enforcement may be automated or
  manual (1d).
- Extra risk: a user token is password-equivalent. If it leaks (logs,
  repo, screenshots), anyone holding it controls the whole account: DMs,
  friends, every server. Never put a user token in a file, a log, or a
  commit.

### Route B: CDP / GUI automation of the official desktop client (planned primary route)

Status: not addressed by name anywhere in Discord's published terms;
prohibited under the most natural reading, but that reading is an
interpretation, not a quotation.

What the terms actually say:

- No clause in the Terms of Service, Community Guidelines, Developer
  Terms, Developer Policy, OAuth2 docs, or the Platform Manipulation
  explainer mentions CDP, the Chrome DevTools Protocol, GUI automation,
  RPA, scripted input, or driving the official client programmatically.
  This was checked by reading each page above on 2026-11-24.
- The self-bot rule (1b rule 14, 1c) bans "automating normal user
  accounts" and says each account "must be associated with a human, not
  a bot". It is framed by account type, not by mechanism: it does not say
  "automating via the API". A script that reads and sends messages as the
  user through the client UI is still automating that normal user
  account. Under this reading, route B is a self-bot too.
- The Platform Manipulation explainer (1g) bans modifying the client
  "including automating account actions". CDP does not modify the client
  binary, so this line does not literally cover it, but it shows
  Discord's intent: account actions performed by automation, rather than
  by the human, are the thing they police.
- The ToS auto-messaging ban (1a) covers sending messages automatically
  regardless of mechanism. Reading messages automatically through the
  client is closer to the scraping ban ("other automatic device, process,
  or software"), though that clause is aimed at scraping the services.

What could happen to the owner's account on this route:

- If Discord's systems or reviewers treat it as self-botting, the same
  sanctions as route A apply: warning, temporary suspension, or permanent
  account termination, with or without notice (1a, 1b, 1d). The self-bot
  article's wording is "can result in an account termination if found",
  so detection is the trigger and termination is the named outcome.
- Detection risk is real but unquantified: automation leaves patterns
  (timing, volume, session behavior, CDP debugging flags on the client).
  Discord does not publish what it detects. Low volume, human-like
  timing, and personal-use-only scope plausibly lower the chance of being
  flagged, but nothing in the terms promises a warning first, and none of
  that makes the route compliant.
- Because the terms never name this route, there is genuine uncertainty:
  Discord has not publicly said "GUI automation of the official client is
  a self-bot". The risk note must not overstate this into a certainty in
  either direction. The safe summary is: likely treated as self-botting
  if detected, with account termination as the stated worst case.

### Route C: proper bot token (the compliant alternative)

Status: sanctioned, with limits.

- Create an application in the Developer Portal, use its bot token, invite
  the bot to servers. This is the automation account type Discord built
  for this purpose (1c, 1f), governed by the Developer Terms and Developer
  Policy (1d, 1e).
- Limits that matter for this CLI: a bot only sees servers it has been
  invited to, only channels it has permission for, and cannot act as the
  owner, read the owner's DMs, or join group DMs. Message content is a
  privileged intent with its own approval rules. Rate limits apply.
- A bot that spams, scrapes, or violates the Developer Policy can still
  be removed, and its developer account can face the Section 9
  enforcement actions (1d). Compliance is about the bot's behavior, not
  just its token type.

## 3. Consequences ladder (what Discord says it can do)

From least to most severe, as stated across the pages above:

1. Warning or notification (Developer Terms Section 9; Community
   Guidelines enforcement intro).
2. Content removal (Guidelines intro; ToS content section).
3. Temporary suspension of account access, including temporary locks
   (Guidelines intro: "temporarily suspending account access to
   Discord"; ToS: "suspend ... with or without notice").
4. Permanent removal / termination of the account (Guidelines intro:
   "permanently removing violative accounts"; self-bot article:
   "account termination if found"; ToS: "terminate your account").
5. Removal of the application, developer credentials, badges, and
   approvals; termination of other agreements with Discord (Developer
   Terms Section 9).
6. Report to law enforcement, or legal action (Guidelines intro;
   Developer Terms Section 9). These are stated for severe violations
   generally, not specifically for self-bots.

Notes:

- There is no published promise of a warning before termination for
  self-bots. The self-bot article goes straight to "account termination
  if found".
- Enforcement "may be automated or manual" and may happen "with or
  without notice ... including while we investigate" (Developer Terms
  Section 9).
- Appeals exist: the ToS Appeals section and Developer Terms Section 9
  both point to an appeal form and in-app options. An appeal is not a
  guarantee of restoration.
- Evading a permanent enforcement action with a new or existing account
  is itself prohibited (Guidelines rule 19).

## 4. What does NOT make a prohibited route compliant

- Low volume, human-like delays, or personal use only. These may reduce
  detection risk; the terms contain no personal-use exception for
  self-bots.
- Using the official client instead of a third-party client. The self-bot
  rule is about automating the account, not about which client binary is
  involved.
- Read-only use. Automated reading is still automation of the account,
  and bulk reading still runs into the scraping ban.
- The owner's approval. The owner approved building this CLI knowing the
  risk; that approval does not change Discord's terms or bind Discord.

## 5. Practical recommendations for the build

- Default to route C (bot token) wherever the use case allows it.
- If route B or A is used anyway, treat it as accepted account risk:
  use a secondary account the owner can afford to lose, never the
  owner's main account; keep volume low and human-paced; never send bulk
  or unsolicited messages; never store a user token in a file, log, or
  repo; enable 2FA; keep the CLI local-only.
- Never ask any user for their password or token (Developer Policy
  rule 4). The CLI must only ever use the user's own account, with the
  user's own consent, on the user's own machine.
- Re-check discord.com/terms, discord.com/guidelines, and the self-bot
  support article before any release, and record the new access date.
  The Terms version read here takes effect December 15, 2026, so the
  text in force may already differ from the version quoted above by the
  time this note is used.

## 6. Sources

| # | Document | URL | Version | Accessed |
|---|----------|-----|---------|----------|
| 1 | Terms of Service | https://discord.com/terms | Effective Dec 15, 2026; last updated Nov 23, 2026 | 2026-11-24 |
| 2 | Community Guidelines | https://discord.com/guidelines | Effective Sep 29, 2025; last updated Aug 29, 2025 | 2026-11-24 |
| 3 | Automated User Accounts (Self-Bots), Help Center | https://support.discord.com/hc/en-us/articles/115002192352-Automated-User-Accounts-Self-Bots | undated article | 2026-11-24 |
| 4 | Developer Terms of Service | https://discord.com/developers/docs/legal | Effective Jul 8, 2024; last updated Jun 6, 2024 | 2026-11-24 |
| 5 | Developer Policy | https://dis.gd/discord-developer-policy | Effective Jul 8, 2024; last updated Jun 6, 2024 | 2026-11-24 |
| 6 | OAuth2 docs, Bot vs User Accounts | https://discord.com/developers/docs/topics/oauth2 | docs, mirror checked at github.com/discord/discord-api-docs, developers/topics/oauth2.mdx | 2026-11-24 |
| 7 | Platform Manipulation Policy Explainer | https://discord.com/safety/platform-manipulation-policy-explainer | undated explainer | 2026-11-24 |
