# NewsNotFound Article Creation 📰

This is the entire source code for NewsNotFound's article generation process. 

## What is NewsNotFound?

NewsNotFound is a news website located at https://newsnotfound.com.

![App Screenshot](http://newsnotfound.com/wp-content/uploads/2023/04/1677003418639-jpeg-e1682077026373.webp)

Our mission is to lead the way in AI journalism by providing completely neutral and unbiased news articles that can be governed by the public.

We believe this is the key to a genuine, trustworthy and transparent media landscape, void of the possibility of corruption.

## Project Whitepaper

[Click here to view our whitepaper](https://newsnotfound.com/whitepaper/)


# Process Overview 🔍

The article creation process can be broken down into the following stages:

- Scrape and load headlines
- Cluster related headlines
- Choose story
- Scrape facts
- Generate brief
- Write article
- Bias checker (temporarily disabled, see NOTE)
- Format article
- Generate headline
- Structure article
- Generate cover image

**NOTE:** The bias checker has been temporarily removed as of 19/04/23. This was implemented when we used GPT-3 for generating the article, however GPT-4 seems to be much more consistent at producing unbiased articles. Using the bias checker with GPT-4 was harming the quality of the article, so it is currently pending improvements.

## Sources

See [`load_headlines.py`](https://github.com/joshwallerr/newsnotfound/blob/main/load_headlines.py) for each category's sources list.

## Countribution

Any and all contributions are welcome and massively appreciated.

Please use the [Issues](https://github.com/joshwallerr/newsnotfound/issues) tab for tracking feature requests and bugs.

We use [GitHub Discussions](https://github.com/joshwallerr/newsnotfound/discussions) for general questions and conversations about this project.

## Contact

For all enquiries, please [contact us here](https://newsnotfound.com/contact/).