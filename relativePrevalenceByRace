import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

depression_file_path = r'F:\Raine\depression conditions.csv'
visit_files = [
    r'F:\Raine\all_visits_updated.csv',  
]

depression_data = pd.read_csv(depression_file_path, parse_dates=['CONDITION_START_DATE'], dayfirst=True)

depression_data.dropna(subset=['PERSON_ID', 'CONDITION_START_DATE'], inplace=True)

depression_data = depression_data[depression_data['CONDITION_START_DATE'] >= '2018-01-01']

depression_data['Month'] = depression_data['CONDITION_START_DATE'].dt.to_period('M')

visit_data = pd.concat([
    pd.read_csv(file, parse_dates=['VISIT_START_DATE'], dayfirst=True)
    for file in visit_files
])

visit_data.dropna(subset=['PERSON_ID', 'VISIT_START_DATE'], inplace=True)

visit_data = visit_data[visit_data['VISIT_START_DATE'] >= '2018-01-01']

visit_data['Month'] = visit_data['VISIT_START_DATE'].dt.to_period('M')

demo_data = visit_data[['PERSON_ID','RACE_CONCEPT_ID']].drop_duplicates(subset='PERSON_ID')

depression_data = pd.merge(
    depression_data,
    demo_data,
    on='PERSON_ID',
    how='left'  
)

def map_gender(g_id):
    """ Map GENDER_CONCEPT_ID to a label. """
    if g_id == 8507:
        return 'Male'
    elif g_id == 8532:
        return 'Female'

def map_race(r_id):
    """ Map RACE_CONCEPT_ID to a label. """
    if r_id == 8515:
        return 'Asian'
    elif r_id == 8516:
        return 'Black'
    elif r_id == 8527:
        return 'White'
    else:
        return 'Other'

def map_ethnicity(e_id):
    """ Map ETHNICITY_CONCEPT_ID to a label. """
    if e_id == 38003563:
        return 'Hispanic/Latino'
    else:
        return 'Not Hispanic/Latino'

def map_age(age):
    """ Convert numeric age into a category. """
    if pd.isna(age):
        return 'Unknown'
    age = float(age)
    if age < 13:
        return '<13'
    elif 13 <= age <= 17:
        return '13-17'
    elif 18 <= age <= 34:
        return '18-34'
    elif 35 <= age <= 65:
        return '35-65'
    else:
        return '>65'

depression_data['RaceCategory']   = depression_data['RACE_CONCEPT_ID'].apply(map_race)

visit_data['RaceCategory']   = visit_data['RACE_CONCEPT_ID'].apply(map_race)

def plot_prevalence_by_category(category_col, title_str, y_lim=None):
    """
    category_col: str - one of ['GenderCategory', 'RaceCategory', 'EthCategory', 'AgeCategory']
    title_str   : str - for the plot title
    y_lim       : tuple or None - y-axis limits if desired
    """

    monthly_depr_counts = (
        depression_data
        .dropna(subset=[category_col])  
        .groupby(['Month', category_col])['PERSON_ID']
        .nunique()
        .reset_index(name='DepressionCount')
    )

    monthly_depr_counts['Month'] = monthly_depr_counts['Month'].dt.to_timestamp()

    monthly_visitors = (
        visit_data
        .dropna(subset=[category_col])  
        .groupby(['Month', category_col])['PERSON_ID']
        .nunique()
        .reset_index(name='VisitorCount')
    )
    monthly_visitors['Month'] = monthly_visitors['Month'].dt.to_timestamp()

    combined = pd.merge(monthly_depr_counts,
                        monthly_visitors,
                        on=['Month', category_col],
                        how='outer')  

    combined['DepressionCount'] = combined['DepressionCount'].fillna(0)
    combined['VisitorCount']    = combined['VisitorCount'].fillna(0)

    combined['RelativePrevalence'] = 0
    mask = combined['VisitorCount'] > 0
    combined.loc[mask, 'RelativePrevalence'] = (
        combined.loc[mask, 'DepressionCount'] / combined.loc[mask, 'VisitorCount']
    )

    pivoted = combined.pivot(index='Month', columns=category_col, values='RelativePrevalence')

    plt.figure(figsize=(14, 7))
    sns.lineplot(data=pivoted, marker='o')
    plt.title(f'Relative Prevalence of Depression by {title_str}', fontsize=16, weight='bold')
    plt.xlabel('Month', fontsize=13)
    plt.ylabel('Diagnoses / Unique Visitors', fontsize=13)
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.xticks(rotation=45)
    if y_lim is not None:
        plt.ylim(y_lim)
    plt.legend(title=title_str, fontsize=11)
    plt.tight_layout()
    plt.show()

plot_prevalence_by_category(
    category_col='RaceCategory',
    title_str='Race',
    y_lim=(0.015, 0.06)  
)
