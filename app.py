# app.py
# This is the entire web application, built with Streamlit.
# Run it with: streamlit run app.py

import streamlit as st
import pandas as pd
from matplotlib.figure import Figure

from database import (
    create_tables, create_user, verify_user,
    add_student, get_all_students, update_student,
    delete_student, search_student
)
from calculations import calculate_result

# ---------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit command)
# ---------------------------------------------------------
st.set_page_config(page_title="Student Performance Dashboard", page_icon="📊", layout="wide")

create_tables()  # make sure database tables exist before anything else runs

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
# Streamlit reruns the ENTIRE script top-to-bottom every time you click
# anything. session_state is how we remember things (like "is the user
# logged in?") ACROSS those reruns — without it, every click would
# forget who's logged in.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


def get_students_dataframe():
    """Fetches all students as a Pandas DataFrame."""
    rows = get_all_students(st.session_state.username)
    columns = [
    "id",
    "username",
    "name",
    "roll_no",
    "subject1",
    "subject2",
    "subject3",
    "total",
    "percentage",
    "grade",
    "result"
]
    return pd.DataFrame(rows, columns=columns)


# ---------------------------------------------------------
# LOGIN / SIGNUP PAGE
# ---------------------------------------------------------
def auth_page():
    st.title("📊 Student Performance Dashboard")

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()  # re-run the script so it now shows the main app
            else:
                st.error("Invalid username or password.")

    with tab_signup:
        st.subheader("Create a new account")
        new_username = st.text_input("Choose a username", key="signup_username")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")

        if st.button("Create Account"):
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success = create_user(new_username, new_password)
                if success:
                    st.success("Account created! Please go to the Login tab to sign in.")
                else:
                    st.error("That username is already taken.")


# ---------------------------------------------------------
# MAIN APP (only shown after login)
# ---------------------------------------------------------
def main_app():
    # ---- Sidebar navigation ----
    st.sidebar.title(f"👋 Welcome, {st.session_state.username}")
    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Dashboard", "➕ Add Student", "📋 Manage Students", "📈 Analytics", "📉 Charts", "📤 Reports"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    if page == "🏠 Dashboard":
        page_home()
    elif page == "➕ Add Student":
        page_add()
    elif page == "📋 Manage Students":
        page_manage()
    elif page == "📈 Analytics":
        page_analytics()
    elif page == "📉 Charts":
        page_charts()
    elif page == "📤 Reports":
        page_reports()


def page_home():
    st.title("Dashboard Overview")
    df = get_students_dataframe()

    total = len(df)
    passed = len(df[df["result"] == "Pass"]) if total > 0 else 0
    failed = total - passed
    average = round(df["percentage"].mean(), 2) if total > 0 else 0

    # st.columns() creates side-by-side boxes, like our old "cards"
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", total)
    col2.metric("Passed", passed)
    col3.metric("Failed", failed)
    col4.metric("Average %", f"{average}%")

    st.subheader("All Students")
    if df.empty:
        st.info("No students added yet.")
    else:
        display_df = df.drop(columns=["username"])
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def page_add():
    st.title("Add Student")

    with st.form("add_student_form", clear_on_submit=True):
        name = st.text_input("Name")
        roll_no = st.text_input("Roll No")
        col1, col2, col3 = st.columns(3)
        subject1 = col1.number_input("Subject 1 Marks", min_value=0, max_value=100, step=1)
        subject2 = col2.number_input("Subject 2 Marks", min_value=0, max_value=100, step=1)
        subject3 = col3.number_input("Subject 3 Marks", min_value=0, max_value=100, step=1)

        submitted = st.form_submit_button("Save Student", type="primary")

        if submitted:
            if not name or not roll_no:
                st.error("Name and Roll No are required.")
            else:
                total, percentage, grade, result = calculate_result(subject1, subject2, subject3)
                add_student(
    st.session_state.username,
    name,
    roll_no,
    subject1,
    subject2,
    subject3,
    total,
    percentage,
    grade,
    result
)
                st.success(f"Student '{name}' added successfully! Grade: {grade}, Result: {result}")


def page_manage():
    st.title("Manage Students")

    keyword = st.text_input("🔍 Search by name or roll no")
    students = (
    search_student(st.session_state.username, keyword)
    if keyword
    else get_all_students(st.session_state.username)
)

    if not students:
        st.info("No students found.")
        return

    # Build a dropdown of "Name (Roll No)" so the user can pick a student to edit/delete
    options = {f"{s[2]} (Roll No: {s[3]})": s for s in students}
    df = pd.DataFrame(
    students,
    columns=[
        "id",
        "username",
        "name",
        "roll_no",
        "subject1",
        "subject2",
        "subject3",
        "total",
        "percentage",
        "grade",
        "result",
    ],
)
    display_df = df.drop(columns=["username"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.subheader("Edit or Delete a Student")
    selected_label = st.selectbox("Select a student", list(options.keys()))
    selected = options[selected_label]  # the full row tuple


    with st.form("edit_student_form"):

        name = st.text_input("Name", value=selected[2])
        roll_no = st.text_input("Roll No", value=selected[3])

        col1, col2, col3 = st.columns(3)

        subject1 = col1.number_input("Subject 1 Marks", min_value=0, max_value=100, value=int(selected[4]))
        subject2 = col2.number_input("Subject 2 Marks", min_value=0, max_value=100, value=int(selected[5]))
        subject3 = col3.number_input("Subject 3 Marks", min_value=0, max_value=100, value=int(selected[6]))

        col_a, col_b = st.columns(2)

        with col_a:
            update_clicked = st.form_submit_button("Update Student", type="primary")

        with col_b:
            delete_clicked = st.form_submit_button("Delete Student")

        if update_clicked:
            total, percentage, grade, result = calculate_result(subject1, subject2, subject3)
            update_student(
                selected[0], name, roll_no,
                subject1, subject2, subject3,
                total, percentage, grade, result
            )
            st.success("Student updated successfully!")
            st.rerun()

        if delete_clicked:
            delete_student(selected[0])
            st.success("Student deleted successfully!")
            st.rerun()

def page_analytics():
    st.title("Analytics")
    df = get_students_dataframe()

    if df.empty:
        st.info("No student data yet. Add some students first.")
        return

    grade_counts = df["grade"].value_counts()
    subject_averages = {
        "Subject 1": round(df["subject1"].mean(), 2),
        "Subject 2": round(df["subject2"].mean(), 2),
        "Subject 3": round(df["subject3"].mean(), 2),
    }
    top_row = df.loc[df["percentage"].idxmax()]
    bottom_row = df.loc[df["percentage"].idxmin()]
    pass_percentage = round((len(df[df["result"] == "Pass"]) / len(df)) * 100, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Top Scorer", f'{top_row["name"]}', f'{top_row["percentage"]}%')
    col2.metric("Lowest Scorer", f'{bottom_row["name"]}', f'{bottom_row["percentage"]}%')
    col3.metric("Overall Pass %", f"{pass_percentage}%")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Grade Distribution")
        st.dataframe(grade_counts.rename("Count"), use_container_width=True)
    with col_b:
        st.subheader("Subject-wise Average Marks")
        st.dataframe(pd.Series(subject_averages, name="Average"), use_container_width=True)


def page_charts():
    st.title("Charts")
    df = get_students_dataframe()

    if df.empty:
        st.info("No student data yet. Add some students first.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = Figure(figsize=(4, 3.5))
        ax = fig.add_subplot(111)
        grade_counts = df["grade"].value_counts().sort_index()
        ax.bar(grade_counts.index, grade_counts.values, color="#1E3A8A")
        ax.set_title("Grade Distribution", fontsize=10)
        fig.tight_layout()
        st.pyplot(fig)

    with col2:
        fig = Figure(figsize=(4, 3.5))
        ax = fig.add_subplot(111)
        result_counts = df["result"].value_counts()
        colors = ["#16A34A" if label == "Pass" else "#DC2626" for label in result_counts.index]
        ax.pie(result_counts.values, labels=result_counts.index, autopct="%1.1f%%", colors=colors)
        ax.set_title("Pass vs Fail", fontsize=10)
        fig.tight_layout()
        st.pyplot(fig)

    with col3:
        fig = Figure(figsize=(4, 3.5))
        ax = fig.add_subplot(111)
        subjects = ["Subject 1", "Subject 2", "Subject 3"]
        averages = [df["subject1"].mean(), df["subject2"].mean(), df["subject3"].mean()]
        ax.bar(subjects, averages, color="#3B82F6")
        ax.set_ylim(0, 100)
        ax.set_title("Subject-wise Average", fontsize=10)
        fig.tight_layout()
        st.pyplot(fig)


def page_reports():
    st.title("Reports")
    df = get_students_dataframe()

    if df.empty:
        st.info("No students to export yet.")
        return

    st.write("Click below to download all student records as a CSV file.")
    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Export to CSV",
        data=csv_data,
        file_name="student_report.csv",
        mime="text/csv",
        type="primary"
    )


# ---------------------------------------------------------
# ROUTING: show login page or main app based on session state
# ---------------------------------------------------------
if st.session_state.logged_in:
    main_app()
else:
    auth_page()
