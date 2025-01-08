+++
title = "LLM Benchmarks Are Not Trustworthy"
date = 2025-01-08T17:20:47-05:00
images = []
tags = ['tech', 'ai', 'llms', 'science']
categories = []
draft = false
+++

If you believe OpenAI's marketing, their LLM products are automating an increasingly large fraction of software engineering jobs. They substantiate this, in part, by citing how their products perform against various LLM benchmarks. [Here's an example](https://openai.com/index/introducing-swe-bench-verified/) where OpenAI touts GPT-4o's performance on a benchmark called [SWE-bench](https://www.swebench.com/index.html):

> Each sample in the SWE-bench test set is created from a resolved GitHub issue in one of 12 open-source Python repositories on GitHub. Each sample has an associated pull request (PR), which includes both the solution code and unit tests to verify code correctness.
> 
> [...]
> 
> We found that GPT-4o’s performance on the best-performing scaffold reaches 33.2% on SWE-bench Verified, more than doubling its score of 16% on the original SWE-bench.

These benchmarks differ a bit, but most of them are structurally equivalent:

- They have a ~static list of problem statements. Sometimes these are coding problems, sometimes they're math problems.
- They feed each problem statement to the LLM, and take the response.
- They take each response, and compare it to a static list of known correct answers for each problem.
- Finally, they calculate what percentage of questions the LLM got right.

Some benchmarks get a little fancy - [FrontierMath](https://epoch.ai/frontiermath) rates how "hard" the math problems are - but they're all roughly shaped like this. Some benchmarks, like SWE-bench, publish all the problem statements publicly. Some, like, FrontierMath, don't, but critically, _have to send the problems to OpenAI to evaluate its models_.

Now imagine for a second that you're an LLM company, trying to cheat at a benchmark. It's obvious what you do, right? You take the problem statements and _put them in your model_ so that when it sees one of these problems, it is overwhelmingly likely to return the answer the examiner is looking for. And this is definitely cheating; the whole point of a benchmark is to try to evaluate something under normal operation, and you're deliberately making your model behave differently when it's being tested. It's the moral equivalent of [Volkswagen programming its car engines to emit fewer emissions when being tested by regulators.](https://en.wikipedia.org/wiki/Volkswagen_emissions_scandal)

When a benchmark has been cheated in this way, you see the LLM perform extremely well in-sample (on questions it's been trained on), but its performance dramatically decreases out-of-sample. And this is the shape of what's happened with SWE-bench; some folks at York University discovered that ~94% of SWE-bench's problems came from data that existed during the training of e.g. OpenAI's GPT-4o. [When they restricted the dataset, GPT-4o's performance dropped by ~90%, to a success rate of 3.8%:](https://arxiv.org/pdf/2410.06992)

> In addition, over 94% of the issues were created before LLM’s knowl-
edge cutoff dates, posing potential data leakage issues.
> 
> [...]
> 
> After carefully analyzing the passed instances from the SWE-Agent + GPT-4 model with the new dataset, SWE-Bench+, we observed a decline in the pass rate, dropping from 3.97% (as seen on the refined SWE-Bench) to a resolution rate of 0.55%. We further evaluated SWE-RAG + GPT-4, SWE-RAG + GPT-3.5, and AutoCodeRover + GPT-4o models on the new dataset to verify our findings, where the resolution rates of the models drop significantly, which are 0.73%, 0.55%, and 3.83%, respectively.

To be clear, I'm not claiming that OpenAI is knowingly cheating on benchmarks. I don't think they have to be, in order for this to happen. They're a private company with a closed model, and internally, they're hoovering up as much data as they can possibly get. But I do think that, in the current environment, you absolutely have to view LLM benchmarks from a position of default-distrust, _especially_ given the amounts of money sloshing around in the AI industry.