from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def load_employee_data():
    """Simulate loading employee skill data"""
    return pd.DataFrame(
        {
            "employee_id": range(1, 11),
            "name": [
                "John Smith",
                "Alice Johnson",
                "Bob Wilson",
                "Carol Brown",
                "David Lee",
                "Emma Davis",
                "Frank Miller",
                "Grace Taylor",
                "Henry Adams",
                "Ivy Chen",
            ],
            "primary_skills": [
                "Python,ML,Data Analysis",
                "Project Management,Agile,Leadership",
                "Java,Cloud,DevOps",
                "UI/UX,Frontend,React",
                "Data Science,Python,Statistics",
                "Backend,Python,Database",
                "ML,Deep Learning,PyTorch",
                "Frontend,JavaScript,Vue",
                "Cloud,AWS,Infrastructure",
                "Full Stack,Python,JavaScript",
            ],
            "experience_years": [5, 8, 6, 4, 7, 5, 6, 3, 9, 4],
            "current_project": [
                "Project A",
                "Project B",
                None,
                "Project C",
                None,
                "Project A",
                "Project B",
                None,
                "Project C",
                "Project A",
            ],
            "availability_date": pd.date_range(
                start=datetime.now(), periods=10, freq="W"
            ).date,
        }
    )


def main():
    st.title("🎯 AI Skill Matcher")

    tabs = st.tabs(["🔍 Project Staffing", "👥 Employee Skills", "📊 Skills Analytics"])

    # Load data
    df = load_employee_data()

    with tabs[0]:
        st.header("Project Staffing Assistant")

        # Project requirements input
        with st.form("project_requirements"):
            st.subheader("Enter Project Requirements")
            project_name = st.text_input("Project Name")
            required_skills = st.multiselect(
                "Required Skills",
                [
                    "Python",
                    "ML",
                    "Data Analysis",
                    "Project Management",
                    "Agile",
                    "Java",
                    "Cloud",
                    "DevOps",
                    "UI/UX",
                    "Frontend",
                    "React",
                    "Data Science",
                    "Statistics",
                    "Backend",
                    "Database",
                    "Deep Learning",
                    "PyTorch",
                    "JavaScript",
                    "Vue",
                    "AWS",
                    "Infrastructure",
                    "Full Stack",
                ],
            )
            team_size = st.number_input("Team Size Needed", min_value=1, max_value=10)
            start_date = st.date_input("Project Start Date")

            submitted = st.form_submit_button("Find Matches")

            if submitted and required_skills:
                st.subheader("Recommended Team Members")

                # Simple matching algorithm (in practice, this would be more sophisticated)
                matches = []
                for _, employee in df.iterrows():
                    skills = set(employee["primary_skills"].split(","))
                    match_score = len(set(required_skills) & skills) / len(
                        required_skills
                    )
                    if match_score > 0:
                        matches.append(
                            {
                                "name": employee["name"],
                                "match_score": match_score,
                                "available": employee["current_project"] is None,
                                "experience": employee["experience_years"],
                                "skills": employee["primary_skills"],
                            }
                        )

                matches.sort(
                    key=lambda x: (x["match_score"], x["available"]), reverse=True
                )

                for match in matches[:team_size]:
                    with st.expander(
                        f"👤 {match['name']} - Match Score: {match['match_score']:.0%}"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Skills:", match["skills"])
                            st.write("Experience:", f"{match['experience']} years")
                        with col2:
                            st.write(
                                "Status:",
                                "Available" if match["available"] else "Assigned",
                            )
                            if not match["available"]:
                                st.warning("⚠️ Currently assigned to another project")

    with tabs[1]:
        st.header("Employee Skills Database")

        # Search and filter
        search = st.text_input("Search Employees")
        filtered_df = df[df["name"].str.contains(search, case=False)] if search else df

        # Display employee profiles
        for _, employee in filtered_df.iterrows():
            with st.expander(f"👤 {employee['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Skills:", employee["primary_skills"])
                    st.write("Experience:", f"{employee['experience_years']} years")
                with col2:
                    st.write(
                        "Current Project:",
                        employee["current_project"]
                        if employee["current_project"]
                        else "Available",
                    )
                    st.write("Available from:", employee["availability_date"])

    with tabs[2]:
        st.header("Skills Analytics")

        # Skill distribution
        all_skills = []
        for skills in df["primary_skills"]:
            all_skills.extend(skills.split(","))

        skill_counts = pd.Series(all_skills).value_counts()

        fig_skills = px.bar(
            x=skill_counts.index,
            y=skill_counts.values,
            title="Skill Distribution in Organization",
        )
        st.plotly_chart(fig_skills)

        # Experience distribution
        fig_exp = px.histogram(
            df, x="experience_years", title="Experience Distribution", nbins=10
        )
        st.plotly_chart(fig_exp)

        # Project allocation
        project_counts = df["current_project"].value_counts()
        available = project_counts.get(None, 0)
        allocated = len(df) - available

        fig_allocation = go.Figure(
            data=[
                go.Pie(
                    labels=["Allocated", "Available"],
                    values=[allocated, available],
                    hole=0.3,
                )
            ]
        )
        fig_allocation.update_layout(title="Resource Allocation")
        st.plotly_chart(fig_allocation)

        # Key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Employees", len(df))
        with col2:
            st.metric("Available Resources", available)
        with col3:
            st.metric("Unique Skills", len(skill_counts))


if __name__ == "__main__":
    main()
