import csv
import ast
import random
import os

def find_most_suitable_headlines(category):
    # Read related_headlines.csv
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'related_headlines.csv'), "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        category_index = header.index(category)
        all_related_headlines = [ast.literal_eval(row[category_index]) for row in reader if row[category_index]]

    # Read covered.csv
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covered.csv'), "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        covered_headlines = [row[0] for row in reader]

    def choose_headlines(headlines):
        headlines = sorted(headlines, key=lambda x: x[1], reverse=True)
        headlines = [x[0] for x in headlines if x[0] not in covered_headlines]
        return headlines[:3]

    def should_skip_list(headlines):
        covered_count = sum([1 for x in headlines if x[0] in covered_headlines])
        if len(headlines) > 2 and covered_count >= 2:
            return True
        if len(headlines) <= 2 and covered_count >= 1:
            return True
        return False

    # Filter out the lists that should be skipped
    valid_related_headlines = [x for x in all_related_headlines if not should_skip_list(x)]

    if valid_related_headlines:
        # Choose the most suitable list
        suitable_list = max(valid_related_headlines, key=lambda x: sum([y[1] for y in x]))

        # Exclude covered headlines and choose top 3 headlines
        chosen_headlines = choose_headlines(suitable_list)
    else:
        # Read headlines.csv
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'headlines.csv'), "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            category_index = header.index(category)
            all_headlines = [row[category_index] for row in reader if row[category_index]]

        # Choose a random headline that hasn't been covered
        random_headline = random.choice([x for x in all_headlines if x not in covered_headlines])
        chosen_headlines = [random_headline]

    for headline in chosen_headlines:
        if 'live briefing' in headline.lower():
            chosen_headlines.remove(headline)

    return chosen_headlines

# Example usage
# category = "us"
# result = find_most_suitable_headlines(category)
# print(result)