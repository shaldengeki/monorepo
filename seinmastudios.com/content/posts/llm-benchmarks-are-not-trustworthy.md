+++
title = "LLM benchmarks like SWE-bench are not trustworthy"
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

Some benchmarks get a little fancy - [FrontierMath](https://epoch.ai/frontiermath) rates how "hard" the math problems are - but they're all roughly shaped like this. Some benchmarks, like SWE-bench, publish all the problem statements publicly. Some, like, FrontierMath, don't, but critically, have to send the problems to OpenAI to evaluate its models.

Now imagine for a second that you're an LLM company, trying to make your model better at coding or math. Obviously you're going to scrape Github and include its code, issues, and PRs in your training set. And obviously you're going to look at math problems your users are solving, and use that in future training runs. The upshot of this is that the vast majority of public and non-public benchmarks' question sets are in your training set.

When a benchmark has been undermined in this way, you see the LLM perform extremely well in-sample (on questions it's been trained on), but its performance dramatically decreases out-of-sample (like, when it actually runs in the real world). That's why avoiding this is, like, ML 101; training on your test set means benchmarks no longer give you an accurate picture of how good your model is.

And this is the shape of what's happened with SWE-bench; some folks at York University discovered that ~94% of SWE-bench's problems came from data that existed during the training of e.g. OpenAI's GPT-4o. [When they restricted the dataset, GPT-4o's performance dropped by ~90%, to a success rate of 3.8%:](https://arxiv.org/pdf/2410.06992)

> In addition, over 94% of the issues were created before LLM’s knowl-
edge cutoff dates, posing potential data leakage issues.
> 
> [...]
> 
> After carefully analyzing the passed instances from the SWE-Agent + GPT-4 model with the new dataset, SWE-Bench+, we observed a decline in the pass rate, dropping from 3.97% (as seen on the refined SWE-Bench) to a resolution rate of 0.55%. We further evaluated SWE-RAG + GPT-4, SWE-RAG + GPT-3.5, and AutoCodeRover + GPT-4o models on the new dataset to verify our findings, where the resolution rates of the models drop significantly, which are 0.73%, 0.55%, and 3.83%, respectively.

With FrontierMath, [OpenAI's o1 scored less than 2%](https://arxiv.org/abs/2411.04872) when the benchmark was released in November 2024. At the end of December, [OpenAI announced that o3 solved 25% of the problems.](https://techcrunch.com/2024/12/20/openai-announces-new-o3-model/) (Interestingly, the public hasn't been given access to the model.)

To be clear, I'm not claiming that OpenAI is knowingly cheating on benchmarks. I don't think they have to be, in order for this to happen. They're a private company with a closed model, and internally, they're hoovering up as much data as they can possibly get. This leakage is just what I'd expect to happen by default.

But I do think that you absolutely have to view LLM benchmarks from a position of default-distrust, _especially_ given the amounts of money sloshing around in the AI industry. That's what's required for honest science. The real question, in my mind, is whether or when we'll see autonomous software engineering, or math research, being done anywhere.

Thanks to Guanqing Ou for feedback on this post.