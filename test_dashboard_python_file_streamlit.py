#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import dash
from dash import dcc, Dash, html, Input, Output, dash_table
import plotly.express as px
st.title('Movies Dashboard')

import warnings
warnings.filterwarnings("ignore")


# In[2]:


#!pip install streamlit


# In[3]:


movie_rating_tags_df = pd.read_csv("movie_rating_tags.xls")


# In[4]:


movie_rating_tags_df


# In[12]:


genre_cols = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary',
              'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 'Mystery',
              'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

# Create app
app = dash.Dash(__name__)
app.title = "Movies Explorer Dashboard"

# App layout
app.layout = html.Div([
    html.H1("Movies Explorer Dashboard", style={'textAlign': 'center', 'color': '#FFD700'}),

    html.Div([
        html.Div([
            html.Label("Year", style={'marginRight': '10px', 'color': '#FFD700'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(y), 'value': y} for y in sorted(movie_rating_tags_df['year'].dropna().unique())],
                placeholder="Select Year",
                style={'width': '140px', 'backgroundColor': '#111', 'color': '#FFD700'}
            )
        ], style={'marginRight': '20px'}),

        html.Div([
            html.Label("Genre", style={'marginRight': '10px', 'color': '#FFD700'}),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': g, 'value': g} for g in genre_cols],
                placeholder="Select Genre",
                style={'width': '200px', 'backgroundColor': '#111', 'color': '#FFD700'}
            )
        ])
    ], style={'display': 'flex', 'flexDirection': 'row', 'marginBottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='top-movies-plot')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.H3("Trending Now", style={'textAlign': 'center', 'color': '#FFD700'}),
            dcc.Graph(id='trending-plot')
        ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '2%'})
    ]),

    html.Div([
        html.H3("Rating Trend", style={'color': '#FFD700', 'textAlign': 'left'}),
        dcc.Graph(id='rating-line-plot')
    ])
], style={
    'backgroundColor': '#000000',  # Black background
    'color': '#FFD700',            # Gold text
    'padding': '20px',
    'fontFamily': 'Arial'
})

# Callback: Top 10 Movies
@app.callback(
    Output('top-movies-plot', 'figure'),
    Input('year-dropdown', 'value'),
    Input('genre-dropdown', 'value')
)
def update_top_movies(selected_year, selected_genre):
    filtered_df = movie_rating_tags_df.copy()

    # Filter by year if selected
    if selected_year:
        filtered_df = filtered_df[filtered_df['year'] == selected_year]
    
    # Filter by genre if selected
    if selected_genre:
        filtered_df = filtered_df[filtered_df[selected_genre] == 1]
    
    # Check if the filtered dataframe is empty
    if filtered_df.empty:
        return {}  # Return an empty figure if there's no data to display
    
    # Ensure 'rating_count' is numeric and drop rows with missing values
    filtered_df['rating_count'] = pd.to_numeric(filtered_df['rating_count'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['rating_count'])

    # Group by movie title and get the top 6 movies
    top_movies = (filtered_df
                  .groupby('title')['rating_count']
                  .sum()
                  .reset_index()
                  .sort_values('rating_count', ascending=False)
                  .head(6))

    # Check if top_movies is empty after processing
    if top_movies.empty:
        return {}

    # Generate the bar plot
    fig = px.bar(top_movies,
                 x='rating_count', y='title',
                 orientation='h',
                 title=f"Top Movies{f' in {selected_year}' if selected_year else ''}{f' - {selected_genre}' if selected_genre else ''}",
                 labels={'rating_count': 'Rating Count', 'title': ''},
                 color_discrete_sequence=['#FFD700'],
                 template='plotly_dark')
    
    # Customize layout and formatting
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        yaxis_tickfont=dict(size=10, family='Arial', color='gold'),
        plot_bgcolor='#000',
        paper_bgcolor='#000',
        font=dict(color='gold')
    )
    
    return fig

# Callback: Trending Movies
@app.callback(
    Output('trending-plot', 'figure'),
    Input('year-dropdown', 'value')
)
def update_trending(_):
    trending = (movie_rating_tags_df[movie_rating_tags_df['year'] >= 2014]
                .groupby('title')['rating_count']
                .sum()
                .reset_index()
                .sort_values('rating_count', ascending=False)
                .head(10))

    fig = px.bar(trending,
                 x='rating_count', y='title',
                 orientation='h',
                 labels={'rating_count': 'Rating Count', 'title': ''},
                 template='plotly_dark', color_discrete_sequence=['#FFD700'])

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        font=dict(color='#FFD700'),
        plot_bgcolor='#000',
        paper_bgcolor='#000',
        yaxis_tickfont=dict(size=10, family='Arial', color='#FFD700')
    )
    return fig

# Callback: Rating Trend
@app.callback(
    Output('rating-line-plot', 'figure'),
    Input('year-dropdown', 'value'),
    Input('genre-dropdown', 'value')
)
def update_rating_line(selected_year, selected_genre):
    filtered_df = movie_rating_tags_df.copy()

    if selected_genre:
        filtered_df = filtered_df[filtered_df[selected_genre] == 1]

    line_data = (filtered_df.groupby('year')
                 .agg(avg_rating=('rating', 'mean'),
                      total_rating_count=('rating_count', 'sum'))
                 .reset_index())

    fig = px.line(line_data,
                  x='year', y='total_rating_count',
                  markers=True,
                  labels={'total_rating_count': 'Total Rating Count', 'year': 'Year'},
                  template='plotly_dark', color_discrete_sequence=['#FFD700'])

    fig.update_layout(
        font=dict(color='#FFD700'),
        plot_bgcolor='#000',
        paper_bgcolor='#000',
        title_font=dict(color='#FFD700')
    )
    return fig

# Run server
if __name__ == '__main__':
    app.run_server(debug=True, port=8055)


# In[ ]:




