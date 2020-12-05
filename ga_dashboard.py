import bokeh
import bokeh.layouts
import bokeh.models
import bokeh.plotting
import datetime as dt
import markdown
import numpy as np
import pandas as pd
import streamlit as st
import json
from pandas.io.json import json_normalize

DATA_PATH = 'data.csv'
def main():
    st.markdown('''
    # Google Analytics Dashboard
    ### Created by [Brian Rafferty](https://www.brianrafferty.net/)
    Dashboard for Google Analytics data recorded by the Google Store.
    Data provided by Google BigQuery database: google_analytics_sample
    Inspiration for project: [Kaggle](https://www.kaggle.com/c/ga-customer-revenue-prediction/data?select=train.csv).
    ''')
    st.markdown('## In modern business, the 80/20 rule denotes how only a small percentage of customers produce most of the revenue. Due to this phenomenon, businesses face a daily challenge to better understand their customers.')
    st.image('Google-Store.jpg', caption='Image from Claudiu Sima', use_column_width=True)
    st.markdown('## The goal of this dashboard is to highlight revenue indicators for the Google Store, and help the marketing team discover insights to leverage untapped markets.')
    st.write('')

    @st.cache
    def load_data():
        data = pd.read_csv(DATA_PATH, nrows=10000, index_col=0)
        return data

    raw_df = load_data()
    raw_df.to_csv('data.csv')

    if st.checkbox('Show some raw Google Analytics data'):
        st.subheader('Raw data')
        st.write(raw_df.head())
        st.write('As you can see, some columns contain JSON. Before analysing the data, preprocessing is required. We will use [this kernel](https://www.kaggle.com/julian3833/1-quick-start-read-csv-and-flatten-json-fields/notebook), by [Julian](https://www.kaggle.com/julian3833), to convert the single json columns into a "flattened" format.')

    @st.cache
    def preprocess_json():
        json_cols = ['trafficSource', 'geoNetwork', 'device', 'totals']
        data = pd.read_csv(DATA_PATH, 
                     converters={column: json.loads for column in json_cols}, 
                     dtype={'fullVisitorId': 'str'},
                     nrows=10000,
                     index_col=0)
        
        for col in json_cols:
            flattened_col_df = json_normalize(data[col])
            flattened_col_df.columns = [f'{col}.{subcolumn}' for subcolumn in flattened_col_df.columns]
            data = data.drop(col, axis=1).merge(flattened_col_df, right_index=True, left_index=True)
        numeric_cols = ['totals.hits', 'totals.pageviews', 'totals.bounces', 'totals.newVisits', 'totals.transactionRevenue']
        for col in numeric_cols:
            data[col] = pd.to_numeric(data[col])
            data[col] = data[col].fillna(0)
        data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
        data['date'] = data['date'].dt.strftime('%Y-%m-%d')

        return data

    clean_df = preprocess_json()

    if st.checkbox('Show some of the cleaned data'):
        st.subheader('Clean data')
        st.write(clean_df.head())
        st.write('Now each column that contained JSON is expanded into a flattened format. We can now begin data analysis!')
    
    if st.checkbox('Click to visualize the correlation of the dataset.'):
        correlation = clean_df.corr()
        st.write(correlation)
        
    
    
    st.markdown('''
    ### Click each tab below to explore the data visualizations.
    ''')
    st.write('')
    tabs = bokeh.models.Tabs(
        tabs=[
            device_panel(clean_df),
            date_panel(clean_df),
            geography_panel(clean_df),
        ]
    )
    st.bokeh_chart(tabs)

def _markdown(text):
    return bokeh.models.widgets.markups.Div(
        text=markdown.markdown(text), sizing_mode="stretch_width"
    )

def device_panel(df):
    count = df.groupby('device.browser')['totals.transactionRevenue'].agg(['count'])
    count.columns = ['count']
    count = count.sort_values(by='count', ascending=False)
    
    a = bokeh.plotting.figure(x_range=list(count.index), plot_width=700, plot_height=500, title='Count of Customers who Accessed Google Store by Internet Browser', toolbar_location=None, tools='')
    a.vbar(x=count.index, top=count['count'], width=0.9, color='#4285F4')
    a.xaxis.major_label_orientation = 'vertical'

    non_zero = pd.DataFrame()
    non_zero['non zero count'] = df[df['totals.transactionRevenue'] > 0].groupby('device.browser')['totals.transactionRevenue'].count()
    non_zero = non_zero.sort_values(by='non zero count', ascending=False)

    b = bokeh.plotting.figure(x_range=list(non_zero.index), plot_width=700, plot_height=500, title='Count of Customers who Made a Purchase at Google Store by Internet Browser', toolbar_location=None, tools='')
    b.vbar(x=non_zero.index, top=non_zero['non zero count'], width=0.9, color='#DB4437')
    b.xaxis.major_label_orientation = 'vertical'

    average = df.groupby('device.browser')['totals.transactionRevenue'].agg(['mean'])
    average.columns = ['mean']
    average = average.sort_values(by='mean', ascending=False)
    
    c = bokeh.plotting.figure(x_range=list(average.index), plot_width=700, plot_height=500, title='Average Revenue Generated by Internet Browser', toolbar_location=None, tools='')
    c.vbar(x=average.index, top=average['mean'], width=0.9, color='#F4B400')
    c.xaxis.major_label_orientation = 'vertical'
    browser_text = """
<br/>We can infer that Google Store should target customers who use Chrome. Not only is the vast majority of their revenue generated from customers who use Chrome, but their customer base also overwhelmingly uses Chrome over other browsers.
    """

    count = df.groupby('device.deviceCategory')['totals.transactionRevenue'].agg(['count'])
    count.columns = ['count']
    count = count.sort_values(by='count', ascending=False)
    
    d = bokeh.plotting.figure(x_range=list(count.index), plot_width=700, plot_height=500, title='Count of Customers who Accessed Google Store by Device Category', toolbar_location=None, tools='')
    d.vbar(x=count.index, top=count['count'], width=0.9, color='#4285F4')
    #d.xaxis.major_label_orientation = 'vertical'

    non_zero = pd.DataFrame()
    non_zero['non zero count'] = df[df['totals.transactionRevenue'] > 0].groupby('device.deviceCategory')['totals.transactionRevenue'].count()
    non_zero = non_zero.sort_values(by='non zero count', ascending=False)

    e = bokeh.plotting.figure(x_range=list(non_zero.index), plot_width=700, plot_height=500, title='Count of Customers who Made a Purchase at Google Store by Device Category', toolbar_location=None, tools='')
    e.vbar(x=non_zero.index, top=non_zero['non zero count'], width=0.9, color='#0F9D58')
    #e.xaxis.major_label_orientation = 'vertical'

    average = df.groupby('device.deviceCategory')['totals.transactionRevenue'].agg(['mean'])
    average.columns = ['mean']
    average = average.sort_values(by='mean', ascending=False)
    
    f = bokeh.plotting.figure(x_range=list(average.index), plot_width=700, plot_height=500, title='Average Revenue Generated by Device Category', toolbar_location=None, tools='')
    f.vbar(x=average.index, top=average['mean'], width=0.9, color='#DB4437')
    #f.xaxis.major_label_orientation = 'vertical'
    os_text = """
<br/>Google Store should target customers who use Desktop and Laptop computers to browse. The data shows that a customer is much more likely to make a purchase with a computer than a mobile device or tablet.
    """

    column = bokeh.layouts.Column(
        children=[a,b,c,_markdown(browser_text),d,e,f,_markdown(os_text)], sizing_mode="stretch_width"
    )
    return bokeh.models.Panel(child=column, title="Device Plots")

def date_panel(df):
    count = df.groupby('date')['totals.transactionRevenue'].agg(['count'])
    count.columns = ['count']
    count.sort_index()
    
    a = bokeh.plotting.figure(x_range=list(count.index), plot_width=700, plot_height=500, title='Count of Customers who Accessed Google Store by Date', toolbar_location=None, tools='')
    a.line(x=count.index, y=count['count'], line_width=3, color='#4285F4')
    
    non_zero = pd.DataFrame()
    non_zero['non zero count'] = df[df['totals.transactionRevenue'] > 0].groupby('date')['totals.transactionRevenue'].count()
    non_zero.sort_index()

    b = bokeh.plotting.figure(x_range=list(non_zero.index), plot_width=700, plot_height=500, title='Count of Customers who Made a Purchase at Google Store by Date', toolbar_location=None, tools='')
    b.line(x=non_zero.index, y=non_zero['non zero count'], line_width=3, color='#DB4437')
    
    date_text = """
<br/>The time series data displays that Google Store should invest in ad campaigns during the holiday season to better target paying customers. It is interesting to see how the amount of Google Store page views drop between September 2016 and January 2017, but the amount of purchases during that period remains the same.
    """
    column = bokeh.layouts.Column(
        children=[a, b, _markdown(date_text)], sizing_mode="stretch_width"
    )
    return bokeh.models.Panel(child=column, title="Date Plots")

def geography_panel(df):
    count = df.groupby('geoNetwork.continent')['totals.transactionRevenue'].agg(['count'])
    count.columns = ['count']
    count = count.sort_values(by='count', ascending=False)
    
    a = bokeh.plotting.figure(x_range=list(count.index), plot_width=700, plot_height=500, title='Count of Customers who Accessed Google Store by Continent', toolbar_location=None, tools='')
    a.vbar(x=count.index, top=count['count'], width=0.9, color='#4285F4')
    #a.xaxis.major_label_orientation = 'vertical'

    non_zero = pd.DataFrame()
    non_zero['non zero count'] = df[df['totals.transactionRevenue'] > 0].groupby('geoNetwork.continent')['totals.transactionRevenue'].count()
    non_zero = non_zero.sort_values(by='non zero count', ascending=False)

    b = bokeh.plotting.figure(x_range=list(non_zero.index), plot_width=700, plot_height=500, title='Count of Customers who Made a Purchase at Google Store by Continent', toolbar_location=None, tools='')
    b.vbar(x=non_zero.index, top=non_zero['non zero count'], width=0.9, color='#DB4437')
    #b.xaxis.major_label_orientation = 'vertical'

    average = df.groupby('geoNetwork.continent')['totals.transactionRevenue'].agg(['mean'])
    average.columns = ['mean']
    average = average.sort_values(by='mean', ascending=False)
    
    c = bokeh.plotting.figure(x_range=list(average.index), plot_width=700, plot_height=500, title='Average Revenue Generated by Continent', toolbar_location=None, tools='')
    c.vbar(x=average.index, top=average['mean'], width=0.9, color='#F4B400')
    #c.xaxis.major_label_orientation = 'vertical'
    continent_text = """
<br/>Based upon the continental data, Google Store should target customers who live in the Americas. From this view it is only the Americas that generate revenue, but looking at a continental perspective might be too generalized.
    """

    count = df.groupby('geoNetwork.subContinent')['totals.transactionRevenue'].agg(['count'])
    count.columns = ['count']
    count = count.sort_values(by='count', ascending=False)
    
    d = bokeh.plotting.figure(x_range=list(count.index), plot_width=700, plot_height=500, title='Count of Customers who Accessed Google Store by Sub Continent', toolbar_location=None, tools='')
    d.vbar(x=count.index, top=count['count'], width=0.9, color='#4285F4')
    d.xaxis.major_label_orientation = 'vertical'

    non_zero = pd.DataFrame()
    non_zero['non zero count'] = df[df['totals.transactionRevenue'] > 0].groupby('geoNetwork.subContinent')['totals.transactionRevenue'].count()
    non_zero = non_zero.sort_values(by='non zero count', ascending=False)

    e = bokeh.plotting.figure(x_range=list(non_zero.index), plot_width=700, plot_height=500, title='Count of Customers who Made a Purchase at Google Store by Sub Continent', toolbar_location=None, tools='')
    e.vbar(x=non_zero.index, top=non_zero['non zero count'], width=0.9, color='#0F9D58')
    #e.xaxis.major_label_orientation = 'vertical'

    average = df.groupby('geoNetwork.subContinent')['totals.transactionRevenue'].agg(['mean'])
    average.columns = ['mean']
    average = average.sort_values(by='mean', ascending=False)
    
    f = bokeh.plotting.figure(x_range=list(average.index), plot_width=700, plot_height=500, title='Average Revenue Generated by Sub Continent', toolbar_location=None, tools='')
    f.vbar(x=average.index, top=average['mean'], width=0.9, color='#DB4437')
    f.xaxis.major_label_orientation = 'vertical'
    subcontinent_text = """
<br/>By breaking it down further into sub continents, we now know that Google Store should focus their marketing on North American and Caribbean customers. That could have been a lot of money wasted by including South Americans in the ad campaign.
    """
    column = bokeh.layouts.Column(
        children=[a, b, c, _markdown(continent_text), d, e, f, _markdown(subcontinent_text)], sizing_mode="stretch_width"
    )
    return bokeh.models.Panel(child=column, title="Geographic Plots")

main()

