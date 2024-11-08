import streamlit as st

# Set up page configuration
st.set_page_config(layout="wide")

# Define allowed credentials
allowed_username = "svaradharajan@randomtrees.com"
allowed_password = "randomtrees"

# Session state to track login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# CSS to adjust the sidebar width and styling
st.markdown("""
    <style>
            .stAppHeader {
        background-color: #C3002F; /* Change this to your preferred color */
        color: white;
        top:0;
        font-size: 24px;
        text-align: center;
        padding: 40px;
        
    }  
            .stSidebar{
            background-color:#ffffff;
            color:white;
            margin-top:90px;
            border-radius:10px;
            font-size: 24px;
            text-align: center;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                       
            
            }
            .stSidebar title{
            color:white;
            }
        /* Adjust the sidebar width */
        .css-1d391kg {
            width: 100px; /* Change to desired width */
        }
        /* Center the content within the sidebar */
        .css-1d391kg > div {
            margin: 0 auto;
        }
            

    </style>
""", unsafe_allow_html=True)

# Login function
def login():
    st.title("Supplier Risk Navigator")
    
    # Username and password input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Login button and validation
    if st.button("Log in"):
        if username == allowed_username and password == allowed_password:
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting to dashboard...")
            # st.session_state.logged_in = True
            st.rerun()
            # st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Logout function
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        # st.experimental_rerun()

# Define pages
dashboard = st.Page(
    "reports/wraps.py", title="Wraps", icon=":material/dashboard:", default=True
)
bugs = st.Page("reports/vin.py", title="Vin", icon=":material/bug_report:")
alerts = st.Page(
    "reports/supplier.py", title="Supplier", icon=":material/notification_important:"
)

# # Conditional rendering based on login status
if st.session_state.logged_in:
    # st.title("Welcome to the Dashboard")
    
    # Navigation for logged-in users
    pg = st.navigation(
        {
            "Account": [st.Page(logout, title="Log out", icon=":material/logout:")],
            "Reports": [dashboard, bugs, alerts],
        }
    )
    pg.run()
else:
    login()










# import streamlit as st

# # Set up page configuration
# st.set_page_config(layout="wide")

# # Define allowed credentials
# allowed_username = "svaradharajan@randomtrees.com"
# allowed_password = "randomtrees"

# # Initialize session state to track login status
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# # Custom CSS to center the login card
# st.markdown("""
#     <style>
#         /* Center the card */
#         .login-card {
#             display: flex;
#             justify-content: center;
#             align-items: center;
#             height: 100vh;
#             background-color: #f5f7fa;
#         }
#         /* Style the login form card */
#         .card {
#             background-color: #ffffff;
#             padding: 40px 20px;
#             border-radius: 10px;
#             box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#             max-width: 400px;
#             text-align: center;
#         }
#         .card h2 {
#             color: #333;
#             margin-bottom: 30px;
#             font-size: 24px;
#             font-weight: 600;
#         }
#         /* Style the input fields */
#         .stTextInput > div > div > input {
#             padding: 10px;
#             font-size: 16px;
#         }
#         /* Style the login button */
#         .stButton > button {
#             background-color: #C3002F;
#             color: white;
#             font-size: 16px;
#             padding: 10px;
#             width: 100%;
#             border: none;
#             border-radius: 5px;
#             cursor: pointer;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # Login function
# def login():
#     st.markdown('<div class="login-card">', unsafe_allow_html=True)
#     with st.container():
#         st.markdown('<div class="card">', unsafe_allow_html=True)
#         st.markdown('<h2>Login</h2>', unsafe_allow_html=True)
        
#         # Username and password input fields within the card
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
        
#         # Login button and validation
#         if st.button("Log in"):
#             if username == allowed_username and password == allowed_password:
#                 st.session_state.logged_in = True
#                 st.success("Login successful! Redirecting to dashboard...")
#                 st.experimental_rerun()
#             else:
#                 st.error("Invalid username or password")
        
#         st.markdown('</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)

# # Logout function
# def logout():
#     if st.button("Log out"):
#         st.session_state.logged_in = False
#         st.experimental_rerun()

# # Conditional rendering based on login status
# if st.session_state.logged_in:
#     st.title("Welcome to the Dashboard")
#     logout()
# else:
#     login()
