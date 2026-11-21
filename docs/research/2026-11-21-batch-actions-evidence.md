# Batched actions evidence: 10 more sources for the A1 pilot

Compiled: 2026-11-21. Purpose: collect published evidence on grouping many
actions into one observation, meaning code execution batching (the model
writes one program that performs many tool or UI actions) and multi-action
per observation (one model call emits a sequence that runs without an
intermediate screenshot or result). This supports the design of the A1
pilot, which batches predictable action sequences in this repository's
computer use executor.

Method and scope: every source below was opened and read on 2026-11-21.
Numbers are quoted only where the source states them. These 10 sources are
new relative to the earlier research notes in this repository: the
2026-10-19 batching and grounding note (OpenAI computer use guides,
OmniParser, UI-TARS, ShowUI) and the 2026-11-21 code mode integration note
(Cloudflare Code Mode, the Claude platform docs on programmatic tool
calling, goose code mode). Two Anthropic engineering posts appear here
because they are distinct publications from the platform docs already
covered, and they carry the measurements.

## 1. Code execution with MCP: Building more efficient agents

- Publisher: Anthropic (Engineering blog), published 2025-11-04
- URL: https://www.anthropic.com/engineering/code-execution-with-mcp
- Accessed: 2026-11-21
- Claim: presenting MCP servers as code APIs, so the agent writes one
  program instead of one tool call per step, cut token usage in their
  Google Drive to Salesforce workflow from 150,000 tokens to 2,000 tokens,
  a 98.7% saving. Mechanisms named: tool definitions load on demand instead
  of upfront, intermediate data is filtered inside the execution
  environment (in their example the agent sees 5 rows instead of 10,000),
  and loops, conditionals and error handling happen in code rather than as
  chained model calls. The post also notes agents can keep state in the
  execution environment and reuse it across steps.
- Evidence strength: vendor claim. One illustrative worked example, no
  benchmark methodology, no run count, no success rate comparison. The
  post itself frames the figure as an example, and its own caveat is that
  running agent generated code requires a secure execution environment
  with appropriate sandboxing, resource limits, and monitoring.

## 2. Introducing advanced tool use on the Claude Developer Platform

- Publisher: Anthropic, published 2025-11-24
- URL: https://www.anthropic.com/research/advanced-tool-use
- Accessed: 2026-11-21
- Claim: Programmatic Tool Calling, where Claude orchestrates tools from
  inside a code execution block instead of individual API round trips,
  reduced average token usage on complex research tasks from 43,588 to
  27,297 tokens, a 37% reduction, and a single code block can run 20 or
  more tool calls, removing the inference pass that each separate call
  would have cost. Reported accuracy effects on Anthropic internal
  evaluations: internal knowledge retrieval rose from 25.6% to 28.5% and
  the GIA benchmark from 46.5% to 51.2% with programmatic calling. The
  same post reports separate gains for the Tool Search Tool (tool
  definition overhead from about 77K tokens to about 8.7K).
- Evidence strength: vendor reported internal evaluations. More than an
  anecdote, since averages over a task set are reported, but the evals are
  Anthropic's own, not public benchmarks, and no independent replication
  is cited in the post.

## 3. Code Execution with MCP benchmark (AIMultiple), as audited by TokDocs

- Source read: "Is MCP Dead? Code Execution With MCP and the 77% Token
  Claim", Matt Cullerton, TokDocs, published 2026-10-26, a line by line
  audit of AIMultiple's benchmark article "Code Execution with MCP: A New
  Approach to AI Agent Efficiency" (Sevval Alper, updated 2026-09-09)
- URL: https://mattcullerton.com/tokdocs/is-mcp-dead-code-execution-with-mcp-and-the-77-token-claim/
- Accessed: 2026-11-21
- Claim: in AIMultiple's controlled comparison (GPT-4.1, one MCP server,
  Bright Data in Pro Mode, two task types, 50 runs per approach), code
  execution used 175,081 total tokens against 775,197 for regular MCP, a
  77.4% reduction, with average input tokens down 78.5% and task success
  at 100% for both approaches. The same table shows the costs of
  batching: output tokens rose 120% because the model writes code, and
  average latency rose about 7%, from 9.66 s to 10.37 s. Priced out, the
  cost saving is 74.1%, not 77.4%.
- Evidence strength: independent measured benchmark, but small and
  narrow: one model, one server, two task types. AIMultiple itself lists
  those limits, and notes success may fall on tasks where code quality
  matters more. This is the only source in this set that independently
  measured a latency penalty for code batching.

## 4. Executable Code Actions Elicit Better LLM Agents (CodeAct)

- Authors: Xingyao Wang and co-authors, ICML 2024
- URL: https://arxiv.org/html/2402.01030v4
- Accessed: 2026-11-21
- Claim: making each agent action a block of executable Python, which can
  combine multiple tool calls, loops and data flow into one step,
  outperformed text and JSON action formats across 17 LLMs on API-Bank
  and the authors' M3ToolEval benchmark: up to 20% higher success rate
  while requiring up to 30% fewer actions (interaction turns). Execution
  errors come back as feedback, so the agent can revise its next code
  action, a recovery path that single JSON calls do not have.
- Evidence strength: peer reviewed, measured benchmark, author run. The
  strongest experimental design in this set, though the tasks are API
  tasks, not GUI computer use, and the benchmark set for multi-tool tasks
  is small (82 tasks).

## 5. CoAct-1: Computer-Using Multi-Agent System with Coding Actions

- Authors: Salesforce AI Research and co-authors, ICLR 2026 (OpenReview)
- URL: https://openreview.net/pdf?id=l1MQVgIKEU
- Accessed: 2026-11-21
- Claim: a computer use system that routes subtasks either to a GUI
  operator or to a programmer agent that writes and executes Python or
  Bash scripts reached 60.8% success on OSWorld and 52.5% on
  WindowsAgentArena, state of the art on both at publication, ahead of
  GUI only frameworks. Gains were largest where one script replaces many
  GUI steps, for example Calc tasks at 70.21% and VS Code tasks at
  78.26%.
- Evidence strength: peer reviewed conference paper with measured
  benchmark results, author run. Directly about computer use, which most
  other sources here are not, but it tests hybrid routing to code, not
  pure GUI action batching, so it supports code execution as an escape
  hatch rather than longer GUI batches specifically.

## 6. OSWorld-Human: Benchmarking the Efficiency of Computer-Use Agents

- Authors: Reyna Abhyankar, Qi Qi, Yiying Zhang (UC San Diego, GenseeAI),
  2025
- URL: https://arxiv.org/html/2506.16042v1
- Accessed: 2026-11-21
- Claim: this paper defines the grouped-action trajectory, the closest
  published analogue of the A1 design: consecutive actions that can be
  correctly executed from the same visual observation are grouped and
  counted as one step, so one observation and one LLM call covers the
  whole group. Human gold trajectories for all 369 OSWorld tasks show
  grouping cuts steps in every application, for example LibreOffice Calc
  from 13.6 single actions to 5.9 groups, LibreOffice Impress from 8.5
  to 4.5, LibreOffice Writer from 9.0 to 6.1, Chrome from 6.8 to 5.0.
  Their latency study of Agent S2 found planning and reflection LLM calls
  account for 75% to 94% of total latency, later steps can take 3 times
  longer than early ones as context grows, and even the best agents take
  1.4 to 2.7 times more steps than the human trajectories require.
- Evidence strength: measured study with released data, 369 tasks, 16
  agents evaluated. Important limit: the paper measures the headroom for
  grouping from human trajectories; it does not run an agent that
  actually groups actions, so it proves the opportunity, not the success
  rate of a grouping agent. It also names where grouping fails: actions
  that trigger new windows, popups or major UI changes cannot share one
  observation, and applications with such changes show the smallest
  grouping gains.

## 7. Beyond Browsing: API-Based Web Agents

- Authors: Yueqi Song, Frank Xu, Shuyan Zhou, Graham Neubig (Carnegie
  Mellon University), Findings of ACL 2025
- URL: https://arxiv.org/html/2410.16464v1
- Accessed: 2026-11-21
- Claim: on WebArena, an agent acting through APIs and code instead of
  step by step browsing reached 29.2% success against 14.8% for the
  browsing agent, and a hybrid agent that switches between APIs and
  browsing reached 35.8%, more than 20 points above browsing alone. The
  API agents also finished in fewer steps on average, 7.8 against 8.4
  for browsing, because one API call or code block replaces several page
  interactions. The offsetting cost the paper reports is prompt size:
  API documentation inflates the context.
- Evidence strength: peer reviewed, measured benchmark, author run.
  About web tasks rather than desktop GUI, and the comparison is API
  access versus browsing, not batch length within one interface.

## 8. smolagents and the CodeAgent design (Hugging Face)

- Publisher: Hugging Face, smolagents library documentation and project
  page
- URLs: https://pypi.org/project/smolagents/1.16.1/ and
  https://huggingface.co/docs/smolagents/v1.26.0/guided_tour
- Accessed: 2026-11-21
- Claim: the framework's default CodeAgent writes each step as a Python
  snippet instead of a JSON tool call dictionary. The project states this
  uses 30% fewer steps, and therefore 30% fewer LLM calls, than the JSON
  pattern, and reaches higher performance on difficult benchmarks,
  because one code step can nest calls, loop, branch and reuse variables
  that JSON would need one model call each to handle.
- Evidence strength: framework vendor claim. The 30% figure is inherited
  from the CodeAct paper (source 4), not from a separate smolagents
  benchmark, so it corroborates adoption of the pattern rather than
  adding an independent measurement. The docs also state the operational
  risk plainly: generated code runs with real privileges unless a
  sandboxed executor is configured.

## 9. Selenium Actions API reference

- Publisher: Selenium project (official API documentation)
- URL: https://www.selenium.dev/selenium/docs/api/javascript/Actions.html
- Accessed: 2026-11-21
- Claim: browser automation has shipped multi-action per call for years
  at the driver level. A client builds an action sequence (pointer,
  keyboard and wheel inputs interleaved as ticks across devices) and one
  perform() call sends the whole sequence; the remote end executes it
  tick by tick until all actions complete. No observation or result is
  produced between actions inside a sequence. The source states no
  performance numbers; it is design evidence that a single call carrying
  many low level actions is a standard, supported interface, and that
  the trade is fixed in advance: nothing inside the sequence can react
  to intermediate page state.
- Evidence strength: primary documentation of a shipped interface. No
  measurements, and it concerns test automation rather than model driven
  agents, but it is the mechanism layer an agent side batch ultimately
  travels over when it drives a real browser through WebDriver.

## 10. Playwright MCP and the run code tool (Microsoft)

- Publisher: Microsoft, Playwright MCP server documentation
- URLs: https://playwright.dev/docs/getting-started-mcp and
  https://github.com/microsoft/playwright-mcp
- Accessed: 2026-11-21
- Claim: alongside its one action per call tools, Playwright MCP ships
  browser_run_code_unsafe, a single tool call that runs a whole
  Playwright script against the live page: "For complex interactions
  that go beyond individual tool calls, use the browser_run_code_unsafe
  tool to execute Playwright scripts directly." One call can navigate,
  click, fill and read, and returns one result, replacing a chain of
  snapshot and action calls. The docs state no performance numbers.
- Evidence strength: primary vendor documentation of a shipped feature,
  no measurements. Its value here is the risk framing, which the vendor
  states itself: the tool executes arbitrary JavaScript in the server
  process, is described as RCE-equivalent, should only be enabled for
  trusted clients, and the server "is not a security boundary". Code
  batching at this layer is deliberately opt-in because a batched script
  bypasses per action checks.

## Synthesis for the A1 pilot

What the combined evidence supports:

- The dominant cost in agent loops is the model call, not the action.
  OSWorld-Human measured planning and reflection calls at 75% to 94% of
  latency, and every source that counts steps treats one model call per
  group, not per action, as the saving. Batching predictable actions
  into one observation attacks the measured bottleneck.
- Code execution batching has consistent, large token savings across
  independent and vendor measurements: 37% on Anthropic's internal
  research tasks, 77.4% total tokens in AIMultiple's independent test,
  98.7% in Anthropic's single worked example. The direction is not in
  dispute; the size depends on tool count and on how much intermediate
  data would otherwise pass through the model.
- Fewer steps can coincide with equal or better success, not just lower
  cost: CodeAct measured up to 20% higher success with up to 30% fewer
  turns, CoAct-1 set OSWorld state of the art by routing work to
  scripts, and Beyond Browsing roughly doubled browsing success with
  API actions. AIMultiple found equal success (100% both arms) on its
  narrow task set.
- Grouping has a principled boundary, stated by OSWorld-Human: group
  only actions whose targets are all present in the current observation.
  Human trajectories show the available compression is real but bounded
  (roughly a factor of 2 on the most groupable applications, much less
  where actions open new windows or dialogs).

What the evidence does not prove:

- No source measures a GUI agent that batches raw pointer and keyboard
  actions per observation on desktop tasks end to end. OSWorld-Human
  measures the headroom from human trajectories; CodeAct and Beyond
  Browsing measure API and code actions; CoAct-1 measures routing to
  scripts. The A1 pilot still has to produce its own success and latency
  numbers for batched GUI actions specifically.
- The headline token figures come from tool heavy API workloads, where
  most saving is tool definitions and intermediate data never entering
  context. A screenshot driven GUI loop saves model turns, not tool
  schemas, so expect savings closer to the step reduction ratios
  (roughly 30% fewer turns in CodeAct, up to about half the steps in
  OSWorld-Human's groupable apps) than to 98.7%.
- Latency is not guaranteed to fall per task. The one independent
  benchmark that timed both arms found code execution about 7% slower
  per call and output tokens up 120%, because the model writes code.
  Batching pays when it removes whole model calls, which is a step
  count effect, not a per call effect.

Risks the sources name, which the pilot design must carry:

- Stale state inside a batch. A sequence planned from one observation
  cannot react to intermediate changes; OSWorld-Human's grouping rule
  (same observation must cover every action) and the Selenium design
  (no results inside a sequence) both mark this as the hard boundary.
  Batches must break at navigation, dialogs and any state the plan did
  not already see.
- Error recovery moves into the batch. With no observation between
  actions, a mid batch failure is only visible at the end, so the batch
  result must say how far it got. The compensating strength, from
  CodeAct and Anthropic, is that code batches can carry their own error
  handling and return execution errors as structured feedback for the
  next model call.
- Security surface grows. Anthropic requires a sandboxed execution
  environment with resource limits and monitoring for agent written
  code; Hugging Face warns code agents execute with real privileges by
  default; Microsoft ships its run code tool as explicitly unsafe and
  opt-in. A batch executor that runs model written code inherits all
  of this, and per action approval checks no longer see the individual
  actions inside a batch.
