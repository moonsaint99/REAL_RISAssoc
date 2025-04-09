import pandas as pd
import glob

# Specify the path to the directory containing the uncorrected CSV files
file_pattern = "results/picks_*_uncorrected.csv"

# Use glob to find all matching files
file_list = glob.glob(file_pattern)

# Read and concatenate all the CSVs into a single DataFrame
combined_df = pd.concat((pd.read_csv(file) for file in file_list), ignore_index=True)

# Display the combined DataFrame or save it to a file
print(combined_df.head())
combined_df.to_csv("combined_uncorrected.csv", index=False)