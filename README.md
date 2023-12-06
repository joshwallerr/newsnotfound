# NewsNotFound Article Creation 📰

This is the entire source code for NewsNotFound's article generation process. 

## December 2023 Update

NewsNotFound has been temporarily shut down as of December 5th 2023.

All costs for this project were paid for through personal funding.

My personal financial situation has taken a hit recently, so i can no longer afford to keep the project running.

I do plan on bringing it back as soon as I can, with a new UI and updated functionality.

Whilst i search for a job, I'm working on a few other (less expensive) projects in the background:
- [DocDecoder](https://chromewebstore.google.com/detail/docdecoder-summarize-web/pbcajhinmaijadgdofjohponnggbkjhh?hl=en)
- [Neversleep](https://neversleepclothing.com/products/genesis)

I would be incredibly grateful for any support you can offer, whether it's trying out these projects, providing feedback, or even spreading the word.

Your support has been the backbone of NewsNotFound, and I am very thankful for the community that has grown around it.

I look forward to bringing back NewsNotFound better than ever.

Josh

## What is NewsNotFound?

NewsNotFound was a news website located at https://newsnotfound.com.

We want to build the most unbiased news platform on the internet.

![App Screenshot](https://cdn.shopify.com/s/files/1/0673/2005/4067/files/nnfsc.jpg?v=1701863723)

Our mission is to lead the way in AI journalism by providing completely neutral and unbiased news articles that can be governed by the public.

We believe this is the key to a genuine, trustworthy and transparent news source, void of the possibility of corruption.

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

## CRON Schedule

| Expression   | Translation                      |            Command                  |
|--------------|----------------------------------|:-----------------------------------:|
| 0 * * * *    | Every hour                       | python3 load_headlines.py           |
| 0 */6 * * *  | Every 6 hours                    | python3 app.py world                |
| 0 11 * * *   | At 11:00                         | python3 app.py science              |
| 15 */6 * * * | At minute 15 past every 6th hour | python3 app.py uk                   |
| 30 */6 * * * | At minute 30 past every 6th hour | python3 app.py us                   |
| 36 */8 * * * | At minute 36 past every 8th hour | python3 app.py teesside             |
| 1 8 * * *    | At 08:01                         | python3 app.py tyneside             |
| 3 8 * * *    | At 08:03                         | python3 app.py sunderland           |
| 6 8 * * *    | At 08:06                         | python3 app.py worcester            |
| 9 8 * * *    | At 08:09                         | python3 app.py bedford              |
| 12 8 * * *   | At 08:12                         | python3 app.py norwich              |
| 15 8 * * *   | At 08:15                         | python3 app.py west_yorkshire       |
| 18 8 * * *   | At 08:18                         | python3 app.py plymouth             |
| 0 7 * * *    | At 07:00                         | python3 app.py india                |
| 0 14 * * *   | At 14:00                         | python3 app.py brazil               |
| 0 9 * * *    | At 09:00                         | python3 app.py turkey               |
| 0 10 * * *   | At 10:00                         | python3 app.py uk_politics          |
| 15 11 * * *  | At 11:15                         | python3 app.py technology           |
| 25 11 * * *  | At 11:25                         | python3 app.py finance_energy_solar |
| 35 11 * * *  | At 11:30                         | python3 app.py finance_energy_wind  |
| 45 11 * * *  | At 11:35                         | python3 app.py finance_energy_gas   |
| 55 11 * * *  | At 11:40                         | python3 app.py finance_energy_hydro |
| 30 16 * * *  | At 16:30                         | python3 app.py china                |
| 50 12 * * *  | At 12:50                         | python3 app.py finance_commodities  |
| 10 13 * * *  | At 13:10                         | python3 app.py uk_agriculture       |
| 20 13 * * *  | At 13:20                         | python3 app.py us_agriculture       |
| 10 14 * * *  | At 14:10                         | python3 app.py crypto               |
| 10 16 * * *  | At 16:10                         | python3 app.py us_politics          |
| 10 17 * * *  | At 17:10                         | python3 app.py uk_construction      |
| 20 17 * * *  | At 17:20                         | python3 app.py uk_education         |
| 30 13 * * *  | At 13:30                         | python3 app.py ai                   |
| 10 15 * * *  | At 15:10                         | python3 app.py cybersecurity        |

## Countribution

Any and all contributions are welcome and massively appreciated.

Please use the [Issues](https://github.com/joshwallerr/newsnotfound/issues) tab for tracking feature requests and bugs.

We use [GitHub Discussions](https://github.com/joshwallerr/newsnotfound/discussions) for general questions and conversations about this project.

## Contact

For all enquiries, please [contact us here](https://newsnotfound.com/contact/).
