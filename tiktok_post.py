from social import get_tiktok_story_caption, generate_tiktok_video
from scrape import headlines_links, get_article_images

nnf_hl = headlines_links(['https://newsnotfound.com/'])
three_headlines = list(nnf_hl.keys())[:3]

story1 = three_headlines[0]
story2 = three_headlines[1]
story3 = three_headlines[2]
funny_story, tiktok_caption = get_tiktok_story_caption()

print(story1)
print(story2)
print(story3)
print(funny_story)
print(tiktok_caption)

# Scrape images from site - first 3 in main banner block

three_links = list(nnf_hl.values())[:3]
img_links = get_article_images(three_links)
print(img_links)

img_url1 = img_links[0]
# Skipping img 2 because it does not have a place in the video template
img_url3 = img_links[2]

video = generate_tiktok_video(story1, story2, story3, funny_story, img_url1, img_url3)
print(video)


# TODO
# Failed because no funny_Story was added? - load data into tiktok.db and try again.
# Figure out why images didn't upload properly.
# Figure out why text resize didn't work as intended.