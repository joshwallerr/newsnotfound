from social import get_tiktok_story_caption, generate_tiktok_video, retrieve_tiktok_video, download_tiktok_video
from scrape import headlines_links, get_article_images
import json

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

video_data = generate_tiktok_video(story1, story2, story3, funny_story, img_url1, img_url3)
print(video_data)

video_id = video_data['videoId']
print(video_id)

retrieved_video_data = retrieve_tiktok_video(video_id)
retrieved_video_url = retrieved_video_data['url']

download_tiktok_video(retrieved_video_url)

# Now upload to TikTok - ask ChatGPT. Example prompt:
# I have a locally downloaded video in linux that I want to upload to tiktok via their API. The video is located at video/video.mp4. How can I upload the video to tiktok using python
