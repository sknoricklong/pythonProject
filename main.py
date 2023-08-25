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

            # Process selected terms
            for idx, term in enumerate(selected):
                # Replace 3 letters followed by a space and then 3 numbers with a hyphen in place of the space
                selected[idx] = re.sub(r'([A-Za-z]{3}) (\d{3})', r'\1-\2', term)

                # Replace the term "PDIA" with "PDD"
                if term.upper() == "PDIA":
                    selected[idx] = "PDD"


            def convert_to_last_first(name):
                # If the name has a space, assume it's in the "FIRST LAST" format and convert it
                if ' ' in name:
                    first, last = name.split(' ', 1)
                    return f"{last}, {first}"
                return name


            # Update the selected terms list to also include the alternative "LAST, FIRST" format for names
            selected += [convert_to_last_first(term) for term in selected if ' ' in term]

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

            regex_pattern = '|'.join(selected)

            df = df_full[(df_full["description"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["course_name"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["course_code"].str.contains(regex_pattern, case=False, regex=True)) |
                         (df_full["professor"].str.contains(regex_pattern, case=False, regex=True))]
        elif type == "See all courses":
            df = df_full.copy()

        # Term Selection
        unique_terms = df['term'].dropna().unique().tolist()
        selected_terms = st.multiselect("Select Terms", unique_terms, default=unique_terms)

        # Concentration Abbreviations
        concentration_abbreviations = {
            'Analysis of Policies and Institutions': 'API',
            'Business and Government Policy': 'BGP',
            'Democracy, Politics and Institutions': 'DPI',
            'International Development': 'ID',
            'International and Global Affairs': 'IGA',
            'Management, Leadership, and Decision Sciences': 'MLD',
            'Social and Urban Policy': 'SUP',
            'STEM': 'STEM'  # Add STEM to the abbreviations
        }

        # Define the STEM courses
        stem_courses = [
            "API-114", "API-141", "API-201", "API-205", "API-209",
            "API-302", "API-318", "IGA-402", "DPI-640", "DPI-851M",
            "DPI-703", "MLD-304", "SUP-427"
        ]

        # Concentration Selection
        unique_concentrations = sorted(df['concentration'].dropna().unique().tolist())

        # Add STEM to the unique concentrations list
        unique_concentrations.append('STEM')

        # Replace concentrations with their abbreviations for display purposes
        display_concentrations = [concentration_abbreviations.get(concentration, concentration) for concentration in
                                  unique_concentrations]
        selected_display_concentrations = st.multiselect("Select Concentrations", display_concentrations,
                                                         default=display_concentrations)

        # If STEM is selected, fetch only the STEM courses
        if 'STEM' in selected_display_concentrations:
            selected_courses = stem_courses
        else:
            # Convert selected display abbreviations back to full concentration names for lookups
            selected_concentrations = [key for key, value in concentration_abbreviations.items() if
                                       value in selected_display_concentrations]
            # Fetch the courses for the selected concentrations from the dataframe
            selected_courses = df[df['concentration'].isin(selected_concentrations)]['course_code'].tolist()

        st.markdown("")
        st.markdown("😎 [Buy HKS Swag](https://bit.ly/hks-swag-tool)")
        st.markdown("👉 [Feedback?](https://forms.gle/dVQtp7XwVhqnv5Dw8)")

        if selected_terms:
            df = df[df['term'].isin(selected_terms)]

        if selected_concentrations:
            df = df[df['concentration'].isin(selected_concentrations)]

    # Group by professor and aggregate course information
    grouped = df.groupby('professor').agg(
        mean_rating=('mean_rating', 'mean'),
        mean_workload=('mean_workload', 'mean'),
        courses=('course_name', lambda x: '<br>'.join([f"({i + 1}) {course}" for i, course in enumerate(x)]))
    ).reset_index()


    def plot_scatterplot(df):
        fig = px.scatter(df, x='mean_rating', y='mean_workload', hover_name="professor",
                         labels=dict(courses='Courses Taught', mean_rating='Average Professor Rating',
                                     mean_workload='Average Professor Workload'))

        hovertemplate = "<b>%{hovertext}</b><br><b>Courses:</b><br>%{customdata[0]}<br><b>Average Rating:</b> %{customdata[1]:.2f}<br><b>Average Workload:</b> %{customdata[2]:.2f}"
        fig.update_traces(customdata=df[['courses', 'mean_rating', 'mean_workload']].values,
                          hovertemplate=hovertemplate)

        fig.update_layout(hoverlabel=dict(font_size=12))

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

        # Rectangle 1
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=4.79, y0=2.05,
                      x1=5.015, y1=2.2,
                      line=dict(color="LightSeaGreen", width=0),
                      fillcolor="limegreen",
                      opacity=0.5,
                      layer='below'
                      )

        # Rectangle 2
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=3.72, y0=4.675,
                      x1=3.945, y1=4.825,
                      line=dict(color="LightSeaGreen", width=0),
                      fillcolor="orangered",
                      opacity=0.5,
                      layer='below'
                      )

        # Rectangle 3
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=3.72, y0=2.05,
                      x1=3.945, y1=2.2,
                      line=dict(color="LightSeaGreen", width=0),
                      fillcolor="lightgrey",
                      opacity=0.5,
                      layer='below'
                      )

        # Rectangle 4
        fig.add_shape(type="rect",
                      xref="x", yref="y",
                      x0=4.79, y0=4.675,
                      x1=5.015, y1=4.825,
                      line=dict(color="LightSeaGreen", width=0),
                      fillcolor="lightgrey",
                      opacity=0.5,
                      layer='below'
                      )

        fig.add_trace(go.Scatter(
            x=[4.9, 3.83, 3.83, 4.9],
            y=[2.125, 4.735, 2.125, 4.735],
            text=["Better prof, less effort",
                  "Worse prof, more effort",
                  "Worse prof, less effort",
                  "Better prof, more effort"],
            mode="text",
        ))

        fig.update_xaxes(range=[3.7, 5.025])
        fig.update_yaxes(range=[2, 4.8])
        fig.update_layout(showlegend=False)

        fig.update_layout(uniformtext_minsize=15)
        st.plotly_chart(fig)

    st.header("🗓️ Compare Fall 2023 Courses at HKS")
    st.info("""
    - See courses based on instructor **quality** (horizontal axis) and **workload** (vertical axis)
    - Each point represents the **average score** the professor has received across their 3 most recent courses taught
    - Explore **all** courses or search **specific** courses, then hover over the points to see course scores
    """)
    plot_scatterplot(grouped)

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