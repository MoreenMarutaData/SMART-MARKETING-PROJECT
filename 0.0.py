import pandas as pd
import numpy as np
import streamlit as st
import re
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import altair as alt
from fontTools.varLib import merger

st.set_option('deprecation.showPyplotGlobalUse', False)

# HEADER CODE
header = st.container()
with header:
    st.header("WELCOME TO MYMOVIES.AFRICA PROJECT")
    col1 = st.columns(1)
    # with col1:
    #     st.header("A cat")
    #     st.image('MyMoviesAfrica_logo_Black_2009201.png')
    image = Image.open('MyMoviesAfrica_logo_Black_2009201.png')
    st.image(image, caption=' ')
    # link = '[TABLEAU](https://public.tableau.com/views/SmartMarketingAnalysisMyMoviesAfrica/Story1?:language=en-US' \
    #        '&publish=yes&:display_count=n&:origin=viz_share_link) '
    # t_link = st.markdown(link, unsafe_allow_html=True)
    # st.write("The link to our Tableau Visualisations: ", t_link)
    # link2 = "https://docs.google.com/presentation/d/1En6jT0-pYGhGKDNTCxu8VMQRl-Rk3TzLQqf6CA8rY6o/" \
    #         "edit#slide=id.g10da8e4a416_0_130"
    # p_link = st.markdown(link2)
    # st.write("The link ti the presentation slides: ", p_link)

# SIDE BAR
# uploaded_file = st.sidebar.file_uploader("Choose a file")
# if uploaded_file is not None:
#    customertrans = pd.read_csv(uploaded_file)
# customertrans = pd.read_csv("customertrans.csv")

# LOAD FIRST DATASET
customertrans = pd.read_csv("customertrans.csv")

# LOAD 2ND DATASET
movie_titles = pd.read_csv("TitlesUsers.csv")

# LOAD THE 3RD DATASET
transactions_df = customertrans.copy()

# DATA PREPARATION
chars_to_remove = ['st', 'nd', 'rd', 'th']
regular_expression = '[' + re.escape(''.join(chars_to_remove)) + ']'
customertrans['new_date'] = customertrans['Date'].str.replace(regular_expression, '', regex=True)
customertrans[['day', 'month']] = customertrans["new_date"].str.split(" ", 1, expand=True)
customertrans["month"] = customertrans["month"].str.strip(" ")
customertrans[['month_name', 'year']] = customertrans["month"].str.split(" ", 1, expand=True)
customertrans["year"] = customertrans["year"].str.strip(" ")
values_dict = {'Ja': 1, 'Feb': 2, 'Ma': 3, 'Ap': 4, 'May': 5, 'Ju': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oc': 10,
               'Nov': 11, 'Dec': 12}


def map_values(row, values_dict):
    return values_dict[row]


customertrans['month_numb'] = customertrans['month_name'].apply(map_values, args=(values_dict,))
customertrans[['day', 'month_numb']] = np.round(customertrans[['day', 'month_numb']], 2)
customertrans = customertrans[['Invoice No.', 'Customer', 'Gender', 'Title', 'Transaction Type',
                               'Amount (KES)', 'Date', 'Time', 'Platform', 'Country', 'day', 'month_numb', 'year']]
customertrans['new_date'] = customertrans['month_numb'].astype(str) + '-' + customertrans['day'].astype(str) \
                            + '-' + customertrans['year']
customertrans['new_date'] = pd.to_datetime(customertrans['new_date'])
customertrans['day_of_the_week'] = customertrans['new_date'].dt.day_name()

customertrans['Platform'] = customertrans['Platform'].replace("Windows 10", "Windows")
customertrans['Platform'] = customertrans['Platform'].replace("Windows 8", "Windows")
customertrans['Platform'] = customertrans['Platform'].replace("Windows 8.1", "Windows")
customertrans['Platform'] = customertrans['Platform'].replace("Windows 7", "Windows")
customertrans['Platform'] = customertrans['Platform'].replace("Windows Vista", "Windows")

df2020 = customertrans[customertrans['year'] == "2020"]
df2021 = customertrans[customertrans['year'] == "2021"]

# Male datasets
male2020 = df2020[df2020['Gender'] == "M"]
male2021 = df2021[df2021['Gender'] == "M"]

# Female datasets
female2020 = df2020[df2020['Gender'] == "F"]
female2021 = df2021[df2021['Gender'] == "F"]


# FUNCTIONS
def sales_per_week(year, week):
    # acquiring a dataframe of choice
    #
    choice = (transactions_df['year'].isin([year])) & (transactions_df['WeekNumber'].isin([week]))
    new_df = transactions_df[choice]
    # acquiring the total sales
    #
    total_sales = new_df['Amount (KES)'].sum()
    # sales based on gender
    #  as well as occurrence of the purchases based on the gender
    #
    males = new_df['Gender'].isin(['M'])
    male_transactions = new_df[males]
    number_of_male_sales = male_transactions['Gender'].value_counts().sum()
    male_sales = male_transactions['Amount (KES)'].sum()
    females = new_df['Gender'].isin(['F'])
    female_transactions = new_df[females]
    number_of_female_sales = female_transactions['Gender'].value_counts().sum()
    female_sales = female_transactions['Amount (KES)'].sum()
    # counts of the content sold
    #
    content_most_sold = new_df['Title'].value_counts()
    content_most_sold_df = pd.DataFrame(content_most_sold)
    # acquiring the daily sales according to the week entered
    #
    daily_sales = new_df.groupby('Date').sum()
    daily_sales = daily_sales[['Amount (KES)']]
    new_df2 = new_df.groupby(['Date', 'day_of_the_week'])['Amount (KES)'].sum().reset_index()
    new_df2 = pd.DataFrame(new_df2, index=None)
    st.title('Trend of Sales')
    Sales = transactions_df.groupby('Date')['Amount (KES)'].sum()
    Sales = pd.DataFrame(Sales)
    st.write('\n')
    st.line_chart(Sales)
    st.write('\n')
    st.title('Weekly Analysis')
    st.write('\n')
    st.write('\n')
    st.subheader('Total Sales For The Week \n')
    st.write("**The total sales for this week amounts to:** ", total_sales, " shillings")
    st.subheader('Number Of Movie Sales\n')
    st.write("Counts of the movies sold are in this order :")
    st.write('\n')
    st.write(content_most_sold)
    st.write('\n')
    st.subheader('Sales Based on Gender \n')
    if male_sales > female_sales:
        st.write(number_of_male_sales, " ***males*** bought a movie this week compared to ", number_of_female_sales,
                 " ***females*** who bought a movie this week. The total sales for the male gender was higher this week. It amounted to ksh: ",
                 male_sales)
    else:
        st.write(number_of_female_sales, " ***females*** bought a movie this week compared to ", number_of_male_sales,
                 " ***males*** bought a movie this week. The total sales for the male gender was higher this week. It amounted to ksh: ",
                 female_sales)
    st.write('\n')
    viz = alt.Chart(new_df).mark_bar().encode(x=alt.X('day_of_the_week', sort=None), y='Amount (KES)', color='Gender')
    viz = viz.properties(width=alt.Step(50))
    st.write(viz)
    # st.write('\n')
    # st.write(daily_sales)
    # st.write('\n')
    # st.write(new_df2)
    # st.write('\n')
    st.subheader('Daily sales for the week')
    st.write('\n')
    c = alt.Chart(new_df2).mark_bar().encode(x=alt.X('day_of_the_week'), y='Amount (KES)')
    c = c.properties(width=alt.Step(50))
    st.write(c)
    st.write('\n')
    st.subheader('Trend of sales for the week')
    st.line_chart(daily_sales)
    st.button('Re-run')


def piechart(df, col, colabels):
    data = df[col]
    labels = df[colabels]
    colors = ['gold', 'maroon']
    explode = (0.1, 0)
    fig = plt.figure(figsize=(5, 5))
    plt.pie(data, labels=labels, colors=colors, explode=explode, autopct='%.0f%%', startangle=60)
    plt.title("Percentage of Gender Distribution Per Year")
    plt.show()


def percentage(df, col):
    df['percent'] = ((df[col] /
                      df[col].sum()) * 100).round(1)

    return df


def barplot(df, labels, values):
    sns.set_style("whitegrid")
    bar, ax = plt.subplots(figsize=(10, 6))
    # x = customertrans0['day_of_the_week']
    # y = customertrans0['percent']
    ax = sns.barplot(x=labels, y=values, data=df, ci=None, palette="bright", orient='v', )
    ax.set_title("Percentage Distribution", fontsize=15)
    # ax.set_xlabel ()
    ax.set_ylabel("Percentage")
    # calculate the percentages and annotate the sns barplot
    for rect in ax.patches:
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), "%.1f%%" % rect.get_height(), weight='bold')
    bar.savefig("Seaborn_Pie_Chart.png");


def avgrpu_fun(df, col):
    df['Average'] = ((df[col] /
                      len(df[col])) * 100).round(1)

    return df


# CONTINUATION
side_bar = st.sidebar.radio("MENU", ["Yearly Analysis", "Weekly Analysis"])

# YEARLY ANALYSIS
if side_bar == "Yearly Analysis":
    year = st.sidebar.radio("Select year ", [2020, 2021, "Both 2020 & 2021"])
    if year == 2020:
        # 2020 GENDER

        gender20 = df2020.groupby("Gender")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        gender20
        percentage(gender20, "Count")
        piechart_gender = piechart(gender20, 'percent', 'Gender')
        st.write("This figure shows the distribution of females that engaged with My MoviesAfrica in the year 2020")
        st.pyplot(piechart_gender)

        # 2020 COUNTRIES
        newdf = customertrans.drop_duplicates(subset="Customer", inplace=False)
        newdf20 = df2020.drop_duplicates(subset="Customer", inplace=False)
        country20 = newdf20.groupby("Country")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        country20
        percentage(country20, "Count")
        st.write("This figure shows the countries that brought in most traffic to MYMOVIESAFRICA IN 2020")
        st.pyplot(barplot(country20, "Country", "percent"))

        # 2020 PLATFORMS
        customertrans['Platform'].unique()
        platforms20 = df2020.groupby("Platform")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        platforms20
        percentage(platforms20, "Count")
        st.write("This is the distribution of devices that brought traffic to MYMOVIESAFRICA worldwide.")
        st.write("Most of the users had android devices")
        st.pyplot(barplot(platforms20, "Platform", "percent"))

        # AVERAGE TRANSACTIONS BY DAY
        # Per Day

        customertrans0 = df2020.groupby("day_of_the_week")['Amount (KES)'].sum().reset_index(
            name="Total_Paid").sort_values(by="Total_Paid", ascending=False)
        customertrans0
        percentage(customertrans0, "Total_Paid")
        st.write("This shows the average user traffic by day for the year 2020")
        st.pyplot(barplot(customertrans0, "day_of_the_week", "percent"))

        # # Percentage of most Popular Genres/Film per Year in 2020, 2021 and Combined
        # genre = pd.read_csv("/content/genre.csv", encoding='latin')
        # genre.head(5)
        # percentage(genre, "listorder")
        # genre = genre.sort_values(by="listorder", ascending=False)
    #
    if year == 2021:
        # GENDER
        df2021 = customertrans[customertrans['year'] == "2021"]
        gender21 = df2021.groupby("Gender")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        # gender21
        percentage(gender21, "Count")
        st.write("Compared to 2020, in 2021 we observed more male traffic on MYMOVIES.AFRICA raising the "
                 "distribution to 43% from 32%.")
        st.pyplot(piechart(gender21, 'percent', 'Gender'))

        # 2021 COUNTRIES
        newdf21 = df2021.drop_duplicates(subset="Customer", inplace=False)
        country21 = newdf21.groupby("Country")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        country21
        percentage(country21, "Count")
        st.write("In 2021, we observed more traffic from African Countires like Rwanda unlike 2020.")
        st.write("Kenya still had the highest user engagement on MYMOVIES.AFRICA IN 2021.")
        st.pyplot(barplot(country21.head(5), "Country", "percent"))

        # 2021 PLATFORMS
        platforms21 = df2021.groupby("Platform")['Invoice No.'].count().reset_index(name="Count").sort_values(
            by="Count", ascending=False)
        platforms21
        percentage(platforms21, "Count")
        st.write("Android still topped in 2021 but we noticed a surge of customers using Windows Platform "
                 "as it came second")
        st.write("The unknown platform also had an increase user surge of 9%")
        st.write("While Mac Os had an increase of 12% ")
        st.pyplot(barplot(platforms21, "Platform", "percent"))

        # 2021 TRANSACTIONS
        customertrans1 = df2021.groupby("day_of_the_week")['Amount (KES)'].sum().reset_index(
            name="Total_Paid").sort_values(by="Total_Paid", ascending=False)
        customertrans1
        percentage(customertrans1, "Total_Paid")
        st.write("Just as observed in 2020, on an average, most daily transactions occur on Sundays")
        st.write("From the trend in two years, it's accurate to say that MYMOVIES.AFRICA gets most"
                 " traffic on weekends")
        st.pyplot(barplot(customertrans1, "day_of_the_week", "percent"))

        # GENRES
    else:
        newdf = customertrans.drop_duplicates(subset="Customer", inplace=False)
        # GENDER
        gender = customertrans.groupby("Gender")['Invoice No.'].count().reset_index(name="Count").sort_values(
            by="Count", ascending=False)
        # gender
        percentage(gender, "Count")
        st.write("For both years, we observed that MYMOVIES.AFRICA gets more traffic from females than males by 30%.")
        st.pyplot(piechart(gender, 'percent', 'Gender'))

        # COUNTRIES
        country = newdf.groupby("Country")['Invoice No.'].count().reset_index(name="Count") \
            .sort_values(by="Count", ascending=False)
        country
        percentage(country, "Count")
        st.write("Most users of MYMOVIES.AFRICA are from Kenya followed by Rwanda.")
        st.pyplot(barplot(country.head(5), "Country", "percent"))

# LOAD THE 3RD DATASET COPY FOR WEEKLY ANALYSIS
transactions_df = transactions_df[['Invoice No.', 'Customer', 'Gender', 'Title',
                                   'Transaction Type', 'Amount (KES)', 'Date', 'Time', 'Platform',
                                   'Country', 'day', 'month_numb', 'year', 'day_of_the_week']]
# DATA PREPARATION
transactions_df["Date"] = pd.to_datetime(transactions_df["Date"])
transactions_df = transactions_df.set_index('Date')
transactions_df = transactions_df.sort_index()
transactions_df['WeekNumber'] = transactions_df.index.week
st.dataframe(transactions_df.head())


# WEEKLY ANALYSIS FUNCTION
def analyse():
    if side_bar == "Weekly Analysis":
        year = st.sidebar.radio("Select year ", [2020, 2021])
        # if year == 2020:
        week = st.sidebar.selectbox("Select a week ", range(1, 54, 1))
        a = year
        b = week
        return sales_per_week(a, b)


# if week == range(1, 54, 1):
analyse()
