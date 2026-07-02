# Application Answers — Anthropic (via PhD Source) · Research Engineer / Scientist, Tokens

**Apply here:** https://www.linkedin.com/jobs/view/4431311964/ (agency posting via PhD Source; responses managed off LinkedIn — capture the full agency JD before applying)

## Standard fields
- Salary expectation: Targeting $130k+ base; flexible depending on total compensation and scope. (Single-number forms: 130000)
- Work authorization: U.S. citizen. Authorized to work in the U.S. without sponsorship, now or in the future. Sponsorship not required.
- Notice period: 2 weeks from offer acceptance.
- Phone: 952-303-1045 · LinkedIn: linkedin.com/in/kanu-madhok · GitHub: github.com/kmadhok

## Why Anthropic
I'll be straight about fit: I'm an applied AI engineer, not a pretraining or tokenization researcher, and the Tokens team is a research seat. What I'd bring is a builder's version of the same rigor — I use Claude and the Anthropic API daily to ship production agents, so I know the model's behavior from the outside in a way that's useful when you're deciding what actually matters downstream of a tokenization change. My research-adjacent work is real but honest in scope: a UChicago MS in Applied Data Science, a controlled multi-LLM experiment under the Data & Democracy initiative with 500+ participants and real A/B arms, and a lot of golden-set evaluation design in production. I'd only want this seat if there's a version of it that values strong LLM-systems engineering and experimental discipline alongside the research core; if the team needs a published tokenization/pretraining researcher, I'm not that, and I'd rather say so than oversell.

## Relevant project
Persona-driven multi-LLM donation experiment (UChicago, Data & Democracy): I built a persona-conditioned chatbot across OpenAI and Gemini for a 500+ participant study on whether an LLM can shift a politically-charged donation decision. It was a real experimental design — treatment and control arms, statistical significance as the gate, and a 15% persuasion lift as the result. Using two models was a deliberate variance control: if both produced the same lift, the effect was the chatbot and not a single-model artifact. That's the closest thing I have to research rigor — controlled experimentation with clean attribution.

Evaluation architecture in production: across my Walmart agents I run layered evals ordered cheapest-to-most-expensive — deterministic rule checks, then a golden-query regression suite, then human review — and I think about eval as a decaying target, since a static golden set stops reflecting the data over time. It's engineering, not frontier research, but it's the mindset of measuring a model's behavior rigorously rather than trusting it.

## Note for Kanu
Per the filed JD, this is a significant reach (frontier ML research vs. applied agent-building) and flagged as likely a pass / low-priority. Packet built for visibility; the "Why" is drafted to be honest about the gap rather than to oversell.
