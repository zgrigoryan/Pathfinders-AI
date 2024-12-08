import csv
import matplotlib.pyplot as plt

# Read the CSV file
run_numbers = []
success_rates = []

with open("local_search_results.csv", "r", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        run_numbers.append(int(row["Run_Number"]))
        rate_str = row["Success_Rate"].replace('%', '')
        success_rates.append(float(rate_str))

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(run_numbers, success_rates, marker='o', linestyle='-', color='b')
plt.title("Local Search Success Rate Over Multiple Runs")
plt.xlabel("Run Number")
plt.ylabel("Success Rate (%)")
plt.grid(True)
plt.ylim(0, 100)  # success rate is from 0% to 100%
plt.show()



success_rates = []

with open("local_search_results.csv", "r", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Remove '%' sign if present and convert to float
        rate_str = row["Success_Rate"].replace('%', '')
        success_rates.append(float(rate_str))

# Calculate average success rate
if success_rates:
    average_success_rate = sum(success_rates) / len(success_rates)
    print(f"Average Success Rate: {average_success_rate:.2f}%")
else:
    print("No data found in local_search_results.csv.")
