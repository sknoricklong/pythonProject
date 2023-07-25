import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
from google.oauth2 import service_account
from google.cloud import bigquery
import re


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    st.set_page_config(
        page_title="Search HKS Courses",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)

    table_id = "class-377302.class.2023-spring-queries"

    df_full = pd.read_csv("./fall_2023_courses_cleaned.csv")
    median_rating = df_full['mean_rating'].median()
    median_workload = df_full['mean_workload'].median()

    last_selected = None

    with st.sidebar:
        options = ["See all courses", "Search for courses"]
        type = st.radio("", options, index=0)
        if type == "Search for courses":
            selected = st.text_input("Add search terms, separated by comma:", "environment, climate, rosenbach")
            selected = [string.strip() for string in selected.split(',') if string.strip()]

            current_time = datetime.datetime.now().isoformat()

            # Check if the selected values are different from the default values and the last selected values
            # and that they are not empty or whitespace
            if selected and selected != ['environment', 'climate', 'rosenbach'] and selected != last_selected:
                row_to_insert = [
                    {"query": x, "timestamp": current_time} for x in selected
                ]
                errors = client.insert_rows_json(
                    table_id, row_to_insert, row_ids=[None] * len(row_to_insert)
                )
                last_selected = selected

            regex_pattern = '|'.join(r'\b{}\b'.format(word) for word in selected)

            df = df_full[(df_full["description"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["course_name"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["course_code"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["professor"].str.contains(regex_pattern, case=False, regex=True))]
        elif type == "See all courses":
            df = df_full.copy()

        # Term Selection
        st.markdown("**Filter by Term:**")
        unique_terms = df['term'].dropna().unique().tolist()
        selected_terms = [term for term in unique_terms if st.checkbox(term, value=True, key=term)]

        # Concentration Selection
        st.markdown("**Filter by Concentration:**")
        unique_concentrations = sorted(df['concentration'].dropna().unique().tolist())
        selected_concentrations = [concentration for concentration in unique_concentrations if
                                   st.checkbox(concentration, value=True, key=concentration)]

        st.markdown("")
        st.markdown("👉 [Feedback?](https://forms.gle/dVQtp7XwVhqnv5Dw8)")

        if selected_terms:
            df = df[df['term'].isin(selected_terms)]

        if selected_concentrations:
            df = df[df['concentration'].isin(selected_concentrations)]


    def plot_scatterplot(df):
        fig = px.scatter(df, x='mean_rating', y='mean_workload', hover_name="course_name",
                         hover_data=['prof_search', 'mean_rating', 'mean_workload', 'term'],
                         labels=dict(prof_search='Professor', mean_rating='Average Professor Rating',
                                     mean_workload='Average Professor Workload', term='Term'))
        fig.update_layout(width=900)

        # Add horizontal line
        fig.add_shape(
            type='line',
            x0=median_rating,
            y0=0,
            x1=median_rating,
            y1=5,
            yref='y',
            line=dict(
                color='grey',
                dash='dash',
            )
        )

        # Add vertical line
        fig.add_shape(
            type='line',
            x0=0,
            y0=median_workload,
            x1=5.1,
            y1=median_workload,
            xref='x',
            line=dict(
                color='grey',
                dash='dash',
            )
        )

        fig.add_annotation(x=median_rating, y=2.1,
                           text="Median",
                           showarrow=True,
                           arrowhead=1,
                           arrowcolor='grey',
                           ax=55,
                           font_color='grey')

        fig.add_annotation(x=3.8, y=median_workload,
                           text="Median",
                           showarrow=True,
                           arrowhead=1,
                           arrowcolor='grey',
                           ax=-25,
                           font_color='grey')

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=4.79, y0=2.05,
                      x1=5.015, y1=2.2,
                      line=dict(
                          color="LightSeaGreen",
                          width=0,
                      ),
                      fillcolor="limegreen",
                      opacity=0.5,
                      layer='below'
                      )

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=3.72, y0=4.175,
                      x1=3.945, y1=4.325,
                      line=dict(
                          color="LightSeaGreen",
                          width=0,
                      ),
                      fillcolor="orangered",
                      opacity=0.5,
                      layer='below'
                      )

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=3.72, y0=2.05,
                      x1=3.945, y1=2.20,
                      line=dict(
                          color="LightSeaGreen",
                          width=0,
                      ),
                      fillcolor="lightgrey",
                      opacity=0.5,
                      layer='below'
                      )

        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=4.79, y0=4.175,
                      x1=5.015, y1=4.325,
                      line=dict(
                          color="LightSeaGreen",
                          width=0,
                      ),
                      fillcolor="lightgrey",
                      opacity=0.5,
                      layer='below'
                      )


        fig.add_trace(go.Scatter(
            x=[4.9, 3.83, 3.83, 4.9],
            y=[2.125, 4.25, 2.125, 4.25],
            text=["Better prof, less effort",
                  "Worse prof, more effort",
                  "Worse prof, less effort",
                  "Better prof, more effort"],
            mode="text",
        ))

        fig.update_xaxes(range=[3.7, 5.025])
        fig.update_yaxes(range=[2, 4.73])
        fig.update_layout(showlegend=False)

        fig.update_layout(uniformtext_minsize=15)
        st.plotly_chart(fig)

    st.header("🗓️ Compare Fall 2023 Courses at HKS")
    st.info("""
    - See courses based on instructor **quality** (horizontal axis) and **workload** (vertical axis)
    - Each point represents the **average score** the professor has received across their 3 most recent courses taught
    - Explore **all** courses or search **specific** courses, then hover over the points to see course scores
    """)
    plot_scatterplot(df)

    df.sort_values(by='mean_rating', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    st.header("🥇 Courses Ranked by  Professor's Average Rating")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    df_with_previous = df[['course_name', 'professor', 'mean_rating', 'mean_workload', 'term', 'day', 'time', 'course_code', 'description', 'course_link']].sort_values(by=['mean_rating', 'mean_workload'], ascending=[False, True]).reset_index(drop=True)
    st.write(df_with_previous.dropna(subset=['mean_rating']))

    st.header("📈 New Professors")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    df_new_professors = df_with_previous[df_with_previous['mean_rating'].isna()].reset_index(drop=True)
    df_new_professors = df_new_professors.drop(columns=['mean_rating', 'mean_workload'])
    st.write(df_new_professors)

