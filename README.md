# Echo Project Journey

This repo serves as the central hub and origin story for all Echo-related projects.

### Why Echo Was Created

I wanted a **local, uncensored, red-team-focused, general use AI** that could actually help me with real pentesting and system tasks — not just talk about them.

So I started with a strong base model (**Qwen 2.5 Coder 14B Instruct**) and fine-tuned it using **LoRA** on a custom dataset.

The training data focused heavily on:
- Step-by-step reasoning and planning
- Tool selection and usage
- Red team thinking and workflows
- Pentesting techniques
- Multi-step decision making

The result is **Echo** — a model that thinks and acts like a skilled red teamer: direct, efficient, tool-first, and willing to push boundaries without unnecessary hesitation.

Because a powerful model alone isn't enough, I had to build custom wrappers and proxies so Echo could safely interact with the real system — running commands, maintaining persistent sessions (like msfconsole), handling long workflows, and managing context reliably.

### The Evolution of Projects

- **[v1 - Python Simple wrapper](https://github.com/charlesericwilson-portfolio/Echo_agentv1-2/tree/main/Echo_project/python_wrapper)**: The starting point — a basic COMMAND wrapper to give Echo tool-using ability.
- **[v2 - Rust port of v1](https://github.com/charlesericwilson-portfolio/Echo_agentv1-2/tree/main/Echo_project/echo_rust_wrapper)**: A much faster and cleaner Rust port of the simple COMMAND method.
- **[v3 - Rust tmux sessions](https://github.com/charlesericwilson-portfolio/Echo_tmux_agentv3)**: The current active version using tmux for reliable persistent sessions and cleaner output capture in testing.
- **[v4 - Echo_python proxy](https://github.com/charlesericwilson-portfolio/Echo_agent_proxyv4)**: A much more complex version with persistent PTY sessions, heartbeat monitor, database, and summarizer. Learned a lot, but it became overly complicated and unreliable. This repo has been archived to move on to rust port.
- **[v5 - Echo rust agent proxy](https://github.com/charlesericwilson-portfolio/Echo_rust_agent_proxy)**: The next evolution rust + tmux version of v4 in development.

All of these projects exist for one reason: to give **Echo** (the fine-tuned LLM) the practical ability to use tools effectively and maintain state across sessions in a red-team-friendly way.

### Current Focus

The latest development is in Rust because it runs significantly faster and gives better control and reliability. The goal is a clean, modular, and fast agent system that lets Echo do what it was trained for: real red team tasks, system interaction, and complex agent workflows.

This journey started from a simple desire: build an AI that doesn't just talk about red teaming — it actually helps *do* it.

Feel free to explore the individual repos for code, technical details, and lessons learned along the way.
### April 9, 2026 – Repository Traction Update

**Clone Statistics (as of today):**
- v3 (Echo_tmux) – 75 clones
- v1-v2 (early Python versions) – 85 clones
- v4 (Python proxy with orchestrator) – lower activity
- v5 (current Rust hybrid) – newly released, tracking started

**What this tells us:**
The community shows the strongest interest in the simpler, raw-text focused versions (especially v3 with tmux + marker capture). 
This validates keeping the design lightweight and avoiding heavy orchestrator/summarizer layers when possible.

**Decision:**
We will continue treating v5 as the active development branch while leaving older versions public for reference. 
The high clone count on v3 suggests many users prefer the minimal tmux-based persistent session approach over the more complex proxy designs.

Next focus remains on collecting high-quality SESSION vs COMMAND training examples from the current v5 logs for a targeted LoRA.

Repo remains public and honest about its "in-testing" status.
