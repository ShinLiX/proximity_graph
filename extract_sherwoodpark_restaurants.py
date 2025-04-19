import json
import pandas as pd

# File path to Yelp dataset
file_path = 'yelp_academic_dataset_business.json'

# Store clean restaurant entries
restaurants = []

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        business = json.loads(line)

        # Filter for Sherwood Park, Alberta
        state = business.get('state')
        city = business.get('city')
        categories = business.get('categories')

        if state == 'AB' and city and city.lower().strip() == 'sherwood park':
            if categories and 'Restaurants' in categories:
                name = business.get('name')
                lat = business.get('latitude')
                lon = business.get('longitude')
                stars = business.get('stars')
                reviews = business.get('review_count')

                # Skip if any of the required fields are missing
                if all([name, lat, lon, stars is not None, reviews is not None]):
                    restaurants.append({
                        'name': name.strip().lower(),  # standardize name
                        'latitude': float(lat),
                        'longitude': float(lon),
                        'stars': float(stars),
                        'review_count': int(reviews)
                    })

# Convert to DataFrame
df = pd.DataFrame(restaurants)

# Check for remaining missing values
print("🧼 Missing values per column:\n", df.isnull().sum())

# Save the clean result
df.to_csv('sherwoodpark_restaurants.csv', index=False)
print(f"\n✅ Extracted {len(df)} restaurants in Sherwood Park. Saved as 'sherwoodpark_restaurants.csv'.")