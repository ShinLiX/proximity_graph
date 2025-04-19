import json
import pandas as pd
from collections import Counter

# Path to the Yelp business dataset
file_path = '/Users/wangyaoyi/Desktop/data/yelp_academic_dataset_business.json'

# Use a Counter to count the number of restaurants in each city in Alberta (AB)
city_counter = Counter()

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        business = json.loads(line)
        state = business.get('state')
        city = business.get('city')
        categories = business.get('categories')

        # Filter: Only businesses in Alberta (AB) with 'Restaurants' in categories
        if state == 'AB' and city and categories:
            if 'Restaurants' in categories:
                city_counter[city.strip().lower()] += 1  # Normalize city name to lowercase and strip spaces

# Convert the city counts to a DataFrame and sort by restaurant count
city_df = pd.DataFrame(city_counter.items(), columns=['city', 'restaurant_count'])
city_df = city_df.sort_values(by='restaurant_count', ascending=False)

# Save results to a CSV file
city_df.to_csv('ab_restaurant_city_counts.csv', index=False)

# Print the top 10 cities with the most restaurants
print("\n🍁 Top AB Cities by Restaurant Count:")
print(city_df.head(10))
print(f"\n✅ Saved restaurant counts for {len(city_df)} cities in Alberta to 'ab_restaurant_city_counts.csv'")