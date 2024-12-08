import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import chain

# Load the CSV file into a DataFrame
df = pd.read_csv("results.csv")

# Verify the column names
print("Columns in DataFrame:", df.columns.tolist())

# Define the list of algorithms to include
algorithms = ['BFS', 'DFS', 'UCS', 'A*']

# Check if all required algorithms are present in the DataFrame
missing_algorithms = [alg for alg in algorithms if alg not in df.columns]
if missing_algorithms:
    print(f"Missing columns in CSV: {missing_algorithms}")
    raise ValueError(f"The following required columns are missing in the CSV: {missing_algorithms}")

# Convert the DataFrame from wide to long format for the line plot
df_long = df.melt(id_vars=["Run_number"], var_name="Algorithm", value_name="Runtime")

# Filter out the data to include only the selected algorithms
df_long = df_long[df_long['Algorithm'].isin(algorithms)]

# Set the overall theme for the plots
sns.set_theme(style="whitegrid")

# Create a figure with two subplots side by side
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# ----------------------------
# 1. Line Plot: Runtime vs Run Number
# ----------------------------
sns.lineplot(
    ax=axes[0],
    data=df_long,
    x="Run_number",
    y="Runtime",
    hue="Algorithm",
    marker="o",
    palette="tab10"
)

# Customize the first subplot
axes[0].set_title("Runtime of Algorithms Over Multiple Runs", fontsize=20)
axes[0].set_xlabel("Run Number", fontsize=16)
axes[0].set_ylabel("Runtime (seconds)", fontsize=16)
axes[0].legend(title="Algorithm", fontsize=14, title_fontsize=16)
axes[0].tick_params(axis='both', which='major', labelsize=14)

# ----------------------------
# 2. Bar Chart: Count of Fastest Algorithms
# ----------------------------

# Determine the fastest algorithm(s) for each run
min_runtimes = df[algorithms].min(axis=1)

# Find all algorithms that have the minimum runtime in each run
fastest_algorithms = df[algorithms].apply(lambda row: row[row == row.min()].index.tolist(), axis=1)

# Flatten the list of lists to a single list
fastest_algorithms_flat = list(chain.from_iterable(fastest_algorithms))

# Count how many times each algorithm was the fastest
fastest_counts = pd.Series(fastest_algorithms_flat).value_counts()

# Ensure all algorithms are present, even with zero counts
fastest_counts = fastest_counts.reindex(algorithms, fill_value=0)

# Sort the counts in ascending order
fastest_counts_sorted = fastest_counts.sort_values()

# Debug: Print sorted counts
print("Fastest Counts Sorted:\n", fastest_counts_sorted)

# Create a bar plot for the counts without specifying 'order'
sns.barplot(
    ax=axes[1],
    x=fastest_counts_sorted.index,
    y=fastest_counts_sorted.values,
    palette="viridis"
)

# Customize the second subplot
axes[1].set_title("Number of Times Each Algorithm Was Fastest", fontsize=20)
axes[1].set_xlabel("Algorithm", fontsize=16)
axes[1].set_ylabel("Count", fontsize=16)
axes[1].tick_params(axis='both', which='major', labelsize=14)

# Add counts above the bars for clarity
for index, value in enumerate(fastest_counts_sorted.values):
    axes[1].text(index, value + 0.5, str(value), ha='center', va='bottom', fontsize=14)

# Adjust layout for better spacing
plt.tight_layout()

# Display the plots
plt.show()
