import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv('EPL.csv')
    
    date_parse1_cond = (df.Season.between(1993,2001))|(df.Season.between(2003,2014))|(df.Season.between(2016,2016))
    
    date_parse1_idx = df[date_parse1_cond].index
    date_parse2_idx = df[~date_parse1_cond].index

    df.loc[date_parse1_idx,'Date'] = pd.to_datetime(df.loc[date_parse1_idx,'Date'],format='%d/%m/%y')
    df.loc[date_parse2_idx,'Date'] = pd.to_datetime(df.loc[date_parse2_idx,'Date'],format='%d/%m/%Y')
    
    return df

@st.cache_data
def get_standings(year,df,total_teams = None):
    df_sub = df[df.Season == year]

    teams = list(set(list(df_sub.HomeTeam.unique()) + list(df_sub.AwayTeam.unique())))
    if total_teams:
        teams = total_teams
    standings = pd.DataFrame(teams,columns=['Team'])    

    def count_wins(team):
        C = (df_sub[(df_sub.HomeTeam == team)].FTR == 'H').sum()
        C += (df_sub[(df_sub.AwayTeam == team)].FTR == 'A').sum()
        return C

    def count_draws(team):
        C = (df_sub[(df_sub.HomeTeam == team)|(df_sub.AwayTeam == team)].FTR == 'D').sum()
        return C

    def count_losses(team):
        C = (df_sub[(df_sub.HomeTeam == team)].FTR == 'A').sum()
        C += (df_sub[(df_sub.AwayTeam == team)].FTR == 'H').sum()
        return C
    
    def count_matches_played(team):
        C = df_sub[(df_sub.HomeTeam == team)|(df_sub.AwayTeam == team)]
        return C.shape[0]
    
    def count_goals_for(team):
        C = (df_sub[(df_sub.HomeTeam == team)].FTHG).sum()
        C += (df_sub[(df_sub.AwayTeam == team)].FTAG).sum()
        return C
    
    def count_goals_against(team):
        C = (df_sub[(df_sub.HomeTeam == team)].FTAG).sum()
        C += (df_sub[(df_sub.AwayTeam == team)].FTHG).sum()
        return C
    
    standings['MP'] = standings.Team.apply(count_matches_played)
    
    standings['W'] = standings.Team.apply(count_wins)
    standings['D'] = standings.Team.apply(count_draws)
    standings['L'] = standings.Team.apply(count_losses)

    standings['GF'] = standings.Team.apply(count_goals_for)
    standings['GA'] = standings.Team.apply(count_goals_against)
    standings['GD'] = standings.GF - standings.GA

    standings['Points'] = standings['W']*3 + standings['D']

    standings.sort_values(['Team'],ascending=True,inplace=True)
    standings.sort_values(['Points','GD','GF'],ascending=False,inplace=True)
    standings.index = range(1,len(teams)+1)

    return standings

@st.cache_data
def get_standings_overtime(year,df,imp_cols = ['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','Season']):
    df_year = df[df.Season == year].dropna(axis=1,how='all')[imp_cols]
    
    standings_overtime = pd.DataFrame(pd.date_range(start=df_year.Date.min(), end=df_year.Date.max(), freq='D'),columns=['Date'])
    standings_overtime.loc[:,df_year.HomeTeam.unique()] = 0
    standings_overtime.set_index('Date',inplace=True)

    for ix,day in enumerate(standings_overtime.index):
        standing_i = get_standings(year,df_year[df_year['Date']<=day],total_teams=list(df_year.HomeTeam.unique())).set_index('Team')
        standing_i['Pos'] = range(1,21)
        standings_overtime.loc[day,:] = standing_i['Pos'].loc[list(standings_overtime.columns)].values

    return standings_overtime

@st.cache_data
def get_referee_data(df,imp_cols=['Date','Referee','HY','AY','HR','AR','TY','TR']):
    df['TY'] = df['HY']+df['AY']
    df['TR'] = df['HR']+df['AR']
    return df[imp_cols]

@st.cache_data
def get_referee_overtime(df,ref_name):
    return df[df.Referee == ref_name]