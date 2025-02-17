#prevalence relative to visits by month. 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paths to files
depression_file_path = r'F:\Raine\depression conditions.csv'
visit_files = [
    r'F:\Roham\BC Pandemic (with Hasan)\telehealth.csv',
    r'F:\Roham\BC Pandemic (with Hasan)\outpatient.csv',
    r'F:\Roham\BC Pandemic (with Hasan)\office visit.csv',
    r'F:\Roham\BC Pandemic (with Hasan)\inpatient.csv'
]

# Read and process depression data
data = pd.read_csv(depression_file_path, parse_dates=['CONDITION_START_DATE'], dayfirst=True)
data = data.dropna(subset=['PERSON_ID', 'CONDITION_START_DATE'])
data = data[data['CONDITION_START_DATE'] >= '2018-01-01']
data['Month'] = data['CONDITION_START_DATE'].dt.to_period('M')

# Get unique depression diagnoses per month
monthly_depression_counts = data.groupby('Month')['PERSON_ID'].nunique()
monthly_depression_df = monthly_depression_counts.reset_index(name='Depression Diagnoses')
monthly_depression_df['Month'] = monthly_depression_df['Month'].dt.to_timestamp()

# Combine visit data from all files
visit_data = pd.concat([pd.read_csv(file, parse_dates=['VISIT_START_DATE'], dayfirst=True) for file in visit_files])
visit_data = visit_data.dropna(subset=['PERSON_ID', 'VISIT_START_DATE'])
visit_data = visit_data[visit_data['VISIT_START_DATE'] >= '2018-01-01']
visit_data['Month'] = visit_data['VISIT_START_DATE'].dt.to_period('M')

# Get unique visitors per month
monthly_visitors = visit_data.groupby('Month')['PERSON_ID'].nunique()
monthly_visitors_df = monthly_visitors.reset_index(name='Unique Visitors')
monthly_visitors_df['Month'] = monthly_visitors_df['Month'].dt.to_timestamp()

# Merge depression data with visit data
combined_df = pd.merge(monthly_depression_df, monthly_visitors_df, on='Month')

# Calculate relative prevalence
combined_df['Relative Prevalence'] = combined_df['Depression Diagnoses'] / combined_df['Unique Visitors']

combined_df = combined_df[0:-1]

print(combined_df)

# Plot relative prevalence
sns.set(style="whitegrid", context="talk")
plt.figure(figsize=(16, 8))

sns.lineplot(
    data=combined_df,
    x='Month',
    y='Relative Prevalence',
    marker='o',
    color='#007ACC',  
    linewidth=2.5,
    label='Relative Prevalence of Depression'
)

# Calculate mean and 95% CI for relative prevalence
mean_val = combined_df['Relative Prevalence'][0:24].mean()
std_err = combined_df['Relative Prevalence'].std() / (len(combined_df) ** 0.5)
ci_value = 1.96 * std_err

plt.axhline(mean_val, color='#FF5733', linestyle='--', linewidth=2, label='Mean (2018-19)')
plt.fill_between(combined_df['Month'], mean_val - ci_value, mean_val + ci_value,
                 color='#FFC300', alpha=0.2, label='95% CI (Relative to 2018-19 mean)')

plt.title('Relative Prevalence of Depression Diagnoses (From 2018)', fontsize=18, weight='bold', pad=20)
plt.xlabel('Month', fontsize=14, labelpad=15)
plt.ylabel('Relative Prevalence (Diagnoses per Visitor)', fontsize=14, labelpad=15)
plt.ylim(0.0275, 0.05)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12, frameon=False, loc='upper left')

sns.despine()
plt.show()
