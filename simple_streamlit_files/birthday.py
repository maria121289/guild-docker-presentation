import calendar
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# Configuration
DATA_PATH = r"C:\Users\MariaAlexiou\streamlit\AI Team Birthday - Sheet1.csv"


def load_birthday_data():
    """Load and prepare birthday data from CSV file."""
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")

        # Convert DD-MM birthday strings to datetime for current year
        current_year = datetime.now().year
        df["birthday_date"] = pd.to_datetime(
            df["birthday"] + f"-{current_year}", format="%d-%m-%Y"
        )

        # If birthday has passed this year, add one year for comparison
        today = pd.Timestamp.now()
        mask = df["birthday_date"] < today
        df.loc[mask, "birthday_date"] = df.loc[mask, "birthday_date"] + pd.DateOffset(
            years=1
        )

        return df
    except FileNotFoundError:
        st.error(f"Birthday data file not found at: {DATA_PATH}")
        st.info("""
            Please ensure your CSV file exists and has the following columns:
            - name: Team member's name
            - birthday: Birthday in DD-MM format
            
            Example:
            ```
            name,birthday
            John Doe,15-05
            Jane Smith,03-12
            ```
        """)
        return None
    except Exception as e:
        st.error(f"Error loading birthday data: {str(e)}")
        return None


def get_next_birthdays(df, n=5):
    """Get the next n birthdays."""
    return df.sort_values("birthday_date").head(n)


def calculate_days_until_birthday(birthday_date):
    """Calculate days until next birthday."""
    today = pd.Timestamp.now()
    days = (birthday_date - today).days
    return days


def search_team_member(df, query):
    """Search for team members by name."""
    return df[df["name"].str.contains(query, case=False)]


def create_birthday_distribution_chart(df):
    """Create a bar chart showing birthday distribution by month."""
    monthly_dist = df["birthday_date"].dt.month.value_counts().sort_index()
    monthly_dist.index = monthly_dist.index.map(lambda x: calendar.month_name[x])

    fig = px.bar(
        x=monthly_dist.index,
        y=monthly_dist.values,
        labels={"x": "Month", "y": "Number of Birthdays"},
        title="Birthday Distribution by Month",
    )
    return fig


def main():
    st.title("🎂 Team Birthday Tracker")

    # Load data from backend
    df = load_birthday_data()

    if df is not None:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📅 Next Birthdays", "🔍 Search", "📊 Statistics"])

        with tab1:
            st.header("Upcoming Birthdays")
            n_birthdays = st.slider("Number of upcoming birthdays to show", 1, 10, 5)
            next_bdays = get_next_birthdays(df, n_birthdays)

            for _, row in next_bdays.iterrows():
                days_until = calculate_days_until_birthday(row["birthday_date"])

                st.markdown(
                    f"""
                    ### {row['name']}
                    - 🗓️ Birthday: {row['birthday_date'].strftime('%d %B')}
                    - ⏳ Days until birthday: {days_until}
                    ---
                    """
                )

        with tab2:
            st.header("Search Team Member")
            search_query = st.text_input("Enter name to search:")

            if search_query:
                results = search_team_member(df, search_query)
                if not results.empty:
                    for _, row in results.iterrows():
                        days_until = calculate_days_until_birthday(row["birthday_date"])

                        st.markdown(
                            f"""
                            ### {row['name']}
                            - 🎂 Birthday: {row['birthday_date'].strftime('%d %B')}
                            - ⏳ Days until next birthday: {days_until}
                            ---
                            """
                        )
                else:
                    st.warning("No team members found matching your search.")

        with tab3:
            st.header("Birthday Statistics")

            # Display total number of team members
            st.metric("Total Team Members", len(df))

            # Show birthday distribution chart
            st.plotly_chart(create_birthday_distribution_chart(df))

            # Show monthly distribution
            st.subheader("Birthdays by Month")
            monthly_count = df["birthday_date"].dt.month.value_counts().sort_index()
            for month_num, count in monthly_count.items():
                month_name = calendar.month_name[month_num]
                st.write(f"- {month_name}: {count} birthdays")


if __name__ == "__main__":
    main()
