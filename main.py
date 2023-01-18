import pandas as pd
import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import statsmodels

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    st.set_page_config(
        page_title="Search HKS Courses",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    median_rating, median_workload = 4.436, 3.308
    df_full = pd.read_csv("./spring_2023_courses_cleaned.csv")

    with st.sidebar:
        # st.info(
        #     """
        #     **About:** Compare Spring 2023 courses at HKS, from 3,000+ evaluations on KNET.
        #     """)
        options = ["See all courses", "Search for courses"]
        type = st.radio("", options, index=0)
        if type == "Search for courses":
            selected = st.text_input("Add search terms, separated by comma:", "environment, climate, rosenbach")
            print(selected)
            selected = [string.strip() for string in selected.split(',')]
            df = df_full[df_full["course_description"].str.contains('|'.join(selected), case=False) |
                         df_full["course_name"].str.contains('|'.join(selected), case=False) |
                         df_full["professor"].str.contains('|'.join(selected), case=False)]
        elif type == "See all courses":
            df = df_full.copy()

        # Term Selection
        st.markdown("**Filter by Session:**")
        full_term = st.checkbox("Full Term", value=True)
        spring_1 = st.checkbox("Spring 1", value=True)
        spring_2 = st.checkbox("Spring 2", value=True)
        january = st.checkbox("January", value=False)

        st.markdown("")
        st.markdown("👉 [Feedback?](https://forms.gle/dVQtp7XwVhqnv5Dw8)")



    if not january:
        df = df[df['session'] != 'January']
    if not spring_1:
        df = df[df['session'] != 'Spring 1']
    if not spring_2:
        df = df[df['session'] != 'Spring 2']
    if not full_term:
        df = df[df['session'] != 'Full Term']


    def plot_scatterplot(df):
        fig = px.scatter(df, x='mean_rating', y='mean_workload', hover_name="course_name", hover_data=['prof_search', 'mean_rating', 'mean_workload'],
                         labels=dict(prof_search='Professor', mean_rating='Average Professor Rating', mean_workload='Average Professor Workload'))
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
                      x0=3.72, y0=4.30,
                      x1=3.945, y1=4.45,
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
                      x0=4.79, y0=4.30,
                      x1=5.015, y1=4.45,
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
            y=[2.125, 4.375, 2.125, 4.375],
            text=["Better prof, less effort",
                  "Worse prof, more effort",
                  "Worse prof, less effort",
                  "Better prof, more effort"],
            mode="text",
        ))

        fig.update_xaxes(range=[3.7, 5.025])
        fig.update_yaxes(range=[2, 4.5])
        fig.update_layout(showlegend=False)

        fig.update_layout(uniformtext_minsize=15)
        st.plotly_chart(fig)

    st.header("🗓️ Compare Spring 2023 Courses at HKS")
    st.info("""
    - See courses based on instructor **quality** (horizontal axis) and **workload** (vertical axis), using data from 3,000+ course evaluations on KNET 
    - Each point represents the **average score** the professor has received across all courses taught
    - Explore **all** courses or search **specific** courses, then hover over the points to see course scores
    """)
    plot_scatterplot(df)

    df.sort_values(by='mean_rating', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    st.header("🥇 Courses Ranked by  Professor's Average Rating")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    df_with_previous = df[['course_name', 'professor', 'mean_rating', 'mean_workload', 'session', 'days', 'time', 'course_id', 'course_description', 'url']].sort_values(by=['mean_rating', 'mean_workload'], ascending=[False, True]).reset_index(drop=True)
    st.write(df_with_previous.dropna(subset=['mean_rating']))

    st.header("📈 New Professors")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    st.write(df_with_previous[df_with_previous['mean_rating'].isna()].reset_index(drop=True))

    # for index, row in df.iterrows():
    #     st.markdown(f"**{index+1}. {row['course_name']}**")
    #     st.markdown(
    #         f"""
    #         - *ID:* {row['course_id']}
    #         - *Professor:* {row['professor']}
    #         - *Session:* {row['session']}
    #         - *Time:* {row['days']} {row['time']}
    #         - *Avg. Instructor Rating:* {row['mean_rating']}
    #         - *Avg. Instructor Workload:* {row['mean_workload']}
    #         - *Description:* {row['course_description']}. . . .
    #         """
    #     )




    #
    # def set_page_container_style(
    #         max_width: int = 1100, max_width_100_percent: bool = False,
    #         padding_top: int = 1, padding_right: int = 10, padding_left: int = 10, padding_bottom: int = 10,
    #         color: str = COLOR, background_color: str = BACKGROUND_COLOR,
    # ):
    #     if max_width_100_percent:
    #         max_width_str = f'max-width: 100%;'
    #     else:
    #         max_width_str = f'max-width: {max_width}px;'
    #     st.markdown(
    #         f'''
    #             <style>
    #                 .reportview-container .sidebar-content {{
    #                     padding-top: {padding_top}rem;
    #                 }}
    #                 .reportview-container .main .block-container {{
    #                     {max_width_str}
    #                     padding-top: {padding_top}rem;
    #                     padding-right: {padding_right}rem;
    #                     padding-left: {padding_left}rem;
    #                     padding-bottom: {padding_bottom}rem;
    #                 }}
    #                 .reportview-container .main {{
    #                     color: {color};
    #                     background-color: {background_color};
    #                 }}
    #             </style>
    #             ''',
    #         unsafe_allow_html=True,
    #     )
    #
    #
    # def plot_scatterplot(x, y):
    #     # create a new figure
    #     plt.figure()
    #     # plot the scatterplot
    #     plt.scatter(x, y)
    #     # fit a linear regression model
    #     model = LinearRegression()
    #     model.fit(x[:, np.newaxis], y)
    #     # predict y values using the model
    #     y_pred = model.predict(x[:, np.newaxis])
    #     # plot the line of best fit
    #     plt.plot(x, y_pred, color='r')
    #     # show the plot
    #     st.pyplot()
    #
    # df = pd.read_csv("./course_evaluations_all.csv")
    #
    # with st.sidebar:
    #     st.title("Compare HKS Professors")  # add a title
    #     professor_1 = st.text_input(f"Professor 1:")
    #
    #     # Filter the database for rows that contain the input string
    #     if professor_1:
    #         filtered_data_1 = df[df["professor"].str.contains(professor_1, case=False)]
    #         options_1 = filtered_data_1["professor"].unique()
    #     else:
    #         options_1 = df["professor"].unique()
    #
    #     professor_1_data = df[df["professor"].str.contains(professor_1, case=False)]
    #
    #     # Get the selected option from the user
    #     selected_option_1 = st.selectbox("Select an option:", options_1, key="1")
    #
    #     st.write('You selected:', selected_option_1)
    #     st.write('\n')
    #
    #     professor_2 = st.text_input(f"Professor 2:")
    #
    #     # Filter the database for rows that contain the input string
    #     if professor_1:
    #         filtered_data_1 = df[df["professor"].str.contains(professor_2, case=False)]
    #         options_2 = filtered_data_1["professor"].unique()
    #     else:
    #         options_2 = df["professor"].unique()
    #
    #     professor_2_data = df[df["professor"].str.contains(professor_2, case=False)]
    #
    #     # Get the selected option from the user
    #     selected_option_2 = st.selectbox("Select an option:", options_2, key="2")
    #
    #     st.write('You selected:', selected_option_2)
    #     st.write('\n')
    #
    #     professor_3 = st.text_input(f"Professor 3:")
    #
    #     # Filter the database for rows that contain the input string
    #     if professor_3:
    #         filtered_data_3 = df[df["professor"].str.contains(professor_3, case=False)]
    #         options_3 = filtered_data_3["professor"].unique()
    #     else:
    #         options_3 = df["professor"].unique()
    #
    #     professor_3_data = df[df["professor"].str.contains(professor_3, case=False)]
    #
    #     # Get the selected option from the user
    #     selected_option_3 = st.selectbox("Select an option:", options_3, key="3")
    #
    #     st.write('You selected:', selected_option_3)
    #     st.write('\n')
    #
    # columns = ["How would you rate this instructor overall?",
    #            "How great is the workload in this course compared with your other Kennedy School courses?"]
    #
    # options = [selected_option_1, selected_option_2, selected_option_3]
    # comparison_df = df[df['professor'].isin(options)]
    # comparison_data = comparison_df.groupby('professor').mean()[columns]
    # comparison_data.columns = ['Instructor', 'Workload']
    # comparison_data.sort_values(by='Instructor', ascending=False, inplace=True)
    #
    # st.markdown("**Instructor and Workload Scores (Ranked from Highest to Lowest Instructor Score)**")
    # chart = px.bar(
    #     comparison_data,
    #     barmode="group",
    # )
    # chart.update_layout(height=600, width=1000)
    # # Display the chart
    # st.plotly_chart(chart)
    #
    # # st.write(comparison_df["professor",
    # #              "How would you rate this instructor overall?",
    # #              "How great is the workload in this course compared with your other Kennedy School courses?"])
    # compare = comparison_df[["professor", "year", 'course_name', "How would you rate this instructor overall?", "How great is the workload in this course compared with your other Kennedy School courses?"]].sort_values(by='professor')
    # compare.columns = ["prof", "year", "course", "instructor", "workload"]
    #
    # def plot_scatterplot_and_line_of_best_fit(df, prof, year_col, rating_col):
    #     st.write(f"**{prof}**")
    #     df = df[df['prof']==prof]
    #     fig = px.scatter(df, x=year_col, y=rating_col, trendline='ols', color='course', trendline_scope = 'overall')
    #     fig.update_layout(width=900)
    #     st.plotly_chart(fig)
    #
    #
    # for prof in compare['prof'].unique()[::-1]:
    #     plot_scatterplot_and_line_of_best_fit(compare, prof, 'year', 'instructor')
    #
    # st.markdown("**#Data**")
    # st.write(compare.sort_values(by=['prof', 'year']))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# Commit instructions: https://www.youtube.com/watch?v=ONaPg5QKC8Q
