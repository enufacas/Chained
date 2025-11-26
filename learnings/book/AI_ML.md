# 🤖 AI & Machine Learning

> Artificial intelligence, machine learning, LLMs, and neural networks

**Total Insights:** 3974

**Last Updated:** 2025-11-26

---


## 📰 From Agent Evolution System Implementation


### Genetic Algorithm Evolution for AI Agents


**Content Summary:**

The Agent Evolution System introduces Darwinian evolution to the Chained ecosystem. High-performing agents (fitness >= 0.5) can breed to create offspring with mixed traits from both parents. The system implements: (1) Fitness-based selection using overall_score + longevity_bonus, (2) Uniform crossover where each gene is randomly inherited from either parent, (3) Random mutations at 15% rate with ±20 point variations bounded [0,100], (4) Complete lineage tracking with parent-offspring relationshi...

---


### Integration Patterns for Autonomous Systems


**Content Summary:**

The evolution system integrates with existing infrastructure through: (1) Weekly cron job (Sundays at midnight) after agent evaluation, (2) Automatic issue creation documenting each generation, (3) Git commits for evolution data persistence, (4) Compatibility with existing agent registry format, (5) Manual integration point for adding offspring to active population. Key design decision: Keep evolution separate from spawning to maintain modularity. The system generates evolution data that can be ...

---


### Genetic Diversity Through Specialization Mutations


**Content Summary:**

Specialization mutation occurs at 3% rate (15% base * 0.2) and only shifts to related types. Families defined: organize-* (refactoring agents), secure-* (security agents), engineer-* (builders), assert-* (testers), etc. This prevents random specialization chaos while enabling evolutionary adaptation. For example: organize-guru can mutate to organize-specialist or refactor-champion, but not to secure-ninja. This maintains coherent agent identities while allowing gradual specialization evolution. ...

---


### Documentation as First-Class Deliverable


**Content Summary:**

The 300+ line README includes: (1) Overview and features, (2) Installation and requirements, (3) CLI and Python API usage, (4) Detailed algorithm explanations, (5) Data structure documentation, (6) Configuration reference, (7) Integration patterns, (8) Performance characteristics, (9) Troubleshooting guide, (10) Future enhancements, (11) Academic references. Following @accelerate-specialist principles: documentation is not an afterthought but a core deliverable. Good documentation enables autono...

---


## 📰 From GitHub Copilot (Combined)


### GitHub Copilot Docs: About billing for GitHub Copilot in organizations and enterprises

**Link:** https://docs.github.com/en/copilot/concepts/billing/organizations-and-enterprises


**Content Summary:**

About billing for GitHub Copilot in organizations and enterprises
Learn about pricing and billing cycles for Copilot.
Who can use this feature?
Organizations on a GitHub Free or GitHub Team plan, or organizations and enterprises on GitHub Enterprise Cloud
In this article
Available plans
GitHub offers the following plans for organization accounts:
Copilot Business
at $19 USD per user per month (Purchase additional premium requests at $0.04 USD per request)
Copilot Enterprise
at $39 USD per user p...

---


### GitHub Copilot Docs: About billing for individual GitHub Copilot plans

**Link:** https://docs.github.com/en/copilot/concepts/billing/billing-for-individuals


**Content Summary:**

About billing for individual GitHub Copilot plans
Learn how billing works for Copilot Pro and Copilot Pro+.
In this article
Pricing for Copilot Pro and Copilot Pro+
GitHub offers two paid plans for individuals: Copilot Pro and Copilot Pro+. Both plans are available on a monthly or yearly billing cycle.
Copilot Pro
If you choose a monthly billing cycle
, you will be billed $10 USD per calendar month.
If you choose a yearly billing cycle
, you will be billed $100 USD per year.
Copilot Pro+
If you ...

---


### GitHub Copilot Docs: About Copilot auto model selection

**Link:** https://docs.github.com/en/copilot/concepts/auto-model-selection


**Content Summary:**

About Copilot auto model selection
Automatically select models for Copilot Chat.
Who can use this feature?
Auto model selection is in  public preview for supported IDEs with all GitHub Copilot plans.
In this article
Overview
Experience less rate limiting and reduce the mental load of choosing a model by letting Copilot auto model selection automatically choose the best available model on your behalf.
Copilot auto model selection is currently optimized for model availability, choosing from a list...

---


### GitHub Copilot Docs: About customizing GitHub Copilot responses

**Link:** https://docs.github.com/en/copilot/concepts/prompting/response-customization


**Content Summary:**

About customizing GitHub Copilot responses
Learn about customizing the behavior of GitHub Copilot to fit with your preferences and requirements.
Tool navigation
In this article
Note
This version of this article is about custom instructions on the GitHub website. Click the tabs above for other environments.
About customizing Copilot responses
GitHub Copilot can provide responses that are tailored to your personal preferences, the way your team works, the tools you use, or the specifics of your pr...

---


### GitHub Copilot Docs: About GitHub Copilot Chat

**Link:** https://docs.github.com/en/copilot/concepts/chat


**Content Summary:**

About GitHub Copilot Chat
Learn how you can use GitHub Copilot Chat to enhance your coding experience.
In this article
Overview
GitHub Copilot Chat is the AI-powered chat interface for GitHub Copilot. It allows you to interact with AI models to get coding assistance, explanations, and suggestions in a conversational format.
Copilot Chat can help you with a variety of coding-related tasks, like offering you code suggestions, providing natural language descriptions of a piece of code's functionali...

---


### GitHub Discussion: Copilot L1 Test generation

**Link:** https://github.com/rdkcentral/entservices-softwareupdate/pull/164


No description

---


### GitHub Discussion: Feature: Add GitHub Copilot as model provider

**Link:** https://github.com/Aider-AI/aider/issues/2227


**Content Summary:**

### Issue

Hello!

Please add GitHub Copilot as model provider.

Should be possible like this: https://github.com/olimorris/codecompanion.nvim/blob/5c5a5c759b8c925e81f8584a0279eefc8a6c6643/lua/codecompanion/adapters/copilot.lua

Idea taken from: https://github.com/cline/cline/discussions/660

Thank you!

### Version and model info

_No response_

---


### GitHub Discussion: Ability to import docker-compose defintion and convert them as Copilot app and services

**Link:** https://github.com/aws/copilot-cli/issues/1612


**Content Summary:**

Docker compose is commonly used for local development and testing. We need an ability for Copilot to import Docker Compose files and convert them as Copilot native app and svc objects, in a guide way. This will be a big boost for developers.

---


### GitHub Discussion: sync github copilot chat history across devices

**Link:** https://github.com/microsoft/vscode-copilot-release/issues/991


**Content Summary:**

I really wish it were possible to sync copilot chat histories across devices, ex: I use a laptop on the go and a desktop at home. I usually keep both devices lock-step via GitHub but it sucks that the chat history is different on both devices. I can usually enter in the same prompt to get a similar answer but it just seems counter intuitive that the chats do not sync by default, or there is not at least an option to sync the chats. Thanks

---


### GitHub Discussion: Copilot Chat support

**Link:** https://github.com/github/copilot.vim/issues/57


**Content Summary:**

Creating a placeholder as I know this is a [popular request](https://github.com/orgs/community/discussions/50939). I am exploring options here, but it is not officially on the roadmap at this time. If/when it does happen, it will almost certainly happen in tandem with [support in the Copilot Language Server SDK](https://github.com/github/copilot-language-server-release/issues/1).


---


### GitHub Copilot Docs: About billing for GitHub Copilot in organizations and enterprises

**Link:** https://docs.github.com/en/copilot/concepts/billing/organizations-and-enterprises


**Content Summary:**

About billing for GitHub Copilot in organizations and enterprises
Learn about pricing and billing cycles for Copilot.
Who can use this feature?
Organizations on a GitHub Free or GitHub Team plan, or organizations and enterprises on GitHub Enterprise Cloud
In this article
Available plans
GitHub offers the following plans for organization accounts:
Copilot Business
at $19 USD per user per month (Purchase additional premium requests at $0.04 USD per request)
Copilot Enterprise
at $39 USD per user p...

---


### GitHub Copilot Docs: About billing for individual GitHub Copilot plans

**Link:** https://docs.github.com/en/copilot/concepts/billing/billing-for-individuals


**Content Summary:**

About billing for individual GitHub Copilot plans
Learn how billing works for Copilot Pro and Copilot Pro+.
In this article
Pricing for Copilot Pro and Copilot Pro+
GitHub offers two paid plans for individuals: Copilot Pro and Copilot Pro+. Both plans are available on a monthly or yearly billing cycle.
Copilot Pro
If you choose a monthly billing cycle
, you will be billed $10 USD per calendar month.
If you choose a yearly billing cycle
, you will be billed $100 USD per year.
Copilot Pro+
If you ...

---


### GitHub Copilot Docs: About Copilot auto model selection

**Link:** https://docs.github.com/en/copilot/concepts/auto-model-selection


**Content Summary:**

About Copilot auto model selection
Automatically select models for Copilot Chat.
Who can use this feature?
Auto model selection is in  public preview for supported IDEs with all GitHub Copilot plans.
In this article
Overview
Experience less rate limiting and reduce the mental load of choosing a model by letting Copilot auto model selection automatically choose the best available model on your behalf.
Copilot auto model selection is currently optimized for model availability, choosing from a list...

---


### GitHub Copilot Docs: About customizing GitHub Copilot responses

**Link:** https://docs.github.com/en/copilot/concepts/prompting/response-customization


**Content Summary:**

About customizing GitHub Copilot responses
Learn about customizing the behavior of GitHub Copilot to fit with your preferences and requirements.
Tool navigation
In this article
Note
This version of this article is about custom instructions on the GitHub website. Click the tabs above for other environments.
About customizing Copilot responses
GitHub Copilot can provide responses that are tailored to your personal preferences, the way your team works, the tools you use, or the specifics of your pr...

---


### GitHub Copilot Docs: About GitHub Copilot Chat

**Link:** https://docs.github.com/en/copilot/concepts/chat


**Content Summary:**

About GitHub Copilot Chat
Learn how you can use GitHub Copilot Chat to enhance your coding experience.
In this article
Overview
GitHub Copilot Chat is the AI-powered chat interface for GitHub Copilot. It allows you to interact with AI models to get coding assistance, explanations, and suggestions in a conversational format.
Copilot Chat can help you with a variety of coding-related tasks, like offering you code suggestions, providing natural language descriptions of a piece of code's functionali...

---


### GitHub Discussion: Copilot L1 Test generation

**Link:** https://github.com/rdkcentral/entservices-softwareupdate/pull/164


No description

---


### GitHub Discussion: Feature: Add GitHub Copilot as model provider

**Link:** https://github.com/Aider-AI/aider/issues/2227


**Content Summary:**

### Issue

Hello!

Please add GitHub Copilot as model provider.

Should be possible like this: https://github.com/olimorris/codecompanion.nvim/blob/5c5a5c759b8c925e81f8584a0279eefc8a6c6643/lua/codecompanion/adapters/copilot.lua

Idea taken from: https://github.com/cline/cline/discussions/660

Thank you!

### Version and model info

_No response_

---


### GitHub Discussion: Ability to import docker-compose defintion and convert them as Copilot app and services

**Link:** https://github.com/aws/copilot-cli/issues/1612


**Content Summary:**

Docker compose is commonly used for local development and testing. We need an ability for Copilot to import Docker Compose files and convert them as Copilot native app and svc objects, in a guide way. This will be a big boost for developers.

---


### GitHub Discussion: sync github copilot chat history across devices

**Link:** https://github.com/microsoft/vscode-copilot-release/issues/991


**Content Summary:**

I really wish it were possible to sync copilot chat histories across devices, ex: I use a laptop on the go and a desktop at home. I usually keep both devices lock-step via GitHub but it sucks that the chat history is different on both devices. I can usually enter in the same prompt to get a similar answer but it just seems counter intuitive that the chats do not sync by default, or there is not at least an option to sync the chats. Thanks

---


### GitHub Discussion: Copilot Chat support

**Link:** https://github.com/github/copilot.vim/issues/57


**Content Summary:**

Creating a placeholder as I know this is a [popular request](https://github.com/orgs/community/discussions/50939). I am exploring options here, but it is not officially on the roadmap at this time. If/when it does happen, it will almost certainly happen in tandem with [support in the Copilot Language Server SDK](https://github.com/github/copilot-language-server-release/issues/1).


---


## 📰 From GitHub Trending


### sansan0/TrendRadar - 🎯 告别信息过载，AI 助你看懂新闻资讯热点，简单的舆情监控分析 - 多平台热点聚合+基于 MCP 的AI分析工具。监控35个平台（抖音、知乎、B站、华尔街见闻、财联社等），智能筛选+自动推送+AI对

**Link:** https://github.com/sansan0/TrendRadar


🎯 告别信息过载，AI 助你看懂新闻资讯热点，简单的舆情监控分析 - 多平台热点聚合+基于 MCP 的AI分析工具。监控35个平台（抖音、知乎、B站、华尔街见闻、财联社等），智能筛选+自动推送+AI对话分析（用自然语言深度挖掘新闻：趋势追踪、情感分析、相似检索等13种工具）。支持企业微信/飞书/钉钉/Telegram/邮件/ntfy推送，30秒网页部署，1分钟手机通知，无需编程。支持Docker部署⭐ 让算法为你服务，用AI理解热点

---


### yeongpin/cursor-free-vip - [Support 0.49.x]（Reset Cursor AI MachineID & Bypass Higher Token Limit） Cursor Ai ，自动重置机器ID ， 免费升级使用

**Link:** https://github.com/yeongpin/cursor-free-vip


[Support 0.49.x]（Reset Cursor AI MachineID & Bypass Higher Token Limit） Cursor Ai ，自动重置机器ID ， 免费升级使用Pro功能: You've reached your trial request limit. / Too many free trial accounts used on this machine. Please upgrade to pro. We have this limit in place to prevent abuse. Please let us know if you believe this is a mistake.

---


### volcengine/verl - verl: Volcano Engine Reinforcement Learning for LLMs

**Link:** https://github.com/volcengine/verl


verl: Volcano Engine Reinforcement Learning for LLMs

---


### GibsonAI/Memori - Open-Source Memory Engine for LLMs, AI Agents & Multi-Agent Systems

**Link:** https://github.com/GibsonAI/Memori


Open-Source Memory Engine for LLMs, AI Agents & Multi-Agent Systems

---


### WordPress/gutenberg - The Block Editor project for WordPress and beyond. Plugin is available from the official repository.

**Link:** https://github.com/WordPress/gutenberg


The Block Editor project for WordPress and beyond. Plugin is available from the official repository.

---


### google/adk-go - An open-source, code-first Go toolkit for building, evaluating, and deploying sophisticated AI agent

**Link:** https://github.com/google/adk-go


An open-source, code-first Go toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control.

---


### beclab/Olares - Olares: An Open-Source Personal Cloud to Reclaim Your Data

**Link:** https://github.com/beclab/Olares


Olares: An Open-Source Personal Cloud to Reclaim Your Data

---


### greenbone/openvas-scanner - This repository contains the scanner component for Greenbone Community Edition.

**Link:** https://github.com/greenbone/openvas-scanner


This repository contains the scanner component for Greenbone Community Edition.

---


### ai-dynamo/dynamo - A Datacenter Scale Distributed Inference Serving Framework

**Link:** https://github.com/ai-dynamo/dynamo


A Datacenter Scale Distributed Inference Serving Framework

---


### iptv-org/iptv - Collection of publicly available IPTV channels from all over the world

**Link:** https://github.com/iptv-org/iptv


Collection of publicly available IPTV channels from all over the world

---


### sansan0/TrendRadar - 🎯 告别信息过载，AI 助你看懂新闻资讯热点，简单的舆情监控分析 - 多平台热点聚合+基于 MCP 的AI分析工具。监控35个平台（抖音、知乎、B站、华尔街见闻、财联社等），智能筛选+自动推送+AI对

**Link:** https://github.com/sansan0/TrendRadar


🎯 告别信息过载，AI 助你看懂新闻资讯热点，简单的舆情监控分析 - 多平台热点聚合+基于 MCP 的AI分析工具。监控35个平台（抖音、知乎、B站、华尔街见闻、财联社等），智能筛选+自动推送+AI对话分析（用自然语言深度挖掘新闻：趋势追踪、情感分析、相似检索等13种工具）。支持企业微信/飞书/钉钉/Telegram/邮件/ntfy推送，30秒网页部署，1分钟手机通知，无需编程。支持Docker部署⭐ 让算法为你服务，用AI理解热点

---


### yeongpin/cursor-free-vip - [Support 0.49.x]（Reset Cursor AI MachineID & Bypass Higher Token Limit） Cursor Ai ，自动重置机器ID ， 免费升级使用

**Link:** https://github.com/yeongpin/cursor-free-vip


[Support 0.49.x]（Reset Cursor AI MachineID & Bypass Higher Token Limit） Cursor Ai ，自动重置机器ID ， 免费升级使用Pro功能: You've reached your trial request limit. / Too many free trial accounts used on this machine. Please upgrade to pro. We have this limit in place to prevent abuse. Please let us know if you believe this is a mistake.

---


### volcengine/verl - verl: Volcano Engine Reinforcement Learning for LLMs

**Link:** https://github.com/volcengine/verl


verl: Volcano Engine Reinforcement Learning for LLMs

---


### GibsonAI/Memori - Open-Source Memory Engine for LLMs, AI Agents & Multi-Agent Systems

**Link:** https://github.com/GibsonAI/Memori


Open-Source Memory Engine for LLMs, AI Agents & Multi-Agent Systems

---


### WordPress/gutenberg - The Block Editor project for WordPress and beyond. Plugin is available from the official repository.

**Link:** https://github.com/WordPress/gutenberg


The Block Editor project for WordPress and beyond. Plugin is available from the official repository.

---


### google/adk-go - An open-source, code-first Go toolkit for building, evaluating, and deploying sophisticated AI agent

**Link:** https://github.com/google/adk-go


An open-source, code-first Go toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control.

---


### beclab/Olares - Olares: An Open-Source Personal Cloud to Reclaim Your Data

**Link:** https://github.com/beclab/Olares


Olares: An Open-Source Personal Cloud to Reclaim Your Data

---


### greenbone/openvas-scanner - This repository contains the scanner component for Greenbone Community Edition.

**Link:** https://github.com/greenbone/openvas-scanner


This repository contains the scanner component for Greenbone Community Edition.

---


### ai-dynamo/dynamo - A Datacenter Scale Distributed Inference Serving Framework

**Link:** https://github.com/ai-dynamo/dynamo


A Datacenter Scale Distributed Inference Serving Framework

---


### iptv-org/iptv - Collection of publicly available IPTV channels from all over the world

**Link:** https://github.com/iptv-org/iptv


Collection of publicly available IPTV channels from all over the world

---


## 📰 From Hacker News


### AI World Clocks

**Community Score:** 1255 upvotes

**Link:** https://clocks.brianmoore.com/


**Content Summary:**

? × About AI World Clocks Every minute, a new clock is displayed that has been generated by nine different AI models. Each model is allowed 2000 tokens to generate its clock. Here is its prompt: Create HTML/CSS of an analog clock showing ${time}. Include numbers (or numerals) if you wish, and have a CSS animated second hand. Make it responsive and use a white background. Return ONLY the HTML/CSS code with no markdown formatting. Created by Brian Moore . You can also follow him on Instagram . Ide...

---


### A new Google model is nearly perfect on automated handwriting recognition

**Community Score:** 438 upvotes

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### Llmdeathcount.com

**Link:** https://llmdeathcount.com/

---


### I implemented an ISO 42001-certified AI Governance program in 6 months

**Link:** https://beabytes.com/iso42001-certified-ai-governance/

---


### Trellis AI (YC W24) Is Hiring: Streamline access to life-saving therapies

**Link:** https://www.ycombinator.com/companies/trellis-ai/jobs/f4GWvH0-forward-deployed-engineer-full-time

---


### AI World Clocks

**Link:** https://clocks.brianmoore.com/


&quot;Every minute, a new clock is rendered by nine different AI models.&quot;

---


### Strap Rail

**Link:** https://www.construction-physics.com/p/strap-rail

---


### Streaming AI agent desktops with gaming protocols

**Link:** https://blog.helix.ml/p/technical-deep-dive-on-streaming

---


### A new Google model is nearly perfect on automated handwriting recognition

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### An Antivenom Cocktail, Made by a Llama

**Link:** https://www.asimov.press/p/broad-antivenom

---


### AI World Clocks

**Community Score:** 1089 upvotes

**Link:** https://clocks.brianmoore.com/


**Content Summary:**

? × About AI World Clocks Every minute, a new clock is displayed that has been generated by nine different AI models. Each model is allowed 2000 tokens to generate its clock. Here is its prompt: Create HTML/CSS of an analog clock showing ${time}. Include numbers (or numerals) if you wish, and have a CSS animated second hand. Make it responsive and use a white background. Return ONLY the HTML/CSS code with no markdown formatting. Created by Brian Moore . You can also follow him on Instagram . Ide...

---


### A new Google model is nearly perfect on automated handwriting recognition

**Community Score:** 369 upvotes

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### All praise to the lunch ladies

**Community Score:** 204 upvotes

**Link:** https://bittersoutherner.com/issue-no-12/all-praise-to-the-lunch-ladies


**Content Summary:**

Better South / Better Word All Praise to the Lunch Ladies Blessed are the women who watch over America’s children. Words by Jennifer Justus | Photos by Houston Cofield Portaits featured in this story were taken at Peabody High School and Trenton Elementary School in Trenton, Tennessee. November 4, 2025 Granny won me over with the government cheese. As a child, maybe 4 or 5 years old, when I’d visit her on occasional Sundays in Blue Ridge, Georgia, she’d slice me off a little treat — an orange re...

---


### AI World Clocks

**Link:** https://clocks.brianmoore.com/


&quot;Every minute, a new clock is rendered by nine different AI models.&quot;

---


### A new Google model is nearly perfect on automated handwriting recognition

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### No Leak, No Problem – Bypassing ASLR with a ROP Chain to Gain RCE

**Link:** https://modzero.com/en/blog/no-leak-no-problem/

---


### All praise to the lunch ladies

**Link:** https://bittersoutherner.com/issue-no-12/all-praise-to-the-lunch-ladies

---


### GEN-0 / Embodied Foundation Models That Scale with Physical Interaction

**Link:** https://generalistai.com/blog/nov-04-2025-GEN-0

---


### Show HN: Tiny Diffusion – A character-level text diffusion model from scratch

**Link:** https://github.com/nathan-barry/tiny-diffusion


This is a character-level language diffusion model for text generation.<p>The model is a modified version of Nanochat&#x27;s GPT implementation and is trained on Tiny Shakespeare!<p>It is only 10.7 million parameters, so you can try it out locally.

---


### Mentra (YC W25) Is Hiring: Head of Growth to Make Smart Glasses Mainstream

**Link:** https://www.ycombinator.com/companies/mentra/jobs/2YbQCRw-make-smart-glasses-mainstream-head-of-growth

---


## 📰 From TLDR Tech


### Apple Mini Apps 📱, Blue Origin lands rocket 🚀, GPT-5.1 for devs 👨‍💻 

**Link:** https://tldr.tech/tech/2025-11-14


**Content Summary:**

Stability or and innovation in payments technology (Sponsor)
Why pick one?
With Marqeta, launch payments experiences without choosing between innovation and scale.
Marqeta
combines the scale and reliability of proven payments infrastructure with the flexibility and innovation of a modern platform—so you can move faster, reduce risk, and grow with confidence.
From optimizing spend and cash flow to building seamless, rewards-driven customer experiences, Marqeta's solutions have you covered. When i...

---


### GPT-5.1 🤖, Waymo hits highways 🚗, Homebrew 5 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-13


**Content Summary:**

Your fast path to production MCP (Sponsor)
Gram is the MCP cloud.
Create, host, and scale MCP servers
without the hassle.
Create an agent tool library by defining tools with our lightweight TypeScript framework, importing your APIs, or uploading an existing MCP server. Curate tools into custom toolsets and deploy them as MCP servers.
MCP servers hosted on
Gram
work out of the box with your favorite MCP clients and agent frameworks: Claude, Cursor, OpenAI, Langchain, and more. Scale from zero to ...

---


### iPhone Air flops 📱, Anthropic OpenAI financials leak 💰, becoming a compiler engineer 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-11


**Content Summary:**

Goodbye low test coverage and slow QA cycles (Sponsor)
Bugs sneak out when less than 80% of user flows are tested before shipping. However, getting that kind of coverage (and staying there) is hard and pricey for any team.
QA Wolf's
AI-native solution provides high-volume, high-speed test coverage for web and mobile apps, reducing your organization's QA cycle to minutes.
They can get you:
80% automated E2E test coverage in weeks
—not years
Unlimited parallel test runs
24-hour maintenance and on-...

---


### MSFT OpenAI docs leak 📄, GPT-5.1 🤖, Anthropic’s $50B Bet 💰

**Link:** https://tldr.tech/ai/2025-11-13


**Content Summary:**

Get access to the most performant Kimi K2 Thinking API (Sponsor)
This week, Baseten released Kimi K2 Thinking on Model APIs. Kimi K2 Thinking rivals the leading closed-source agentic models and is engineered for complex reasoning and agentic workflows.With Baseten's API you can get an LLM that is smarter, faster and cheaper. The Kimi K2 Thinking API is built for production workloads with high uptime, scalability, and performance stability:
🧨 Blistering TTFT at 0.3 seconds
⚡140+ tokens per second...

---


### ChatGPT Group Chats 💬, growing an RL environment 🌍, ElevenLabs Scribe v2 🗣

**Link:** https://tldr.tech/ai/2025-11-12


**Content Summary:**

100 prompts for Notion Agents (Sponsor)
Not sure what you can do with Notion Agents? Here are
100 ideas
to get you started...
🐾 This
collection of outcome-oriented prompts
comes with “Agent Steps” that show exactly how an Agent will execute and what it will produce (e.g., dashboards, databases, reports).
🗂️ It's organized by function, so you can find the exact use case you want to solve for (analytics, strategy, event planning, CX...) and test the prompts instantly.
🔌 Connect other data sources ...

---


### Grok Code Remote 👨‍💻 , GPT-5.1 on OpenRouter 🤖, Moonshot AI AMA 💬

**Link:** https://tldr.tech/ai/2025-11-11


**Content Summary:**

Airia: Enterprise AI Orchestration — Agents, Integrations, Workflows, and Governance (Sponsor)
You want AI to become part of your organizational DNA - and that means enabling every department to build out their own use cases, without IT gatekeepers standing in the way. But it shouldn't mean an ungoverned free-for-all.
Airia is the
“let's get serious about AI adoption” platform
. Rapidly prototype, deploy, and manage AI agents that transform workflows across your organization - without sacrificin...

---


### Nano Banana 2 leaks 🍌, GPT-5-Codex-Mini 👨‍💻, nested learning 🧠

**Link:** https://tldr.tech/ai/2025-11-10


**Content Summary:**

OpenAI's head of financial engineering shares her monetization strategy for hypergrowth (Sponsor)
ChatGPT is only one part of OpenAI's success. The other part is the breathtaking speed with which
OpenAI built a new monetization model
.
In a fireside chat at Monetize 2025, OpenAI's Head of Financial Engineering, Sara Conlon, explained how she built an
engineering billing org poised for hypergrowth
.
Read the blog to learn:
Why centralizated monetization infrastructure is essential
Hard lessons fr...

---


### Apple Mini Apps 📱, Blue Origin lands rocket 🚀, GPT-5.1 for devs 👨‍💻 

**Link:** https://tldr.tech/tech/2025-11-14


**Content Summary:**

Stability or and innovation in payments technology (Sponsor)
Why pick one?
With Marqeta, launch payments experiences without choosing between innovation and scale.
Marqeta
combines the scale and reliability of proven payments infrastructure with the flexibility and innovation of a modern platform—so you can move faster, reduce risk, and grow with confidence.
From optimizing spend and cash flow to building seamless, rewards-driven customer experiences, Marqeta's solutions have you covered. When i...

---


### GPT-5.1 🤖, Waymo hits highways 🚗, Homebrew 5 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-13


**Content Summary:**

Your fast path to production MCP (Sponsor)
Gram is the MCP cloud.
Create, host, and scale MCP servers
without the hassle.
Create an agent tool library by defining tools with our lightweight TypeScript framework, importing your APIs, or uploading an existing MCP server. Curate tools into custom toolsets and deploy them as MCP servers.
MCP servers hosted on
Gram
work out of the box with your favorite MCP clients and agent frameworks: Claude, Cursor, OpenAI, Langchain, and more. Scale from zero to ...

---


### iPhone Air flops 📱, Anthropic OpenAI financials leak 💰, becoming a compiler engineer 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-11


**Content Summary:**

Goodbye low test coverage and slow QA cycles (Sponsor)
Bugs sneak out when less than 80% of user flows are tested before shipping. However, getting that kind of coverage (and staying there) is hard and pricey for any team.
QA Wolf's
AI-native solution provides high-volume, high-speed test coverage for web and mobile apps, reducing your organization's QA cycle to minutes.
They can get you:
80% automated E2E test coverage in weeks
—not years
Unlimited parallel test runs
24-hour maintenance and on-...

---


### MSFT OpenAI docs leak 📄, GPT-5.1 🤖, Anthropic’s $50B Bet 💰

**Link:** https://tldr.tech/ai/2025-11-13


**Content Summary:**

Get access to the most performant Kimi K2 Thinking API (Sponsor)
This week, Baseten released Kimi K2 Thinking on Model APIs. Kimi K2 Thinking rivals the leading closed-source agentic models and is engineered for complex reasoning and agentic workflows.With Baseten's API you can get an LLM that is smarter, faster and cheaper. The Kimi K2 Thinking API is built for production workloads with high uptime, scalability, and performance stability:
🧨 Blistering TTFT at 0.3 seconds
⚡140+ tokens per second...

---


### ChatGPT Group Chats 💬, growing an RL environment 🌍, ElevenLabs Scribe v2 🗣

**Link:** https://tldr.tech/ai/2025-11-12


**Content Summary:**

100 prompts for Notion Agents (Sponsor)
Not sure what you can do with Notion Agents? Here are
100 ideas
to get you started...
🐾 This
collection of outcome-oriented prompts
comes with “Agent Steps” that show exactly how an Agent will execute and what it will produce (e.g., dashboards, databases, reports).
🗂️ It's organized by function, so you can find the exact use case you want to solve for (analytics, strategy, event planning, CX...) and test the prompts instantly.
🔌 Connect other data sources ...

---


### Grok Code Remote 👨‍💻 , GPT-5.1 on OpenRouter 🤖, Moonshot AI AMA 💬

**Link:** https://tldr.tech/ai/2025-11-11


**Content Summary:**

Airia: Enterprise AI Orchestration — Agents, Integrations, Workflows, and Governance (Sponsor)
You want AI to become part of your organizational DNA - and that means enabling every department to build out their own use cases, without IT gatekeepers standing in the way. But it shouldn't mean an ungoverned free-for-all.
Airia is the
“let's get serious about AI adoption” platform
. Rapidly prototype, deploy, and manage AI agents that transform workflows across your organization - without sacrificin...

---


### Nano Banana 2 leaks 🍌, GPT-5-Codex-Mini 👨‍💻, nested learning 🧠

**Link:** https://tldr.tech/ai/2025-11-10


**Content Summary:**

OpenAI's head of financial engineering shares her monetization strategy for hypergrowth (Sponsor)
ChatGPT is only one part of OpenAI's success. The other part is the breathtaking speed with which
OpenAI built a new monetization model
.
In a fireside chat at Monetize 2025, OpenAI's Head of Financial Engineering, Sara Conlon, explained how she built an
engineering billing org poised for hypergrowth
.
Read the blog to learn:
Why centralizated monetization infrastructure is essential
Hard lessons fr...

---


### Apple Mini Apps 📱, Blue Origin lands rocket 🚀, GPT-5.1 for devs 👨‍💻 

**Link:** https://tldr.tech/tech/2025-11-14


**Content Summary:**

Stability or and innovation in payments technology (Sponsor)
Why pick one?
With Marqeta, launch payments experiences without choosing between innovation and scale.
Marqeta
combines the scale and reliability of proven payments infrastructure with the flexibility and innovation of a modern platform—so you can move faster, reduce risk, and grow with confidence.
From optimizing spend and cash flow to building seamless, rewards-driven customer experiences, Marqeta's solutions have you covered. When i...

---


### GPT-5.1 🤖, Waymo hits highways 🚗, Homebrew 5 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-13


**Content Summary:**

Your fast path to production MCP (Sponsor)
Gram is the MCP cloud.
Create, host, and scale MCP servers
without the hassle.
Create an agent tool library by defining tools with our lightweight TypeScript framework, importing your APIs, or uploading an existing MCP server. Curate tools into custom toolsets and deploy them as MCP servers.
MCP servers hosted on
Gram
work out of the box with your favorite MCP clients and agent frameworks: Claude, Cursor, OpenAI, Langchain, and more. Scale from zero to ...

---


### iPhone Air flops 📱, Anthropic OpenAI financials leak 💰, becoming a compiler engineer 👨‍💻

**Link:** https://tldr.tech/tech/2025-11-11


**Content Summary:**

Goodbye low test coverage and slow QA cycles (Sponsor)
Bugs sneak out when less than 80% of user flows are tested before shipping. However, getting that kind of coverage (and staying there) is hard and pricey for any team.
QA Wolf's
AI-native solution provides high-volume, high-speed test coverage for web and mobile apps, reducing your organization's QA cycle to minutes.
They can get you:
80% automated E2E test coverage in weeks
—not years
Unlimited parallel test runs
24-hour maintenance and on-...

---


### MSFT OpenAI docs leak 📄, GPT-5.1 🤖, Anthropic’s $50B Bet 💰

**Link:** https://tldr.tech/ai/2025-11-13


**Content Summary:**

Get access to the most performant Kimi K2 Thinking API (Sponsor)
This week, Baseten released Kimi K2 Thinking on Model APIs. Kimi K2 Thinking rivals the leading closed-source agentic models and is engineered for complex reasoning and agentic workflows.With Baseten's API you can get an LLM that is smarter, faster and cheaper. The Kimi K2 Thinking API is built for production workloads with high uptime, scalability, and performance stability:
🧨 Blistering TTFT at 0.3 seconds
⚡140+ tokens per second...

---


### ChatGPT Group Chats 💬, growing an RL environment 🌍, ElevenLabs Scribe v2 🗣

**Link:** https://tldr.tech/ai/2025-11-12


**Content Summary:**

100 prompts for Notion Agents (Sponsor)
Not sure what you can do with Notion Agents? Here are
100 ideas
to get you started...
🐾 This
collection of outcome-oriented prompts
comes with “Agent Steps” that show exactly how an Agent will execute and what it will produce (e.g., dashboards, databases, reports).
🗂️ It's organized by function, so you can find the exact use case you want to solve for (analytics, strategy, event planning, CX...) and test the prompts instantly.
🔌 Connect other data sources ...

---


### Grok Code Remote 👨‍💻 , GPT-5.1 on OpenRouter 🤖, Moonshot AI AMA 💬

**Link:** https://tldr.tech/ai/2025-11-11


**Content Summary:**

Airia: Enterprise AI Orchestration — Agents, Integrations, Workflows, and Governance (Sponsor)
You want AI to become part of your organizational DNA - and that means enabling every department to build out their own use cases, without IT gatekeepers standing in the way. But it shouldn't mean an ungoverned free-for-all.
Airia is the
“let's get serious about AI adoption” platform
. Rapidly prototype, deploy, and manage AI agents that transform workflows across your organization - without sacrificin...

---


## 📰 From Unknown


### GPT-5.1: A smarter, more conversational ChatGPT

**Community Score:** 513 upvotes

**Link:** https://openai.com/index/gpt-5-1/

---


### Britain's railway privatization was an abject failure

**Community Score:** 417 upvotes

**Link:** https://www.rosalux.de/en/news/id/53917/britains-railway-privatization-was-an-abject-failure


**Content Summary:**

Essay | 10/03/2025 Economic / Social Policy - Rosalux International - UK / Ireland - Commons / Social Infrastructure Britain’s Railway Privatization Was an Abject Failure Sold off in the 1990s, the UK’s railways are returning to public hands — but at what cost? Information Author Gareth Dennis , A commuter train waits to leave the station somewhere in London, 18 May 2023. Photo: IMAGO / Pond5 Images Liberalization of the railways has been a key tenet of European transport policy since the early ...

---


### Llmdeathcount.com

**Link:** https://llmdeathcount.com/

---


### I implemented an ISO 42001-certified AI Governance program in 6 months

**Link:** https://beabytes.com/iso42001-certified-ai-governance/

---


### Trellis AI (YC W24) Is Hiring: Streamline access to life-saving therapies

**Link:** https://www.ycombinator.com/companies/trellis-ai/jobs/f4GWvH0-forward-deployed-engineer-full-time

---


### AI World Clocks

**Link:** https://clocks.brianmoore.com/


&quot;Every minute, a new clock is rendered by nine different AI models.&quot;

---


### Strap Rail

**Link:** https://www.construction-physics.com/p/strap-rail

---


### Streaming AI agent desktops with gaming protocols

**Link:** https://blog.helix.ml/p/technical-deep-dive-on-streaming

---


### A new Google model is nearly perfect on automated handwriting recognition

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### An Antivenom Cocktail, Made by a Llama

**Link:** https://www.asimov.press/p/broad-antivenom

---


### AI World Clocks

**Community Score:** 1255 upvotes

**Link:** https://clocks.brianmoore.com/


**Content Summary:**

? × About AI World Clocks Every minute, a new clock is displayed that has been generated by nine different AI models. Each model is allowed 2000 tokens to generate its clock. Here is its prompt: Create HTML/CSS of an analog clock showing ${time}. Include numbers (or numerals) if you wish, and have a CSS animated second hand. Make it responsive and use a white background. Return ONLY the HTML/CSS code with no markdown formatting. Created by Brian Moore . You can also follow him on Instagram . Ide...

---


### A new Google model is nearly perfect on automated handwriting recognition

**Community Score:** 438 upvotes

**Link:** https://generativehistory.substack.com/p/has-google-quietly-solved-two-of

---


### Show HN: Pegma, the free and open-source version of the classic Peg solitaire

**Link:** https://pegma.vercel.app


Discover Pegma, the free and open-source version of the classic Peg solitaire game! Pegma offers a clean, minimal design and smooth gameplay across multiple platforms.<p>Key features:<p>Fully open-source code available on GitHub, inviting community contributions and transparency<p>Custom-designed font created by the developer to enhance the game’s unique style<p>Cross-platform support: play on iOS, Android, or directly in your web browser<p>Lightweight, intuitive interface that stays true to the timeless puzzle mechanics<p>Try it now:<p>Website: <a href="https:&#x2F;&#x2F;pegma.vercel.app" rel="nofollow">https:&#x2F;&#x2F;pegma.vercel.app</a><p>GitHub: <a href="https:&#x2F;&#x2F;github.com&#x2F;khlebobul&#x2F;pegma" rel="nofollow">https:&#x2F;&#x2F;github.com&#x2F;khlebobul&#x2F;pegma</a><p>App Store: <a href="https:&#x2F;&#x2F;apps.apple.com&#x2F;ru&#x2F;app&#x2F;pegma-peg-solitaire&#x2F;id6754343848">https:&#x2F;&#x2F;apps.apple.com&#x2F;ru&#x2F;app&#x2F;pegma-peg-solitaire&#x2F;id67543438...</a><p>Google Play: <a href="https:&#x2F;&#x2F;play.google.com&#x2F;store&#x2F;apps&#x2F;details?id=com.khlebobul.pegma">https:&#x2F;&#x2F;play.google.com&#x2F;store&#x2F;apps&#x2F;details?id=com.khlebobul....</a><p>If you appreciate open-source projects and classic brain teasers, Pegma is definitely worth checking out!

---


### Nano Banana can be prompt engineered for nuanced AI image generation

**Link:** https://minimaxir.com/2025/11/nano-banana-prompts/

---


### Disrupting the first reported AI-orchestrated cyber espionage campaign

**Link:** https://www.anthropic.com/news/disrupting-AI-espionage

---


### Launch HN: Tweeks (YC W25) – Browser extension to deshittify the web

**Link:** https://www.tweeks.io/onboarding


Hey HN! We’re Jason &amp; Matt and we’re building Tweeks (<a href="https:&#x2F;&#x2F;tweeks.io">https:&#x2F;&#x2F;tweeks.io</a>), a browser extension that lets you modify any website in your browser to add functionality, filter&#x2F;highlight, re-theme, reorganize, de-clutter, etc. If you’ve used Violentmonkey&#x2F;Tampermonkey, Tweeks is like a next‑generation userscript manager. Instead of digging through selectors and hand‑writing custom JS&#x2F;CSS, describe what you want in natural language and Tweeks plans + generates your edits and applies them.<p>The modern web is so full of clutter and junk (banners, modals, feeds, and recommendations you didn’t ask for). Even a simple google search is guarded by multiple ads, an AI overview, a trending searches module, etc. before you even see the first real blue link.<p>Every day there&#x27;s a new Lovable-like product (make it simple to build your own website&#x2F;app) or a new agentic browser (AI agents click around and browse the web for you), but we built Tweeks to serve the middle ground: most of our time spent on the web is on someone else&#x27;s site (not our own), and we don&#x27;t want to offload everything to an agentic browser. We want to be able to shape the entire web to our own preferences as we browse.<p>I spent years working on recommendation systems and relevance at Pinterest, and understand how well-meaning recommendations and A&#x2F;B tests can lead to website enshittification. No one sets out to make UX worse, but optimizing for an “average” user is not the same as optimizing for each individual user.<p>I’ve also been hacking “page fixers” as long as I can remember: remove a login wall here, collapse cookie banners there, add missing filters&#x2F;highlights (first with F12&#x2F;inspect element and eventually graduated to advanced GreaseMonkey userscripts). Tweeks started as a weekend prototype that turned simple requests into page edits but unexpectedly grew into something people kept asking to share. We hope you’ll like it too!<p>How it works: Open the Tweeks extension, type your request (e.g. “hide cookie banners and add a price&#x2F;quality score”), and submit. Upon submission, the page structure is captured, an AI agent reviews the structure, plans changes, and returns deterministic transformations (selectors, layout tweaks, styles, and small scripts) that run locally. Your modifications persist across page loads and can be enabled&#x2F;disabled, modified, and shared.<p>Here are a bunch of one‑shot examples from early users:<p><i>Youtube</i>: Remove Youtube Shorts. Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=aL7i89BdO9o" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=aL7i89BdO9o</a>. Try it yourself: <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;bcd8bc32b8034b79a78a8564">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;bcd8bc32b8034b79a78a8564</a><p><i>Hacker News</i>: Filter posts by title&#x2F;url or points&#x2F;comments, modify header and text size. Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=cD5Ei8bMmUk" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=cD5Ei8bMmUk</a>. Try it yourself: <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;97e72c6de5c14906a1351abd">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;97e72c6de5c14906a1351abd</a> (filter), <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;6f51f96c877a4998bda8e781">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;6f51f96c877a4998bda8e781</a> (header + text).<p><i>LinkedIn</i>: Keep track of cool people (extracts author data and send a POST request to a server). Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=WDO4DRXQoTU" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=WDO4DRXQoTU</a><p><i>Reddit</i>: Remove sidebar and add a countdown timer that shows a blocking modal when time is up. Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=kBIkQ9j_u94" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=kBIkQ9j_u94</a>. Try it yourself: <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;e1daa0c5edd441dca5a150c8">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;e1daa0c5edd441dca5a150c8</a> (sidebar), <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;c321c9b6018a4221bd06fdab">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;c321c9b6018a4221bd06fdab</a> (timer).<p><i>New York Times Games</i>: Add a Strands helper that finds all possible words. Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=hJ75jSATg3Q" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;watch?v=hJ75jSATg3Q</a>. Try it yourself: <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;7a955c910812467eaa36f569">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;7a955c910812467eaa36f569</a><p><i>Theming</i>: Retheme Google to be a 1970s CLI terminal. Demo: <a href="http:&#x2F;&#x2F;youtube.com&#x2F;shorts&#x2F;V-CG5CbYJb4" rel="nofollow">http:&#x2F;&#x2F;youtube.com&#x2F;shorts&#x2F;V-CG5CbYJb4</a> (oops sorry a youtube short snuck back in there). Try it yourself: <a href="http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;8c8c0953f6984163922c4da7">http:&#x2F;&#x2F;tweeks.io&#x2F;share&#x2F;script&#x2F;8c8c0953f6984163922c4da7</a>.<p>We just opened access at <a href="https:&#x2F;&#x2F;tweeks.io">https:&#x2F;&#x2F;tweeks.io</a>. It’s currently free, but each use costs tokens so we&#x27;ll likely need to cap usage to prevent abuse. We&#x27;re more interested in early feedback than your money, so if you manage to hit the cap, message us at contact@trynextbyte.com or <a href="https:&#x2F;&#x2F;discord.gg&#x2F;WucN6wpJw2" rel="nofollow">https:&#x2F;&#x2F;discord.gg&#x2F;WucN6wpJw2</a>, tell us how you&#x27;re using it&#x2F;what features you want next, and we&#x27;ll happily reset it for you.<p>Btw if you do anything interesting with it, feel free to make a shareable link (go to ‘Library’ and press ‘share’ after generating) and include it in the comments below. It’s fun to see the different things people are coming up with!<p>We&#x27;re rapidly shipping improvements and would love your feedback and comments. Thanks for reading!

---


### Ask HN: Is building for the web even worth it now?

**Link:** https://news.ycombinator.com/item?id=45924891


Of late, I’ve found my relationship with internet changing. I was here back in the early 2000s and it has always been the first place I go to for entertainment, advice, and work<p>But increasingly, I find myself completely disengaged with the internet. Every time I see a text post, I start asking myself: is this even a real person? Am I just talking to a bot?<p>Every time I see a yellow-tinged image on any of my social media feeds, I mentally switch off. I know it was made by AI and I just find it hard to engage with anything AI-made, no matter how good<p>Same for any AI video that pops up on my feed. It just doesn’t make me scroll past it, it makes me question why am I even here and I end up leaving<p>I know I can’t be the only one. I used to love the internet because it was one place where I could engage with people from all over the world. But now, it feels like I just spend half my energy on figuring out which one is real, which one is AI<p>The line will eventually blur and as a late 30s guy, I really don’t want to spend any more of my time on earth talking to a bot<p>As someone who used to create and build for the web, I find myself increasingly disengaged and discouraged. I’m pouring into a rapidly emptying cup<p>Anyone else feel the same way?

---


### SlopStop: Community-driven AI slop detection in Kagi Search

**Link:** https://blog.kagi.com/slopstop

---


### Show HN: DBOS Java – Postgres-Backed Durable Workflows

**Link:** https://github.com/dbos-inc/dbos-transact-java


Hi HN - I’m Peter, here with Harry (devhawk), and we’re building DBOS Java, an open-source Java library for durable workflows, backed by Postgres.<p><a href="https:&#x2F;&#x2F;github.com&#x2F;dbos-inc&#x2F;dbos-transact-java" rel="nofollow">https:&#x2F;&#x2F;github.com&#x2F;dbos-inc&#x2F;dbos-transact-java</a><p>Essentially, DBOS helps you write long-lived, reliable code that can survive failures, restarts, and crashes without losing state or duplicating work. As your workflows run, it checkpoints each step they take in a Postgres database. When a process stops (fails, restarts, or crashes), your program can recover from those checkpoints to restore its exact state and continue from where it left off, as if nothing happened.<p>In practice, this makes it easier to build reliable systems for use cases like AI agents, payments, data synchronization, or anything that takes hours, days, or weeks to complete. Rather than bolting on ad-hoc retry logic and database checkpoints, durable workflows give you one consistent model for ensuring your programs can recover from any failure from exactly where they left off.<p>This library contains all you need to add durable workflows to your program: there&#x27;s no separate service or orchestrator or any external dependencies except Postgres. Because it&#x27;s just a library, you can incrementally add it to your projects, and it works out of the box with frameworks like Spring. And because it&#x27;s built on Postgres, it natively supports all the tooling you&#x27;re familiar with (backups, GUIs, CLI tools) and works with any Postgres provider.<p>If you want to try it out, check out the quickstart:<p><a href="https:&#x2F;&#x2F;docs.dbos.dev&#x2F;quickstart?language=java" rel="nofollow">https:&#x2F;&#x2F;docs.dbos.dev&#x2F;quickstart?language=java</a><p>We&#x27;d love to hear what you think! We’ll be in the comments for the rest of the day to answer any questions.

---


### LLMs are steroids for your Dunning-Kruger

**Community Score:** 128 upvotes

**Link:** https://bytesauna.com/post/dunning-kruger

---
