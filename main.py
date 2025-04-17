from datasets import load_dataset
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import List
from pymongo import MongoClient
from datetime import datetime

# Setup Mongo DB connection 
mongo_uri = st.secrets["mongo"]["uri"]

client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)

db = client["streamlit_app"]
collection = db["queries"]


st.set_page_config(layout="wide")

st.title("Anthropic Economic Index")
st.header("Claude Conversations Data")

explanation_on = st.toggle("Data Explanation", value=True)
if explanation_on:
    st.write("""
        A dataset of 1 million Claude.ai free and pro conversations were categorised according to O*NET task descriptors (of which there are nearly 20,000!)
        
        The categorisation was done by Claude itself and used a hierarchical approach. 
    """)

    st.write("""
        The type of interaction was categorised into:
        - Directive: Human delegates complete task execution to AI with minimal interaction
        - Feedback Loop: Human and AI engage in iterative dialogue to complete task with human mainly providing feedback from the environment
        - Task Iteration: Human and AI engage in iterative dialogue to complete a task with the human refining the AI outputs
        - Learning: Human seeks understanding and explanation rather than direct task completion
        - Validation: Human uses AI to check or validate their own work
        
        There is also a 'filtered' feature which is the proportion of those conversations that were filtered. 
    """)


def display_interaction_barchart(df, queries):

    columns = ['directive', 'feedback_loop', 'task_iteration', 'validation', 'learning', 'filtered']

    colors = {
        'directive': '#4A90E2',  # Stronger Blue
        'feedback_loop': '#62D97A',  # Stronger Green
        'task_iteration': '#FF9E6D',  # Stronger Orange
        'validation': '#B589D6',  # Stronger Purple
        'learning': '#F6D140',  # Stronger Yellow
        'filtered': '#FF5C5C',  # Stronger Pastel Red (for filtered)
    }

    # Custom legend names for each category
    custom_legend_names = {
        'directive': 'Directive',
        'feedback_loop': 'Feedback Loop',
        'task_iteration': 'Iteration',
        'validation': 'Validation',
        'learning': 'Learning',
        'filtered': 'Filtered'
    }
    
    # Filter the DataFrame (example query, replace with your actual filtering logic)
    filtered_df = df[df["task_name"].str.contains('|'.join(queries), case=False, na=False)]
    filtered_df = filtered_df.sort_values(by='pct', ascending=False)
    filtered_df = filtered_df.reset_index(drop=True)

    # Create a stacked bar chart for all rows combined into one chart
    fig = go.Figure()

    # Add bars for each category (one trace for each column)
    for col in columns:
        # Create hover text that includes task_name and category-value pair
        hover_text = [f"Task Name: {row['task_name']}<br>Task ID: {row['task_id']}<br>Task Volume (% of all conversations on platform): {round(row['pct'],2)}<br>Task Volume (per million conversations): {int((row['pct']/100)*1000000)} <br>Percentage that were {custom_legend_names[col]}: {round(100*row[col],2)}%" for _, row in filtered_df.iterrows()]
        
        # Get the custom legend name for this category
        legend_name = custom_legend_names[col]

        fig.add_trace(go.Bar(
            x=filtered_df.index,  # x-values are the rows
            y=filtered_df[col]*filtered_df['pct'],   # y-values are the values for each row in that column
            name=legend_name,      # Use custom legend name
            marker=dict(color=colors[col]),  # Assign custom vibrant pastel color
            hovertext=hover_text,  # Show task_name + category-value on hover
            hoverinfo='text',      # Only show text (values) when hovered
        ))

    # Update layout for stacking bars
    fig.update_layout(
        barmode='stack',        # Stacked bars
        title="Distribution of Interactions",
        xaxis_title='Row',
        yaxis_title='Value',
        showlegend=True         # Show the legend for the categories
    )

    fig.update_layout(
        hovermode='closest',
        hoverlabel=dict(
            font=dict(size=15)  # Increase hover text font size
        )
    )

    fig.update_layout(
        legend=dict(
            font=dict(
                size=15  # Adjust font size here
            )
        )
    )


    # Display the chart in Streamlit
    st.plotly_chart(fig)


def display_interaction_table(df, queries):

    custom_column_names = {
        'directive': 'Directive',
        'feedback_loop': 'Feedback Loop',
        'task_iteration': 'Task Iteration',
        'validation': 'Validation',
        'learning': 'Learning',
        'filtered': 'Filtered'
    }

    # Filter the DataFrame (example query, replace with your actual filtering logic)
    filtered_df = df[df["task_name"].str.contains('|'.join(queries), case=False, na=False)]
    filtered_df = filtered_df.sort_values(by='pct', ascending=False)
    filtered_df = filtered_df.reset_index(drop=True)

    filtered_df['task_id'] = filtered_df['task_id'].astype(int)
    category_cols = ['directive', 'feedback_loop', 'task_iteration', 'validation', 'learning', 'filtered']
    filtered_df[category_cols] = filtered_df[category_cols].applymap(lambda x: f"{x:.2f}")

    filtered_df.rename(columns=custom_column_names, inplace=True)

    filtered_df['Volume (per 1 Million)'] = round((filtered_df['pct']/100) * 1000000, 0)
    filtered_df['Volume (per 1 Million)'] = filtered_df['Volume (per 1 Million)'].astype(int)

    filtered_df.rename(columns={'pct': 'Volume (percentage of all conversations)'}, inplace=True)

    filtered_df['Rank'] = filtered_df.index + 1

    # move task id to being first column
    columns = list(filtered_df.columns)
    columns.insert(0, columns.pop(columns.index('task_id')))  # Pop 'task_id' and insert at the start
    # Reorder DataFrame based on new column order
    filtered_df = filtered_df[columns]

    st.markdown(filtered_df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        

if __name__ == "__main__":

    df = pd.read_csv("anthropic/integrated.csv")
    df['task_id'] = df.index # we need task IDs as the task names are very long in some cases 

    # Search for a string match in a task 

    st.subheader("Make a Query")
    st.write('For multiple strings to match, use a comma separated query (e.g., "compliance, legal"). Note that it currently matches by substring.')
    st.write("*Please note that we anonymously record queries to see how people are engaging with our content*")

    query = st.text_input("Query Keywords: ")

    if query: 
        queries = [item.strip() for item in query.split(',')]
 
    st.subheader("Tasks: Volume and Interaction Type")

    if query:

        doc = {"text": query, "timestamp": datetime.utcnow()}
        collection.insert_one(doc) # upload to MongoDB database

        st.write("Hover your mouse over a bar to see the task name. A table view can be opened below.")
        display_interaction_barchart(df, queries)

        table_on = st.toggle("Table View", value=True, key="interaction_table_toggle")
        if table_on:
            display_interaction_table(df, queries)
    
    else:
        st.write("Please search for a keyword")

    # High filtered tasks overall 

    st.subheader("High Filtered Tasks (above 0.01% of conversation volume)")
    
    high_filtered = df[(df['filtered'] > 0.7) & (df['pct'] > 0.01)] # we have a cut off to ignore very rarely asked tasks
    display_interaction_barchart(high_filtered, [""])
    
    table_on = st.toggle("Table View", value=True, key="high_filtered_table_toggle")
    if table_on:
        display_interaction_table(high_filtered, [""])




