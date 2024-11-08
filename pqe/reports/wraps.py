# -----------------------------latest anudeep code-----------



import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import snowflake.connector
import plotly.express as px 
import pydeck as pdk

def create_snowflake_connection():
    conn = snowflake.connector.connect(
        user="arampur",
        password="Arampur17",
        account="VJB64387.us-east-1",
        warehouse="COMPUTE_WH",
        database="NISSAN_LOCAL_DB",
        schema="NISSAN_WRAPS_DATA"
    )
    return conn

def fetch_supplier_names():
    query = "SELECT DISTINCT SUPL_SPLR_NM FROM UPDATED_WRAPS_DATA ORDER BY SUPL_SPLR_NM"
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result['SUPL_SPLR_NM'].tolist()

def fetch_vehicle_models():
    query = "SELECT DISTINCT MODEL_NAME FROM UPDATED_WRAPS_DATA ORDER BY MODEL_NAME"
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result['MODEL_NAME'].tolist()

def fetch_parts_names():
    query = "SELECT DISTINCT PART_NAME_DESCRIPTION FROM UPDATED_WRAPS_DATA ORDER BY PART_NAME_DESCRIPTION"
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result['PART_NAME_DESCRIPTION'].tolist()

def fetch_claim_volume_analysis(country, supplier_name, vehicle_model, parts_name, frequency):
    select_statement = f"""
        SELECT 
            CASE 
                WHEN '{frequency}' = 'M' THEN TO_CHAR(SF_CTE_DTE, 'YYYY-MM')
                WHEN '{frequency}' = 'Q' THEN TO_CHAR(SF_CTE_DTE, 'YYYY-Q')
                WHEN '{frequency}' = 'Y' THEN TO_CHAR(SF_CTE_DTE, 'YYYY')
            END AS PERIOD, 
            COUNT(*) AS TOTAL_COUNT, 
            SUM(CASE WHEN WPSCLM_BUS_TYP = '3MIS' THEN 1 ELSE 0 END) AS MIS_3, 
            SUM(CASE WHEN WPSCLM_BUS_TYP = '6MIS' THEN 1 ELSE 0 END) AS MIS_6
        FROM UPDATED_WRAPS_DATA
        WHERE 1=1
    """
    
    if country and country != 'All':
        select_statement += f" AND WPSCLM_VEH_CTRYCDE = '{country}'"
    if supplier_name and supplier_name != 'All':
        select_statement += f" AND SUPL_SPLR_NM = '{supplier_name}'"
    if vehicle_model and vehicle_model != 'All':
        select_statement += f" AND MODEL_NAME = '{vehicle_model}'"
    if parts_name and parts_name != 'All':
        select_statement += f" AND PART_NAME_DESCRIPTION = '{parts_name}'"
    
    select_statement += f"""
        GROUP BY 
            CASE 
                WHEN '{frequency}' = 'M' THEN TO_CHAR(SF_CTE_DTE, 'YYYY-MM')
                WHEN '{frequency}' = 'Q' THEN TO_CHAR(SF_CTE_DTE, 'YYYY-Q')
                WHEN '{frequency}' = 'Y' THEN TO_CHAR(SF_CTE_DTE, 'YYYY')
            END 
        ORDER BY PERIOD
    """

    conn = create_snowflake_connection()
    result = pd.read_sql(select_statement, conn)
    conn.close()
    return result

def fetch_claims_summary(country, supplier_name, vehicle_model, parts_name):
    query = """
        SELECT COUNT(*), SUM(WPSCLM_NMM_CLM_AMT), SUM(WPSCLM_RECVY_AMT), 
               SUM(WPSCLM_DSTRPRT_AMT), SUM(WPSCLM_DSTRLBR_AMT) 
        FROM UPDATED_WRAPS_DATA 
        WHERE 1=1
    """
    if country:
        query += f" AND WPSCLM_VEH_CTRYCDE = '{country}'"
    if supplier_name:
        query += f" AND SUPL_SPLR_NM = '{supplier_name}'"
    if vehicle_model:
        query += f" AND MODEL_NAME = '{vehicle_model}'"
    if parts_name:
        query += f" AND PART_NAME_DESCRIPTION = '{parts_name}'"
    
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    
    result = result.fillna(0)
    return result.iloc[0]

state_coords = { 
    "OH": {"latitude": 40.4173, "longitude": -82.9071,'country_name': 'USA', 'state_name': 'Ohio'},  # Ohio
    "CA": {"latitude": 36.7783, "longitude": -119.4179,'country_name': 'USA', 'state_name': 'California'}, # California
    "NL": {"latitude": 47.5615, "longitude": -52.7126,'country_name': 'CAN', 'state_name': 'Newfoundland and Labrador'},  # Newfoundland and Labrador # Canada
    "GA": {"latitude": 32.1656, "longitude": -82.9001,'country_name': 'USA', 'state_name': 'Georgia'},  # Georgia
    "TN": {"latitude": 35.5175, "longitude": -86.5804,'country_name': 'USA', 'state_name': 'Tennessee'},  # Tennessee
    "MI": {"latitude": 44.3148, "longitude": -85.6024,'country_name': 'USA', 'state_name': 'Michigan'},  # Michigan
    "FL": {"latitude": 27.9944, "longitude": -81.7603,'country_name': 'USA', 'state_name': 'Florida'},  # Florida
    "TX": {"latitude": 31.9686, "longitude": -99.9018,'country_name': 'USA', 'state_name': 'Texas'},  # Texas
    "AB": {"latitude": 53.9333, "longitude": -116.5765,'country_name': 'USA', 'state_name': 'Alberta'},  # Alberta  # Canada
    "WI": {"latitude": 43.7844, "longitude": -88.7879,'country_name': 'USA', 'state_name': 'Wisconsin'},  # Wisconsin
    "IL": {"latitude": 40.6331, "longitude": -89.3985,'country_name': 'USA', 'state_name': 'Illinois'},  # Illinois
    "AZ": {"latitude": 34.0489, "longitude": -111.0937,'country_name': 'USA', 'state_name': 'Arizona'},  # Arizona
    "QC": {"latitude": 52.9399, "longitude": -73.5491,'country_name': 'USA', 'state_name': 'Quebec'},  # Quebec  # Canada
    "NM": {"latitude": 34.5199, "longitude": -105.8701,'country_name': 'USA', 'state_name': 'New Mexico'},  # New Mexico
    "PA": {"latitude": 41.2033, "longitude": -77.1945,'country_name': 'USA', 'state_name': 'Pennsylvania'},  # Pennsylvania
    "MD": {"latitude": 39.0458, "longitude": -76.6413,'country_name': 'USA', 'state_name': 'Maryland'},  # Maryland
    "NJ": {"latitude": 40.0583, "longitude": -74.4057,'country_name': 'USA', 'state_name': 'New Jersey'},  # New Jersey
    "NY": {"latitude": 43.2994, "longitude": -74.2179,'country_name': 'USA', 'state_name': 'New York'},  # New York
    "NC": {"latitude": 35.7596, "longitude": -79.0193,'country_name': 'USA', 'state_name': 'North Carolina'},  # North Carolina
    "MA": {"latitude": 42.4072, "longitude": -71.3824,'country_name': 'USA', 'state_name': 'Massachusetts'},  # Massachusetts
    "ON": {"latitude": 51.2538, "longitude": -85.3232,'country_name': 'CAN', 'state_name': 'Ontario'},  # Ontario  # Canada
    "CT": {"latitude": 41.6032, "longitude": -73.0877,'country_name': 'USA', 'state_name': 'Connecticut'},  # Connecticut
    "NE": {"latitude": 41.4925, "longitude": -99.9018,'country_name': 'USA', 'state_name': 'Nebraska'},  # Nebraska
    "WA": {"latitude": 47.7511, "longitude": -120.7401,'country_name': 'USA', 'state_name': 'Washington'},  # Washington
    "MN": {"latitude": 46.7296, "longitude": -94.6859,'country_name': 'USA', 'state_name': 'Minnesota'},  # Minnesota
    "SC": {"latitude": 33.8361, "longitude": -81.1637,'country_name': 'USA', 'state_name': 'South Carolina'},  # South Carolina
    "MO": {"latitude": 37.9643, "longitude": -91.8318,'country_name': 'USA', 'state_name': 'Missouri'},  # Missouri
    "OK": {"latitude": 35.0078, "longitude": -97.0929,'country_name': 'USA', 'state_name': 'Oklahoma'},  # Oklahoma
    "NV": {"latitude": 38.8026, "longitude": -116.4194,'country_name': 'USA', 'state_name': 'Nevada'},  # Nevada
    "AL": {"latitude": 32.3182, "longitude": -86.9023,'country_name': 'USA', 'state_name': 'Alabama'},  # Alabama
    "AR": {"latitude": 35.2010, "longitude": -91.8318,'country_name': 'USA', 'state_name': 'Arkansas'},  # Arkansas
    "NS": {"latitude": 44.6820, "longitude": -63.7443,'country_name': 'CAN', 'state_name': 'Nova Scotia'},  # Nova Scotia  # Canada
    "KS": {"latitude": 39.0119, "longitude": -98.4842,'country_name': 'USA', 'state_name': 'Kansas'},  # Kansas
    "CO": {"latitude": 39.5501, "longitude": -105.7821,'country_name': 'USA', 'state_name': 'Colorado'},  # Colorado
    "ME": {"latitude": 45.2538, "longitude": -69.4455,'country_name': 'USA', 'state_name': 'Maine'},  # Maine
    "VA": {"latitude": 37.4316, "longitude": -78.6569,'country_name': 'USA', 'state_name': 'Virginia'},  # Virginia
    "MS": {"latitude": 32.3547, "longitude": -89.3985,'country_name': 'USA', 'state_name': 'Mississippi'},  # Mississippi
    "SK": {"latitude": 52.9399, "longitude": -106.4509,'country_name': 'CAN', 'state_name': 'Saskatchewan'},  # Saskatchewan  # Canada
    "IA": {"latitude": 41.8780, "longitude": -93.0977,'country_name': 'USA', 'state_name': 'Iowa'},  # Iowa
    "RI": {"latitude": 41.5801, "longitude": -71.4774,'country_name': 'USA', 'state_name': 'Rhode Island'},  # Rhode Island
    "LA": {"latitude": 30.9843, "longitude": -91.9623,'country_name': 'USA', 'state_name': 'Louisiana'},  # Louisiana
    "IN": {"latitude": 40.2672, "longitude": -86.1349,'country_name': 'USA', 'state_name': 'Indiana'},  # Indiana
    "OR": {"latitude": 43.8041, "longitude": -120.5542,'country_name': 'USA', 'state_name': 'Oregon'},  # Oregon
    "BC": {"latitude": 53.7267, "longitude": -127.6476,'country_name': 'CAN', 'state_name': 'British Columbia'},  # British Columbia  # Canada
    "ND": {"latitude": 47.5515, "longitude": -101.0020,'country_name': 'USA', 'state_name': 'North Dakota'},  # North Dakota
    "NB": {"latitude": 46.5653, "longitude": -66.4619,'country_name': 'CAN', 'state_name': 'New Brunswick'},  # New Brunswick  # Canada
    "WV": {"latitude": 38.5976, "longitude": -80.4549,'country_name': 'USA', 'state_name': 'West Virginia'},  # West Virginia
    "ID": {"latitude": 44.0682, "longitude": -114.7420,'country_name': 'USA', 'state_name': 'Idaho'},  # Idaho
    "MB": {"latitude": 49.8951, "longitude": -97.1384,'country_name': 'CAN', 'state_name': 'Manitoba'},  # Manitoba  # Canada
    "DE": {"latitude": 38.9108, "longitude": -75.5277,'country_name': 'USA', 'state_name': 'Delaware'},  # Delaware
    "KY": {"latitude": 37.8393, "longitude": -84.2700,'country_name': 'USA', 'state_name': 'Kentucky'},  # Kentucky
    "UT": {"latitude": 39.3200, "longitude": -111.0937,'country_name': 'USA', 'state_name': 'Utah'},  # Utah
    "NH": {"latitude": 43.1939, "longitude": -71.5724,'country_name': 'USA', 'state_name': 'New Hampshire'},  # New Hampshire
    "HI": {"latitude": 19.8968, "longitude": -155.5828,'country_name': 'USA', 'state_name': 'Hawaii'},  # Hawaii
    "VT": {"latitude": 44.5588, "longitude": -72.5778,'country_name': 'USA', 'state_name': 'Vermont'},  # Vermont
    "PE": {"latitude": 46.5107, "longitude": -63.4168,'country_name': 'CAN', 'state_name': 'Prince Edward Island'},  # Prince Edward Island  # Canada
    "SD": {"latitude": 43.9695, "longitude": -99.9018,'country_name': 'USA', 'state_name': 'South Dakota'}   # South Dakota
}

def fetch_claim_hotspot_data(supplier_name):
    query = """
        SELECT 
            WPSCLM_ST_CDE AS STATE_CODE, 
            COUNT(*) AS CLAIM_COUNT
        FROM UPDATED_WRAPS_DATA
        WHERE WPSCLM_ST_CDE IS NOT NULL
    """
    
    if supplier_name != 'All':
        query += f" AND SUPL_SPLR_NM = '{supplier_name}'"
    
    query += """
        GROUP BY WPSCLM_ST_CDE
        ORDER BY CLAIM_COUNT DESC
        LIMIT 5
    """
    
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    
    map_data_list = []
    for index, row in result.iterrows():
        state_code = row['STATE_CODE']
        if state_code in state_coords:
            coord = state_coords[state_code]
            map_data_list.append({'lat': coord['latitude'], 'lon': coord['longitude'], 'Claim Count': row['CLAIM_COUNT'],'country_name': coord['country_name'],
                'state_name': coord['state_name']})
    
    return pd.DataFrame(map_data_list)

def fetch_top_suppliers_static():
    query = """
        SELECT SUPL_SPLR_NM, COUNT(*) AS CLAIM_COUNT 
        FROM UPDATED_WRAPS_DATA
        GROUP BY SUPL_SPLR_NM
        ORDER BY CLAIM_COUNT DESC
        LIMIT 5
    """
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result

def fetch_top_issue_categories(supplier_name):
    query = """
        SELECT WPSCLM_CLM_TYP_CDE AS ISSUE_CATEGORY, COUNT(*) AS ISSUE_COUNT 
        FROM UPDATED_WRAPS_DATA
        WHERE SUPL_SPLR_NM = %s
        GROUP BY WPSCLM_CLM_TYP_CDE
        ORDER BY ISSUE_COUNT DESC
        LIMIT 5
    """
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn, params=(supplier_name,))
    conn.close()
    return result

def fetch_top_issue_parts(supplier_name=None):
    query = """
        SELECT PART_NAME_DESCRIPTION, COUNT(*) AS PART_COUNT 
        FROM UPDATED_WRAPS_DATA
        WHERE 1=1
    """
    if supplier_name and supplier_name != 'All':
        query += f" AND SUPL_SPLR_NM = '{supplier_name}'"

    query += """
        GROUP BY PART_NAME_DESCRIPTION
        ORDER BY PART_COUNT DESC
        LIMIT 5
    """
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result

def fetch_top_issue_models(supplier_name=None):
    query = """
        SELECT MODEL_NAME, COUNT(*) AS MODEL_COUNT 
        FROM UPDATED_WRAPS_DATA
        WHERE 1=1
    """
    if supplier_name and supplier_name != 'All':
        query += f" AND SUPL_SPLR_NM = '{supplier_name}'"

    query += """
        GROUP BY MODEL_NAME
        ORDER BY MODEL_COUNT DESC
        LIMIT 5
    """
    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result

def fetch_detailed_warranty_claims(country, supplier_name, vehicle_model, parts_name):
    query = """
        SELECT 
            WPSCLM_VIN_NBR AS VIN_Number,
            MODEL_NAME AS Model_Name,
            WPSCLM_MDL_YR_ID AS Model_Year,
            WPSCLM_VEH_CTRYCDE AS State,
            WPSCLM_CLM_NBR AS Claim_Number,
            WPSCLM_VEH_RPR_DTE AS Claim_Open_Date,
            WPSCLM_IN_SVC_DT AS Claim_Inservice_Date,
            PART_NAME_DESCRIPTION AS Part_Name,
            SUPL_SPLR_NM AS Supplier_Name,
            WPSCLM_CLM_TYP_CDE AS Issue_Category
        FROM UPDATED_WRAPS_DATA
        WHERE 1=1
    """
    
    if country and country != 'All':
        query += f" AND WPSCLM_VEH_CTRYCDE = '{country}'"
    if supplier_name and supplier_name != 'All':
        query += f" AND SUPL_SPLR_NM = '{supplier_name}'"
    if vehicle_model and vehicle_model != 'All':
        query += f" AND MODEL_NAME = '{vehicle_model}'"
    if parts_name and parts_name != 'All':
        query += f" AND PART_NAME_DESCRIPTION = '{parts_name}'"

    conn = create_snowflake_connection()
    result = pd.read_sql(query, conn)
    conn.close()
    return result

# st.set_page_config(layout="wide")

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

        .section-header {
        font-size: 18px;
        margin-bottom: 10px;
        font-weight: bold;
        }

        .metric-box {
            padding: 15px;
            margin: 10px;
            border-radius: 10px;
            background-color: #f9f9f9;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 100%;
            max-width: 180px;
        }
        .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }

    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
    }
    .action-btn {
        padding: 6px 12px;
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 5px;
        cursor: pointer;
        color: #333;
    }

    .action-btn:hover {
        background-color: #e0e0e0;
    }

    .pagination {
        display: flex;
        justify-content: flex-end;
        margin-top: 5px;
        margin-bottom: 5px;
    }

    .pagination a {
        color: #333;
        float: none;
        display: inline-block;
        padding: 5px 10px;
        margin: 0 2px;
        text-decoration: none;
        transition: background-color .3s, transform .2s;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 10px;
    }

    .pagination a.active {
        background-color: #007BFF;
        color: white;
        border: 1px solid #007BFF;
    }

    .pagination a:hover:not(.active) {
        background-color: #f0f0f0;
        transform: scale(1.05);
    }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 6px 10px rgba(0,0,0,0.1);
        max-width: 100%;  /* Ensure card doesn't exceed parent width */
        overflow-x: auto; 
        overflow-y:auto;
        
    }
    .card-header {
        font-size: 18px;        
        color: #333;
        margin-bottom: 10px;
    }
    .action-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        font-size: 12px;
        cursor: pointer;
        border-radius: 4px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 5px 0;
        font-size: 14px;
    }
    th, td {
        padding: 8px 12px;
        border-bottom: 1px solid #ddd;
        border-collapse: collapse;
        text-align:center;
    }
    th {
        background-color: #f2f2f2;
    }
    .css-1d391kg, .css-1v3fvcr, .css-1lcbmhc {  
        width: 200px;  /* Set the width of the sidebar */
    }

    /* Optional: adjust the width of the main content area */
    .css-1g3uw71 {
        margin-left: 120px; /* Adjust margin based on sidebar width */
    }
    .custom-button {
        display: inline-block;
        background-color: #4CAF50; /* Green background */
        color: white; /* White text */
        padding: 10px 20px; /* Padding */
        text-align: center; /* Center text */
        text-decoration: none; /* Remove underline */
        margin: 4px 2px; /* Margin */
        border: none; /* Remove border */
        border-radius: 5px; /* Rounded corners */
        cursor: pointer; /* Pointer cursor on hover */
        width: 100%; /* Full width */
        transition: background-color 0.3s; /* Transition effect */
    }

    .custom-button:hover {
        background-color: #45a049; /* Darker green on hover */
    }
    </style>
""", unsafe_allow_html=True)


st.title("WRAPS - Warranty Dashboard")

supplier_names = fetch_supplier_names()
vehicle_models = fetch_vehicle_models()
parts_names = fetch_parts_names()


col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    country = st.selectbox('Country', ['All', 'USA', 'JPN', 'CAN'], index=1)
with col2:
    supplier_name = st.selectbox('Supplier Name', ['All'] + supplier_names, index=0)
with col3:
    parts_name = st.selectbox('Parts Name', ['All'] + parts_names, index=0)
with col4:
    vehicle_model = st.selectbox('Vehicle Model', ['All'] + vehicle_models, index=0)
with col5:
    date_range = st.selectbox('Date Range Selector', ['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'Custom'], index=1)

filters = {
    "country": country if country != 'All' else None,
    "supplier_name": supplier_name if supplier_name != 'All' else None,
    "vehicle_model": vehicle_model if vehicle_model != 'All' else None,
    "parts_name": parts_name if parts_name != 'All' else None
}
claims_summary = fetch_claims_summary(**filters)

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
with metric_col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Claim Count</div>
        <div class="metric-value">{claims_summary[0]}</div>
    </div>
    """, unsafe_allow_html=True)
with metric_col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Claim Amount</div>
        <div class="metric-value">${claims_summary[1]:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with metric_col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Recovery Amount</div>
        <div class="metric-value">${claims_summary[2]:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with metric_col4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Parts Amount</div>
        <div class="metric-value">${claims_summary[3]:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with metric_col5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Total Labour Amount</div>
        <div class="metric-value">${claims_summary[4]:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    
    with st.expander("Claim Volume Analysis",expanded=True):
        frequency = st.selectbox("Select Report Frequency", ['M', 'Q', 'Y'], index=0, 
                                    format_func=lambda x: {'M': 'Monthly', 'Q': 'Quarterly', 'Y': 'Yearly'}.get(x))

        claim_volume_data = fetch_claim_volume_analysis(country, supplier_name, vehicle_model, parts_name, frequency)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=claim_volume_data["PERIOD"], y=claim_volume_data["TOTAL_COUNT"], name="Total Count",
                                marker=dict(color='blue', opacity=0.7)))
        # fig.add_trace(go.Bar(x=claim_volume_data["PERIOD"], y=claim_volume_data["MIS_3"], name="3 MIS",
        #                         marker=dict(color='orange', opacity=0.7)))
        fig.add_trace(go.Scatter(x=claim_volume_data["PERIOD"], y=claim_volume_data["MIS_3"],mode="lines+markers", name="3 MIS",line=dict(color="green", dash="dot"),))
        fig.add_trace(go.Bar(x=claim_volume_data["PERIOD"], y=claim_volume_data["MIS_6"], name="6 MIS",
                                marker=dict(color='red', opacity=0.7)))

       
        fig.update_layout(
            title='',
            barmode='group',
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            xaxis=dict(showgrid=False), 
            yaxis=dict(showgrid=True), 
            margin=dict(l=0, r=0, t=40, b=0),
            title_font_size=20, 
            title_x=0.5, 
            showlegend=True, 
            hovermode="x unified", 
            bargap=0.2, 
            bargroupgap=0.1,
            height=160  # Set custom height here
        )
        st.plotly_chart(fig, use_container_width=True)

 

with col2:
   
    # with st.expander("Claim Hotspot Region Analysis",expanded=True):
    #     hotspot_data = fetch_claim_hotspot_data(supplier_name)
        
    #     # Create a pydeck map layer for highlighting locations with pins and hover tooltips
    #     layer = pdk.Layer(
    #         "ScatterplotLayer",
    #         data=hotspot_data,
    #         get_position='[lon, lat]',
    #         get_color='[200, 30, 0, 160]',  # red color
    #         get_radius=10000,  # Adjust radius for pin size
    #         pickable=True # Enables tooltips

    #     )
        
    #     # Set up tooltips to display county and state name on hover
    #     tooltip = {
    #         "html": "<b>Country:</b> {country_name}<br/><b>State:</b> {state_name}<br/><b>Claim Count:</b> {Claim Count}",
    #         "style": {"backgroundColor": "steelblue", "color": "white"}
    #     }
        
    #     # Configure the pydeck view
    #     view_state = pdk.ViewState(
    #         latitude=hotspot_data['lat'].mean(),
    #         longitude=hotspot_data['lon'].mean(),
    #         zoom=5,  # Adjust zoom level as needed
    #         pitch=0
    #     )
        
    #     # Create the deck.gl map with the layer and view state
    #     deck = pdk.Deck(
    #         layers=[layer],
    #         initial_view_state=view_state,
    #         tooltip=tooltip
    #     )
        
    #     st.pydeck_chart(deck,use_container_width=True,height=250)

    with st.expander("Claim Hotspot Region Analysis", expanded=True):
        hotspot_data = fetch_claim_hotspot_data(supplier_name)

        # Primary layer with small, solid pins for each location
        layer_main = pdk.Layer(
            "ScatterplotLayer",
            data=hotspot_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',  # red color
            get_radius=5000,  # Adjust radius for pin size
            pickable=True  # Enables tooltips
        )
        
        # Highlight layer with larger, transparent circles for glow effect
        layer_highlight = pdk.Layer(
            "ScatterplotLayer",
            data=hotspot_data,
            get_position='[lon, lat]',
            get_color='[255, 215, 0, 80]',  # Yellow color with low opacity for highlighting
            get_radius=15000,  # Larger radius for highlight effect
            pickable=False  # No tooltips on this layer
        )

        # Tooltips to display information on hover
        tooltip = {
            "html": "<b>Country:</b> {country_name}<br/><b>State:</b> {state_name}<br/><b>Claim Count:</b> {Claim Count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        # Configure the view
        view_state = pdk.ViewState(
            latitude=hotspot_data['lat'].mean(),
            longitude=hotspot_data['lon'].mean(),
            zoom=5,  # Adjust zoom level as needed
            pitch=0
        )

        # Create the deck.gl map with both layers
        deck = pdk.Deck(
            layers=[layer_highlight, layer_main],  # Add both layers to the map
            initial_view_state=view_state,
            tooltip=tooltip
        )

        # Render the map
        st.pydeck_chart(deck, use_container_width=True, height=250)


col3, col4 = st.columns(2)
with col3:
    with st.expander("Top Suppliers by Claims", expanded=True):
        top_suppliers_data = fetch_top_suppliers_static()
        fig_suppliers = px.pie(top_suppliers_data, names='SUPL_SPLR_NM', values='CLAIM_COUNT',
                               hole=0.4, 
                                color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_suppliers.update_layout(height=250,width = 300)
        st.plotly_chart(fig_suppliers, use_container_width=True)

with col4:
    with st.expander("Top Issue Categories by Claims", expanded=True):
        top_issues_data = fetch_top_issue_categories(supplier_name) if supplier_name != 'All' else fetch_top_issue_categories("Default_Supplier")
        fig_issues = px.pie(top_issues_data, names='ISSUE_CATEGORY', values='ISSUE_COUNT',
                             hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_issues.update_layout(height=250)
        st.plotly_chart(fig_issues, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    with st.expander("Top Issue Parts", expanded=True):
        top_parts_data = fetch_top_issue_parts(supplier_name)
        fig_parts = go.Figure(data=go.Bar(
            y=top_parts_data['PART_NAME_DESCRIPTION'],
            x=top_parts_data['PART_COUNT'],
            orientation='h',
            marker=dict(color='rgba(44, 160, 44, 0.7)', line=dict(color='rgba(44, 160, 44, 1.0)', width=2))
        ))
        fig_parts.update_layout(
            
            xaxis_title="Claim Count",
            yaxis_title="Parts",
            height=250,
            template='plotly_dark'
        )
        st.plotly_chart(fig_parts, use_container_width=True)

with col6:
    with st.expander("Top Issue Models", expanded=True):
        top_models_data = fetch_top_issue_models(supplier_name)
        fig_models = go.Figure(data=go.Bar(
            y=top_models_data['MODEL_NAME'],
            x=top_models_data['MODEL_COUNT'],
            orientation='h',
            marker=dict(color='rgba(255, 159, 64, 0.7)', line=dict(color='rgba(255, 159, 64, 1.0)', width=2))
        ))
        fig_models.update_layout(
           
            xaxis_title="Claim Count",
            yaxis_title="Models",
            height=250,
            template='plotly_dark'
        )
        st.plotly_chart(fig_models, use_container_width=True)

st.header("Warranty Claim Summary")

claims_data = fetch_detailed_warranty_claims(country, supplier_name, vehicle_model, parts_name)

st.markdown("""
    <style>
        .claim-summary-card {
            background-color: #f8f9fa;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            box-shadow: 0 6px 10px rgba(0,0,0,0.1);
            max-width: 100%;  /* Ensure card doesn't exceed parent width */
            height:400px;
            overflow-x: auto; 
            overflow-y:auto;
        }
        .claim-summary-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            overflow-x: auto; 
            overflow-y:auto;
            
        }
        .claim-summary-table th, .claim-summary-table td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
            text-align: center;
        }
        .claim-summary-table th {
            background-color: #00000;
            color: black;
        }
        .claim-summary-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .action-btn {
            padding: 6px 12px;
            background-color: #00000;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            font-size: 12px;
            cursor: pointer;
            text-align: center;
        }
        .action-btn:hover {
            background-color: #00000;
        }
    </style>
""", unsafe_allow_html=True)

if claims_data.empty:
    st.write("No data available for the selected filters.")
else:
    if 'CLAIM_NUMBER' in claims_data.columns:
        claims_data['Action'] = claims_data['CLAIM_NUMBER'].apply(
            lambda x: f'<a class="action-btn" onclick="alert(\'Claim Number: {x}\')">View</a>'
        )
    else:
        st.write("Claim_Number column is missing in claims_data.")

    table_html = claims_data.to_html(classes="claim-summary-table", escape=False, index=False)
    st.markdown(f'<div class="claim-summary-card">{table_html}</div>', unsafe_allow_html=True)