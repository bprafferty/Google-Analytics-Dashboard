Title: Google Analytics Dashboard

Author: Brian Rafferty

Date: 12/3/2020

Description: I created an interactive dashboard displaying a sample of Google Analytics data for the Google Store. The data is stored on Google BigQuery, so to avoid incurring charges by connecting this script directly, I used SQL to query a the tables and converted the view to a CSV file called data.csv. With the data stored locally, I could then use pandas to conduct data cleaning, visualization, and analysis.

References: Google Store data from Google BigQuery: google_analytics_sample

To run:
    streamlit run ga_dashboard.py
