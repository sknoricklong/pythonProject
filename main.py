import pandas as pd
import streamlit as st
import os
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import statsmodels

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    BACKGROUND_COLOR = 'white'
    COLOR = 'black'


    def set_page_container_style(
            max_width: int = 1100, max_width_100_percent: bool = False,
            padding_top: int = 1, padding_right: int = 10, padding_left: int = 10, padding_bottom: int = 10,
            color: str = COLOR, background_color: str = BACKGROUND_COLOR,
    ):
        if max_width_100_percent:
            max_width_str = f'max-width: 100%;'
        else:
            max_width_str = f'max-width: {max_width}px;'
        st.markdown(
            f'''
                <style>
                    .reportview-container .sidebar-content {{
                        padding-top: {padding_top}rem;
                    }}
                    .reportview-container .main .block-container {{
                        {max_width_str}
                        padding-top: {padding_top}rem;
                        padding-right: {padding_right}rem;
                        padding-left: {padding_left}rem;
                        padding-bottom: {padding_bottom}rem;
                    }}
                    .reportview-container .main {{
                        color: {color};
                        background-color: {background_color};
                    }}
                </style>
                ''',
            unsafe_allow_html=True,
        )


    def plot_scatterplot(x, y):
        # create a new figure
        plt.figure()
        # plot the scatterplot
        plt.scatter(x, y)
        # fit a linear regression model
        model = LinearRegression()
        model.fit(x[:, np.newaxis], y)
        # predict y values using the model
        y_pred = model.predict(x[:, np.newaxis])
        # plot the line of best fit
        plt.plot(x, y_pred, color='r')
        # show the plot
        st.pyplot()

    df = pd.read_csv("./course_evaluations_all.csv")

    with st.sidebar:
        st.title("Compare HKS Professors")  # add a title
        professor_1 = st.text_input(f"Professor 1:")

        # Filter the database for rows that contain the input string
        if professor_1:
            filtered_data_1 = df[df["professor"].str.contains(professor_1, case=False)]
            options_1 = filtered_data_1["professor"].unique()
        else:
            options_1 = df["professor"].unique()

        professor_1_data = df[df["professor"].str.contains(professor_1, case=False)]

        # Get the selected option from the user
        selected_option_1 = st.selectbox("Select an option:", options_1, key="1")

        st.write('You selected:', selected_option_1)
        st.write('\n')

        professor_2 = st.text_input(f"Professor 2:")

        # Filter the database for rows that contain the input string
        if professor_1:
            filtered_data_1 = df[df["professor"].str.contains(professor_2, case=False)]
            options_2 = filtered_data_1["professor"].unique()
        else:
            options_2 = df["professor"].unique()

        professor_2_data = df[df["professor"].str.contains(professor_2, case=False)]

        # Get the selected option from the user
        selected_option_2 = st.selectbox("Select an option:", options_2, key="2")

        st.write('You selected:', selected_option_2)
        st.write('\n')

        professor_3 = st.text_input(f"Professor 3:")

        # Filter the database for rows that contain the input string
        if professor_3:
            filtered_data_3 = df[df["professor"].str.contains(professor_3, case=False)]
            options_3 = filtered_data_3["professor"].unique()
        else:
            options_3 = df["professor"].unique()

        professor_3_data = df[df["professor"].str.contains(professor_3, case=False)]

        # Get the selected option from the user
        selected_option_3 = st.selectbox("Select an option:", options_3, key="3")

        st.write('You selected:', selected_option_3)
        st.write('\n')

    columns = ["How would you rate this instructor overall?",
               "How great is the workload in this course compared with your other Kennedy School courses?"]

    options = [selected_option_1, selected_option_2, selected_option_3]
    comparison_df = df[df['professor'].isin(options)]
    comparison_data = comparison_df.groupby('professor').mean()[columns]
    comparison_data.columns = ['Instructor', 'Workload']
    comparison_data.sort_values(by='Instructor', ascending=False, inplace=True)

    st.markdown("**Instructor and Workload Scores (Ranked from Highest to Lowest Instructor Score)**")
    chart = px.bar(
        comparison_data,
        barmode="group",
    )
    chart.update_layout(height=600, width=1000)
    # Display the chart
    st.plotly_chart(chart)

    # st.write(comparison_df["professor",
    #              "How would you rate this instructor overall?",
    #              "How great is the workload in this course compared with your other Kennedy School courses?"])
    compare = comparison_df[["professor", "year", 'course_name', "How would you rate this instructor overall?", "How great is the workload in this course compared with your other Kennedy School courses?"]].sort_values(by='professor')
    compare.columns = ["prof", "year", "course", "instructor", "workload"]

    def plot_scatterplot_and_line_of_best_fit(df, prof, year_col, rating_col):
        st.write(f"**{prof}**")
        df = df[df['prof']==prof]
        fig = px.scatter(df, x=year_col, y=rating_col, trendline='ols', color='course', trendline_scope = 'overall')
        st.plotly_chart(fig)


    for prof in compare['prof'].unique()[::-1]:
        plot_scatterplot_and_line_of_best_fit(compare, prof, 'year', 'instructor')

    st.markdown("**#Data**")
    st.write(compare.sort_values(by=['prof', 'year']))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# Commit instructions: https://www.youtube.com/watch?v=ONaPg5QKC8Q
