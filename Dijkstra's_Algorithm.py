import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from geopy.distance import geodesic

# Load restaurant data
restaurants = pd.read_csv('sherwoodpark_restaurants.csv')

# Convert names to title case for better readability
restaurants['name'] = restaurants['name'].str.title()


# Create a distance matrix (in meters) between all restaurants
def create_distance_matrix(df):
    n = len(df)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                loc1 = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
                loc2 = (df.iloc[j]['latitude'], df.iloc[j]['longitude'])
                dist_matrix[i,j] = geodesic(loc1, loc2).meters
    return dist_matrix

distance_matrix = create_distance_matrix(restaurants)

# Create graph
G = nx.Graph()

# Add nodes with restaurant attributes
for idx, row in restaurants.iterrows():
    G.add_node(idx, 
               name=row['name'],
               stars=row['stars'],
               review_count=row['review_count'],
               latitude=row['latitude'],
               longitude=row['longitude'])

# Add weighted edges
for i in range(len(restaurants)):
    for j in range(i+1, len(restaurants)):
        G.add_edge(i, j, weight=distance_matrix[i,j])

print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

# Find the most reviewed restaurant (central node)
central_node = restaurants['review_count'].idxmax()
central_name = restaurants.loc[central_node, 'name']
print(f"Central hub: {central_name} with {restaurants.loc[central_node, 'review_count']} reviews")

# Calculate distances from central node
central_distances = nx.single_source_dijkstra_path_length(G, central_node, weight='weight')

# Add distances to dataframe
restaurants['distance_from_central'] = restaurants.index.map(central_distances)

# Get top 3 most reviewed restaurants
top_3_nodes = restaurants.nlargest(3, 'review_count').index

# Calculate distances from each hub
hub_distances = {}
for node in top_3_nodes:
    hub_name = G.nodes[node]['name']
    hub_distances[hub_name] = nx.single_source_dijkstra_path_length(G, node, weight='weight')
    restaurants[f'distance_from_{hub_name.replace(" ", "_").lower()}'] = restaurants.index.map(hub_distances[hub_name])


# Plot restaurant locations
plt.figure(figsize=(12, 8))
sns.scatterplot(data=restaurants, x='longitude', y='latitude', 
                size='review_count', hue='stars', 
                sizes=(20, 200), palette='viridis', alpha=0.7)

# Mark central hubs
for node in top_3_nodes:
    plt.scatter(restaurants.loc[node, 'longitude'], 
               restaurants.loc[node, 'latitude'],
               s=300, marker='*', c='red', edgecolor='black')
    
plt.title('Spatial Distribution of Restaurants in Sherwood Park\n(Size=Review Count, Color=Star Rating)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Correlation analysis
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Distance vs Stars
sns.regplot(data=restaurants, x='distance_from_central', y='stars', ax=axes[0])
axes[0].set_title('Distance from Central Hub vs. Star Rating')
axes[0].set_xlabel('Distance from Central Hub (meters)')
axes[0].set_ylabel('Star Rating')

# Distance vs Review Count
sns.regplot(data=restaurants, x='distance_from_central', y='review_count', ax=axes[1])
axes[1].set_title('Distance from Central Hub vs. Review Count')
axes[1].set_xlabel('Distance from Central Hub (meters)')
axes[1].set_ylabel('Review Count')

plt.tight_layout()
plt.show()

# Calculate correlation coefficients
pearson_stars = stats.pearsonr(restaurants['distance_from_central'], restaurants['stars'])
pearson_reviews = stats.pearsonr(restaurants['distance_from_central'], restaurants['review_count'])

print(f"Pearson correlation between distance and stars: r={pearson_stars[0]:.3f}, p={pearson_stars[1]:.3f}")
print(f"Pearson correlation between distance and review count: r={pearson_reviews[0]:.3f}, p={pearson_reviews[1]:.3f}")

# Compare restaurants near vs far from central hub
median_distance = restaurants['distance_from_central'].median()
near_hub = restaurants[restaurants['distance_from_central'] <= median_distance]
far_hub = restaurants[restaurants['distance_from_central'] > median_distance]

print(f"\nNear hub (≤{median_distance:.0f}m) stats:")
print(f"  Average stars: {near_hub['stars'].mean():.2f} ± {near_hub['stars'].std():.2f}")
print(f"  Average reviews: {near_hub['review_count'].mean():.2f} ± {near_hub['review_count'].std():.2f}")

print(f"\nFar from hub (>{median_distance:.0f}m) stats:")
print(f"  Average stars: {far_hub['stars'].mean():.2f} ± {far_hub['stars'].std():.2f}")
print(f"  Average reviews: {far_hub['review_count'].mean():.2f} ± {far_hub['review_count'].std():.2f}")

