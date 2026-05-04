import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set working directory to project root
proj_dir = r"d:\DSEB\Seminar 4\Econometric\Project"
os.chdir(proj_dir)

# Read the latest cleaned sample data
df = pd.read_excel('Group13_DSEB66A.xlsx')
# remove outlier
df = df[df['Salary'] > 1000]

# Style settings
sns.set_theme(style="whitegrid")

# Histogram for Age
plt.figure(figsize=(6, 4))
sns.histplot(df['Age'], bins=20, kde=True, color='skyblue')
plt.title('Distribution of Age')
plt.xlabel('Age (Years)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('hist_age.png', dpi=150)
plt.close()

# Histogram for Experience
plt.figure(figsize=(6, 4))
sns.histplot(df['Years of Experience'], bins=15, kde=True, color='lightgreen')
plt.title('Distribution of Experience')
plt.xlabel('Years of Experience')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('hist_experience.png', dpi=150)
plt.close()

# Histogram for Salary
plt.figure(figsize=(6, 4))
sns.histplot(df['Salary'], bins=30, kde=True, color='salmon')
plt.title('Distribution of Salary')
plt.xlabel('Salary (USD)')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('hist_salary.png', dpi=150)
plt.close()

print("Histograms generated successfully.")
