import pandas as pd
import re
import numpy as np

def convert_sqft_to_sqft(value):
    if '-' in value:
        # Calculate mean for ranges like '1200 - 1800'
        lower, upper = map(float, value.split('-'))
        return (lower + upper) / 2
    elif re.match(r'\d+\.?\d*\s*Sq. Meter', value):
        # Convert from square meters to square feet
        sq_meter = float(re.search(r'\d+\.?\d*', value).group())
        return sq_meter * 10.764  # 1 Sq. Meter = 10.764 Sq. Feet
    elif re.match(r'\d+\.?\d*\s*Acres', value):
        # Convert from acres to square feet
        acres = float(re.search(r'\d+\.?\d*', value).group())
        return acres * 43560  # 1 Acre = 43560 Sq. Feet
    elif re.match(r'^\d+\.?\d*$', value):
        # For numeric values without any units
        return float(value)
    else:
        return np.nan  # Convert other cases to NaN


# Load the data from the CSV file
file_path = 'housing_data.csv'
df = pd.read_csv(file_path)


#showing all attributes
print(df.columns)


#dropping unnecessary columns
df2 = df.drop(['area_type', 'society', ], axis=1, inplace=False)
print(df2.columns)


#modifying values in availability column
for index, row in df2.iterrows():
    if row['availability'] != 'Ready To Move':
        df2.loc[index, 'availability'] = 'Under Construction'


#modifying values in location column
for index, row in df2.iterrows():
    if row['location'] == 'Electronics City Phase 1' or row['location'] == 'Electronic City Phase II':
        df2.loc[index, 'location'] = 'Electronic City'
    elif row['location'] == '7th Phase JP Nagar':
        df2.loc[index, 'location'] = 'JP Nagar'

top_20_locations = df2['location'].value_counts().head(20)
top_locations_names = top_20_locations.index.tolist()
print(top_locations_names)

for index, row in df2.iterrows():
    if row['location'] not in top_locations_names:
        df2.loc[index, 'location'] = 'Other'


#renaming size column to bedroom and bath column to bathroom
df2 = df2.rename(columns={'size': 'bedroom', 'bath': 'bathroom'})
print(df2.columns)


#renaming bedroom column values
df2['bedroom'] = df2['bedroom'].str.replace(r'\D+', '', regex=True)     #remove non-numeric characters
df2['bedroom'] = df2['bedroom'].str.strip()     #remove leading and trailing whitespace characters
df2.loc[~df2['bedroom'].isnull(), 'bedroom'] = df2.loc[~df2['bedroom'].isnull(), 'bedroom'].astype(int) #convert non-NaN values into integers


# apply function to 'total_sqft' column
df2['total_sqft'] = df2['total_sqft'].apply(convert_sqft_to_sqft)


#add new columns and initialize with NaN
df2['furnishing'] = np.nan
df2['amenities'] = np.nan


#modifying vcalues in the furnishing column
df2.loc[df2['price'] <= 30, 'furnishing'] = 'Unfurnished'   #set 'Unfurnished' for price <= 30
df2.loc[(df2['price'] > 30) & (df2['price'] <= 80), 'furnishing'] = 'Semi Furnished'    #set 'Semi Furnished' for price between 31 and 80
df2.loc[df2['price'] > 80, 'furnishing'] = 'Fully Furnished'    #set 'Fully Furnished' for price > 80
# df2.to_csv('updated_data.csv', index=False)     #save the updated DataFrame to a CSV file


# Assuming df2 is your DataFrame

# Create a mapping for price ranges to amenities values
amenities_mapping = {
    (0, 30): 1,
    (31, 40): 2,
    (41, 50): 3,
    (51, 60): 4,
    (61, 70): 5,
    (71, 90): 6,
    (91, 150): 7,
    (151, 300): 8,
    (301, 500): 9,
    (501, float('inf')): 10
}

# Iterate over the mapping and set amenities value based on price range
for price_range, amenities_value in amenities_mapping.items():
    df2.loc[(df2['price'] > price_range[0]) & (df2['price'] <= price_range[1]), 'amenities'] = amenities_value

# Fill NaN or infinite values in 'amenities' column with a default value (e.g., 0)
df2['amenities'].replace([np.inf, -np.inf], np.nan, inplace=True)
df2['amenities'].fillna(0, inplace=True)

# Convert 'amenities' column to integers
df2['amenities'] = df2['amenities'].astype(int)


#down-sizing the csv file
total_rows_needed = 259

# Adjusting the weightage for each location based on priority
weightage = [4, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

# Calculate the total weightage
total_weightage = sum(weightage)

# Calculate the number of rows per location based on weightage and total rows needed
num_rows_per_location = [int(total_rows_needed * w / total_weightage) for w in weightage]

# Adjust the number of rows for the last location to reach the total
num_rows_per_location[-1] += total_rows_needed - sum(num_rows_per_location)

# Initialize an empty DataFrame for df3
df3 = pd.DataFrame(columns=df2.columns)

# Sample rows from each location and concatenate to df3
for location, num_rows in zip(top_20_locations.index, num_rows_per_location):
    location_rows = df2[df2['location'] == location].sample(n=num_rows, random_state=42)
    df3 = pd.concat([df3, location_rows])

# Reset the index of df3
df3.reset_index(drop=True, inplace=True)

# Check the size of df3
print(df3.shape)  # Should show (259, number_of_columns)

# Shuffle the rows in df3
df3_shuffled = df3.sample(frac=1, random_state=42)  # Set random_state for reproducibility

# Reset the index of the shuffled DataFrame
df3_shuffled = df3_shuffled.reset_index(drop=True)

#displaying final dataset
for index, row in df3_shuffled.iterrows():
    print(row)

#saving df3 as a csv file without index column
df3_shuffled.to_csv('final_data.csv', index=False)
print("CSV File saved successfully.")