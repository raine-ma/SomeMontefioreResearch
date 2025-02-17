import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = r'F:\Raine\depression conditions.csv'

data = pd.read_csv(file_path, parse_dates=['CONDITION_START_DATE'], dayfirst=True)

data = data.dropna(subset=['PERSON_ID', 'CONDITION_START_DATE'])

earliest_conditions = data.groupby('PERSON_ID', as_index=False).agg({'CONDITION_START_DATE': 'min'})

earliest_conditions = earliest_conditions[earliest_conditions['CONDITION_START_DATE'] >= '2018-01-01']

assert earliest_conditions['PERSON_ID'].duplicated().sum() == 0, "Duplicate PERSON_IDs found after grouping!"

earliest_conditions['Month'] = earliest_conditions['CONDITION_START_DATE'].dt.to_period('M')

monthly_counts = earliest_conditions.groupby('Month').size()

monthly_counts_df = monthly_counts.reset_index(name='Diagnosis Count')
monthly_counts_df['Month'] = monthly_counts_df['Month'].dt.to_timestamp()
print(monthly_counts_df.to_string())

sns.set(style="whitegrid", context="talk") 
plt.figure(figsize=(16, 8))

monthly_counts_df = monthly_counts_df[0:-1]

sns.lineplot(
    data=monthly_counts_df,
    x='Month',
    y='Diagnosis Count',
    marker='o',
    color='#007ACC',
    linewidth=2.5,
    label='Monthly Earliest Diagnoses'
)

mean_val = monthly_counts_df['Diagnosis Count'][0:24].mean()
std_err = monthly_counts_df['Diagnosis Count'].std() / (len(monthly_counts_df) ** 0.5)
ci_value = 1.96 * std_err 

plt.axhline(mean_val, color='#FF5733', linestyle='--', linewidth=2, label='Mean (2018-19)')
plt.fill_between(monthly_counts_df['Month'], mean_val - ci_value, mean_val + ci_value, 
                 color='#FFC300', alpha=0.2, label='95% CI (Relative to 2018-19 mean)')

plt.title('Monthly Earliest Diagnoses of Depression (From 2018)', fontsize=18, weight='bold', pad=20)
plt.xlabel('Month', fontsize=14, labelpad=15)
plt.ylabel('Number of Unique Patients Diagnosed', fontsize=14, labelpad=15)
plt.ylim(200, monthly_counts_df['Diagnosis Count'].max()*1.1)
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12, frameon=False, loc='upper left')

sns.despine()
plt.show()
