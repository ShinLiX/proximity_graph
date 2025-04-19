import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import itertools
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import seaborn as sns
from scipy.stats import pearsonr

# Load the CSV file
df = pd.read_csv("sherwoodpark_restaurants.csv")

# Initialize an undirected graph
G = nx.Graph()

# Add restaurant nodes with attributes
for idx, row in df.iterrows():
    G.add_node(idx, 
               name=row['name'], 
               pos=(row['latitude'], row['longitude']),
               stars=row['stars'], 
               review_count=row['review_count'])

# Set proximity threshold (500 meters)
proximity_threshold_m = 500

# Add edges between restaurants within the threshold distance
for i, j in itertools.combinations(df.index, 2):
    loc_i = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
    loc_j = (df.loc[j, 'latitude'], df.loc[j, 'longitude'])
    distance = geodesic(loc_i, loc_j).meters
    
    if distance <= proximity_threshold_m:
        G.add_edge(i, j, weight=distance)

# Add degree info to original DataFrame
df['degree'] = df.index.map(dict(G.degree()))

# Optional: Save the graph to file for Gephi
nx.write_gml(G, "proximity_graph_500m.gml")

# Show summary
print(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")


# Use longitude and latitude for layout (lon, lat = x, y)
pos = {node: (data['pos'][1], data['pos'][0]) for node, data in G.nodes(data=True)}

# Size and color settings
node_sizes = [5 + 2 * G.nodes[n]['review_count'] for n in G.nodes]
node_colors = [G.nodes[n]['stars'] for n in G.nodes]

# Normalize colors for star rating colorbar
norm = Normalize(vmin=min(node_colors), vmax=max(node_colors))
sm = ScalarMappable(cmap=plt.cm.viridis, norm=norm)
sm.set_array([])

# Create figure and axes
fig, ax = plt.subplots(figsize=(10, 8))

# Draw the graph
nx.draw(
    G,
    pos,
    ax=ax,
    with_labels=False,
    node_size=node_sizes,
    node_color=node_colors,
    cmap=plt.cm.viridis,
    edge_color='gray',
    alpha=0.7
)

# Add colorbar for star rating
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Star Rating")

# Final touches
ax.set_title("Proximity Graph of Restaurants in Sherwood Park (500m Radius)")
ax.set_axis_off()
plt.tight_layout()
plt.show()


# Correlation values
corr_stars_degree = df['stars'].corr(df['degree'])
corr_reviews_degree = df['review_count'].corr(df['degree'])
corr_stars_reviews = df['stars'].corr(df['review_count'])

# Optional p-values
p1 = pearsonr(df['stars'], df['degree'])[1]
p2 = pearsonr(df['review_count'], df['degree'])[1]
p3 = pearsonr(df['stars'], df['review_count'])[1]

print("\n=== Correlation Results ===")
print(f"Stars vs Degree:        r = {corr_stars_degree:.3f}, p = {p1:.3f}")
print(f"Review Count vs Degree: r = {corr_reviews_degree:.3f}, p = {p2:.3f}")
print(f"Stars vs Review Count:  r = {corr_stars_reviews:.3f}, p = {p3:.3f}")


sns.set(style="whitegrid")

# Degree vs. Stars
plt.figure(figsize=(7, 5))
sns.regplot(data=df, x='degree', y='stars', scatter_kws={'alpha': 0.6}, line_kws={'color': 'red'})
plt.title('Nearby Competitors (Degree) vs. Star Rating')
plt.xlabel('Number of Nearby Competitors')
plt.ylabel('Star Rating')
plt.tight_layout()
plt.show()

# Degree vs. Review Count
plt.figure(figsize=(7, 5))
sns.regplot(data=df, x='degree', y='review_count', scatter_kws={'alpha': 0.6}, line_kws={'color': 'blue'})
plt.title('Nearby Competitors (Degree) vs. Review Count')
plt.xlabel('Number of Nearby Competitors')
plt.ylabel('Review Count')
plt.tight_layout()
plt.show()

# Review Count vs. Star Rating
plt.figure(figsize=(7, 5))
sns.regplot(data=df, x='review_count', y='stars', scatter_kws={'alpha': 0.6}, line_kws={'color': 'green'})
plt.title('Review Count vs. Star Rating')
plt.xlabel('Review Count')
plt.ylabel('Star Rating')
plt.tight_layout()
plt.show()