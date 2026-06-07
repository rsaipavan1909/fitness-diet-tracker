import streamlit as st
from datetime import date

from database import (
    create_user,
    login_user,
    add_workout,
    add_diet,
    get_workouts,
    get_diet,
    update_workouts,
    update_diet,
)

st.set_page_config(
    page_title="Fitness & Diet Tracker",
    page_icon="🏋️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
        color: #1f2937 !important;
    }

    .info-box {
        background-color: #f3f6fb !important;
        color: #1f2937 !important;
        padding: 14px 18px;
        border-radius: 10px;
        border: 1px solid #e1e7f0;
        margin-bottom: 18px;
    }

    .info-box b {
        color: #0b57d0 !important;
    }

    .readonly-badge {
        display: inline-block;
        background-color: #eaf2ff !important;
        color: #0b57d0 !important;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    section[data-testid="stSidebar"] button {
        border: 1px solid #d7dee8;
        border-radius: 10px;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        background-color: white;
        color: #1f2937;
    }

    section[data-testid="stSidebar"] button:hover {
        border-color: #0b57d0;
        color: #0b57d0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "menu" not in st.session_state:
    st.session_state.menu = "Weight Record Table"


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.menu = "Weight Record Table"
    st.session_state.edit_mode = False
    st.session_state.confirm_edit = False
    st.session_state.confirm_save = False
    st.rerun()


def auth_screen():
    st.markdown(
        '<div class="main-title">🏋️ Fitness & Diet Tracker</div>',
        unsafe_allow_html=True,
    )
    st.write("Create an account or log in to track your workouts and diet.")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

            if login_btn:
                if not username or not password:
                    st.error("Please enter username and password.")
                else:
                    success, user, message = login_user(username, password)

                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = {
                            "id": str(user["id"]),
                            "name": user["name"],
                            "username": user["username"],
                        }
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    with tab2:
        st.subheader("Sign Up")

        with st.form("signup_form"):
            name = st.text_input("Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            invite_code = st.text_input("Invite Code", type="password")
            signup_btn = st.form_submit_button("Create Account")

            if signup_btn:
                username_clean = username.lower().strip()

                if not name or not username or not password or not confirm_password or not invite_code:
                    st.error("Please fill all fields.")
                elif " " in username_clean:
                    st.error("Username cannot contain spaces.")
                elif len(username_clean) < 3:
                    st.error("Username must be at least 3 characters.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif invite_code != st.secrets["INVITE_CODE"]:
                    st.error("Invalid invite code.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, message = create_user(name, username_clean, password)

                    if success:
                        st.success("Account created. Please log in now.")
                    else:
                        st.error(message)


if not st.session_state.logged_in:
    auth_screen()
    st.stop()


user_id = st.session_state.user["id"]
user_name = st.session_state.user["name"]
username = st.session_state.user["username"]
today = date.today()

st.sidebar.title("🏋️ Fitness & Diet Tracker")
st.sidebar.write(f"Logged in as: **{user_name}**")
st.sidebar.caption(f"Username: `{username}`")

st.sidebar.markdown("### Menu")

if st.sidebar.button("🏋️ Weight Record Table", use_container_width=True):
    st.session_state.menu = "Weight Record Table"

if st.sidebar.button("🍽️ Diet Record Table", use_container_width=True):
    st.session_state.menu = "Diet Record Table"

if st.sidebar.button("📋 Previous Entries", use_container_width=True):
    st.session_state.menu = "Previous Entries"

st.sidebar.divider()

if st.sidebar.button("Logout", use_container_width=True):
    logout()

menu = st.session_state.menu

st.markdown(
    '<div class="main-title">Fitness & Diet Tracker</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="info-box">📅 Date auto-updates daily: <b>{today}</b></div>',
    unsafe_allow_html=True,
)

if menu == "Weight Record Table":
    st.header("Weight Record Table")
    st.write("Enter today's lifting records. The date is automatically added.")

    with st.form("workout_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            exercise = st.text_input("Exercise", placeholder="Bench Press")
        with col2:
            sets = st.number_input("Sets", min_value=1, max_value=20, step=1)
        with col3:
            reps = st.number_input("Reps", min_value=1, max_value=100, step=1)
        with col4:
            weight = st.number_input("Weight", min_value=0.0, step=2.5)

        notes = st.text_area("Notes", placeholder="Example: Felt strong today")

        submitted = st.form_submit_button("Save Workout Record")

        if submitted:
            if not exercise.strip():
                st.error("Please enter the exercise name.")
            else:
                add_workout(
                    user_id,
                    today,
                    exercise.strip(),
                    sets,
                    reps,
                    weight,
                    notes.strip(),
                )
                st.success("Workout record saved.")

    st.subheader("Today's Workout Records")
    workouts = get_workouts(user_id)
    today_workouts = workouts[workouts["date"].astype(str) == str(today)]
    st.dataframe(
        today_workouts.drop(columns=["id"], errors="ignore"),
        use_container_width=True,
    )


elif menu == "Diet Record Table":
    st.header("Diet Record Table")
    st.write("Enter today's meal records. The date is automatically added.")

    with st.form("diet_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"],
            )
        with col2:
            food_item = st.text_input("Food Item", placeholder="Oats + banana")
        with col3:
            quantity = st.text_input("Quantity", placeholder="1 bowl / 200 g")

        col4, col5, col6, col7 = st.columns(4)

        with col4:
            calories = st.number_input("Calories", min_value=0.0, step=10.0)
        with col5:
            protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
        with col6:
            carbs = st.number_input("Carbs (g)", min_value=0.0, step=1.0)
        with col7:
            fat = st.number_input("Fat (g)", min_value=0.0, step=1.0)

        notes = st.text_area("Notes", placeholder="Example: With brown rice")

        submitted = st.form_submit_button("Save Diet Record")

        if submitted:
            if not food_item.strip():
                st.error("Please enter the food item.")
            else:
                add_diet(
                    user_id,
                    today,
                    meal_type,
                    food_item.strip(),
                    quantity.strip(),
                    calories,
                    protein,
                    carbs,
                    fat,
                    notes.strip(),
                )
                st.success("Diet record saved.")

    st.subheader("Today's Diet Records")
    diet = get_diet(user_id)
    today_diet = diet[diet["date"].astype(str) == str(today)]
    st.dataframe(
        today_diet.drop(columns=["id"], errors="ignore"),
        use_container_width=True,
    )


elif menu == "Previous Entries":
    st.header("Previous Entries")
    st.markdown(
        '<span class="readonly-badge">🔒 Read-only mode by default</span>',
        unsafe_allow_html=True,
    )

    workouts = get_workouts(user_id)
    diet = get_diet(user_id)

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if "confirm_edit" not in st.session_state:
        st.session_state.confirm_edit = False

    if "confirm_save" not in st.session_state:
        st.session_state.confirm_save = False

    if not st.session_state.edit_mode:
        if st.button("Enable Edit Mode"):
            st.session_state.confirm_edit = True

    if st.session_state.confirm_edit and not st.session_state.edit_mode:
        st.warning("Do you want to make changes?")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("Yes, enable editing"):
                st.session_state.edit_mode = True
                st.session_state.confirm_edit = False
                st.success("Editing is now enabled.")

        with c2:
            if st.button("Cancel"):
                st.session_state.confirm_edit = False

    if not st.session_state.edit_mode:
        st.subheader("Workout History")
        st.dataframe(
            workouts.drop(columns=["id"], errors="ignore"),
            use_container_width=True,
        )

        st.subheader("Diet History")
        st.dataframe(
            diet.drop(columns=["id"], errors="ignore"),
            use_container_width=True,
        )

    else:
        st.info("Edit mode is active. Review your changes carefully before saving.")

        st.subheader("Edit Workout History")
        edited_workouts = st.data_editor(
            workouts,
            use_container_width=True,
            num_rows="fixed",
            disabled=["id", "volume"],
            key="edited_workouts",
        )

        st.subheader("Edit Diet History")
        edited_diet = st.data_editor(
            diet,
            use_container_width=True,
            num_rows="fixed",
            disabled=["id"],
            key="edited_diet",
        )

        if not st.session_state.confirm_save:
            if st.button("Save Changes"):
                st.session_state.confirm_save = True

        if st.session_state.confirm_save:
            st.warning("Are you sure you want to save these changes permanently?")
            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("Yes, save permanently"):
                    update_workouts(user_id, edited_workouts)
                    update_diet(user_id, edited_diet)
                    st.session_state.confirm_save = False
                    st.session_state.edit_mode = False
                    st.success("Changes saved successfully.")
                    st.rerun()

            with c2:
                if st.button("Cancel Save"):
                    st.session_state.confirm_save = False

            with c3:
                if st.button("Exit Edit Mode"):
                    st.session_state.confirm_save = False
                    st.session_state.edit_mode = False
                    st.rerun()

    st.info("Saving changes asks for confirmation before updates are permanently saved.")