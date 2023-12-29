"""
Created on Thur 28/12/2023

@author: Timme
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

from helpers import *

# Layouts
st.set_page_config(layout="wide")#class="st-emotion-cache-6qob1r eczjsme3"
st.sidebar.markdown(
    """
    <style>
        [class="st-emotion-cache-1cypcdb eczjsme11"] {
            width: 200px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Load data
df = load_data()


# Build Dashboard
add_sidebar = st.sidebar.selectbox('Dashboard View',('Standings','Referee Info'))

if add_sidebar == 'Standings':
    st.markdown(' # Standings')
    col1,col2 = st.columns([1,4])
    
    selected_year = col1.selectbox('Select a Year', list(range(2023,1992,-1)))
    selected_view = col1.selectbox('Select a View', ['Table','Graph'])

    if selected_view == 'Table':
        standings = get_standings(selected_year,df)
        col2.markdown(' ## Table ')
        col2.dataframe(standings)
    elif selected_view == 'Graph':
        selected_team = col1.multiselect('Select a Team', sorted(list(df[df.Season==2022].HomeTeam.unique())))
        standings_overtime = get_standings_overtime(selected_year,df)

        fig = px.line(standings_overtime,x=standings_overtime.index, y=selected_team, title=f'{selected_team} Standings for {selected_year}/{selected_year+1} Season Plot')
        # fig.update_layout(yaxis=dict(range=[20, 1]))
        fig.update_layout(yaxis=dict(autorange='reversed'))
        fig.update_layout(yaxis_title='Position')
        fig.update_layout(legend=dict(title='Team'))

        col2.plotly_chart(fig)
elif add_sidebar == 'Referee Info':
    st.markdown(' # Referee Info')
    col1,col2 = st.columns([1,4])
    
    selected_view = col1.selectbox('Select a View',['Referee Overtime'])
    selected_ref = col1.selectbox('Select a Referee',list(df.Referee.value_counts()[df.Referee.value_counts()>=3].keys()))

    df_refs = get_referee_data(df)
    df_ref = get_referee_overtime(df_refs,selected_ref)

    trace_Y = go.Scatter(x=df_ref.Date,y=df_ref.TY,mode='lines',name='Yellow', line=dict(color='yellow'))
    trace_R = go.Scatter(x=df_ref.Date,y=df_ref.TR,mode='lines',name='Red', line=dict(color='red'))

    layout = go.Layout(title=f'Number of Yellow and Red Cards given by {selected_ref} Over Time',
                   yaxis=dict(title='Number of Cards'),
                   legend=dict(title='Card Type'))

    fig = go.Figure(data=[trace_Y, trace_R], layout=layout)

    col2.plotly_chart(fig)    