# --------------------------------- perfect working vin mangement code -------------------------------
import streamlit as st
import snowflake.connector
import pandas as pd

# Set up page configuration and custom styling
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
    /* General Page Styling */
    .search-bar {
        width: 35%;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ccc;
        font-size: 14px;
        margin-bottom: 20px;
        margin-right: 20px;
    
    }

    .controls-section {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .control-item button {
        background-color: #002C61;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        color: white;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s ease;
    }

    .control-item button:hover {
        background-color: #004A9F;
    }

    /* Styling for VIN Summary Section */
    .vin-summary-content {
        
        padding: 0px;
        
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 0;
    }

    .vin-item {
        background-color: #f4f4f4;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: left;
    }

    /* Styling for the Claim Summary Table */
    .claim-summary {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
    }

    .claim-summary th {
        background-color: #002C61;
        color: white;
        padding: 12px;
        text-align: left;
    }

    .claim-summary td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
        background-color: #f9f9f9;
    }

    .claim-summary tr:nth-child(even) td {
        background-color: #f3f6fa;
    }

    .claim-summary tr:hover td {
        background-color: #e1edff;
        color: #002C61;
        font-weight: bold;
    }

    .claim-summary-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }

    /* Styling for Intelligence Analysis */
    .intelligence-bar {
        background-color: #DAA520;
        border-radius: 8px;
        padding: 12px;
        color: white;
        font-weight: bold;
        font-size: 18px;
        text-align: left;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .intelligence-checkbox {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
        padding: 12px;
        margin-top:10px;
        margin-bottom: 10px;
        background-color: #f7f7f7;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .run-button {
        background-color: #DAA520;
        position: absolute;
        right:0;
        
        align-items: center;
        color: white;
        padding: 12px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        width: 25%;
        margin-bottom: 20px;
        font-size: 16px;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .run-button:hover {
        background-color: #004A9F;
    }

    .details-box {
        background-color: #f7f7f7;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Custom styles for expander headers */
    .expander-header {
        background-color: #002C61;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 18px;
        margin-bottom: 10px;
        cursor: pointer;
    }

    /* Styling for the Part Summary Table */
    .part-summary {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom:5px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    }

    .part-summary th {
        background-color: #002C61;
        color: white;
        padding: 12px;
        text-align: left;
    }

    .part-summary td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
        background-color: #f9f9f9;
    }

    .part-summary tr:nth-child(even) td {
        background-color: #f3f6fa;
    }

    .part-summary tr:hover td {
        background-color: #e1edff;
        color: #002C61;
        font-weight: bold;
    }

    .part-summary th:nth-child(1),
    .part-summary td:nth-child(1) {
        text-align: center;
    }

    .part-summary td a {
        color: #0066cc;
        text-decoration: none;
    }

    .part-summary td a:hover {
        text-decoration: underline;
    }
            
    .card {
        background-color: #f8f9fa;
        padding: 10px;
        margin: 5px 0;
        margin-top:60px;    
        border-radius: 10px;
        box-shadow: 0 6px 10px rgba(0,0,0,0.1);
        max-width: 100%;  /* Ensure card doesn't exceed parent width */
        overflow-x: auto; 
        overflow-y:auto;
        
    }
    

    </style>
""", unsafe_allow_html=True)

# Snowflake Query Function
def query_snowflake(vin_number: str):
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user='arampur',
        password='Arampur17',
        account='VJB64387.us-east-1',
        warehouse='COMPUTE_WH',
        database='SPDBCOSMIC',
        schema='PUBLIC'
    )
    cursor = conn.cursor()

    # Query VIN Summary
    cursor.execute(f"""
        SELECT WPSCLM_VIN_NBR, WPSCLM_MDL_YR_ID, MODEL_NAME, WPSCLM_ENG_MDL_CDE, 
               WPSCLM_ENG_SRL_NBR, WPSCLM_VEHMI_CNT, WPSCLM_VEH_KLM_CNT, WPSCLM_VEH_CLR_CDE 
        FROM NISSAN_LOCAL_DB.SRN_DATASETS.VIN_DATAS
        WHERE WPSCLM_VIN_NBR = '{vin_number}'
    """)
    vin_summary = cursor.fetchone()

    # Query Claim Summary
    cursor.execute(f"""
        SELECT WPSCLM_CLM_NBR, WPSCLM_WO_OPEN_DT, PART_NAME_DESCRIPTION, SUPL_SPLR_NM ,ISSUE_SUMMARY
        FROM NISSAN_LOCAL_DB.SRN_DATASETS.VIN_DATAS 
        WHERE WPSCLM_VIN_NBR = '{vin_number}'
    """)
    claim_summary = cursor.fetchall()

    # Query Parts Summary
    cursor.execute(f"""
        SELECT WPSCLM_CLM_NBR, PART_NAME_DESCRIPTION, SERVICE_ADVISOR_COMMENTS, TECHNICIAN_COMMENTS, 
               ISSUE_SUMMARY, ROOTCAUSE_CATEGORY, RCA_SOURCE_SYSTEM 
        FROM NISSAN_LOCAL_DB.SRN_DATASETS.VIN_DATAS
        WHERE WPSCLM_VIN_NBR = '{vin_number}'
    """)
    parts_summary = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    return vin_summary, claim_summary, parts_summary

# Streamlit UI
st.title("Vehicle Warranty Summary")

# User Input for VIN Number
search_vin = st.text_input("Search VIN", placeholder="Enter VIN", key="vin_search")

if search_vin:
    vin_summary, claim_summary, parts_summary = query_snowflake(search_vin)

    if vin_summary:
        vin_css = """
        <style>
        .vin-summary-card {
        padding: 10px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin:0;
        }
        .vin-summary-card h4{
        margin-bottom:8px;
        padding:0;
        font-weight:2px;
        }
        
        
        
   
        </style>
        """
         # Insert the CSS into Streamlit
        st.markdown(vin_css, unsafe_allow_html=True)

        # Display VIN Summary
        
        vin_html = f"""<div class="vin-summary-card">
                        <h4><strong>VIN Summary</strong></h4>
                        <div class="vin-summary-content">
                            <div class="vin-item"><strong>VIN Number:</strong> {vin_summary[0]}</div>
                            <div class="vin-item"><strong>Model Year:</strong> {vin_summary[1]}</div>
                            <div class="vin-item"><strong>Model Name:</strong> {vin_summary[2]}</div>
                            <div class="vin-item"><strong>Engine Model Code:</strong> {vin_summary[3]}</div>
                            <div class="vin-item"><strong>Engine Serial Number:</strong> {vin_summary[4]}</div>
                            <div class="vin-item"><strong>Miles Driven:</strong> {vin_summary[5]}</div>
                            <div class="vin-item"><strong>KM Driven:</strong> {vin_summary[6]}</div>
                            <div class="vin-item"><strong>Colour Code:</strong> {vin_summary[7]}</div>
                        </div>
                    </div>
                    """
        # Display the table in Streamlit
        st.markdown(vin_html, unsafe_allow_html=True)
           # Custom CSS for the table
        table_css = """
        <style>
        .custom-card {
        padding: 10px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        .custom-table th, .custom-table td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        .custom-table th {
            background-color: #002C61;
            color: white;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .custom-table tr:hover {
            background-color: #ddd;
        }
        .custom-card h4{
        margin-bottom:8px;
        padding:0;
        font-weight:2px;
        }
        </style>
        """

        # Insert the CSS into Streamlit
        st.markdown(table_css, unsafe_allow_html=True)
        # Display Claim Summary
        # st.subheader("Claim Summary")
        # claim_df = pd.DataFrame(claim_summary, columns=["Claim Number", "Open Date", "Part Name", "Supplier Name"])
        # st.dataframe(claim_df)
        table_html = "<div class='custom-card'>"
        table_html += "<h4><strong>Claim Summary</strong></h4>"
        table_html += "<table class='custom-table'>"
        table_html += "<tr><th>Claim Number</th><th>Open Date</th><th>Part Name</th><th>Supplier Name</th><th>Issue Category</th></tr>"

        for item in claim_summary:
            table_html += f"<tr><td>{item[0]}</td><td>{item[1]}</td><td>{item[2]}</td><td>{item[3]}</td><td>{item[4]}</td></tr>"
        
        table_html += "</table></div>"

        # Display the table in Streamlit
        st.markdown(table_html, unsafe_allow_html=True)
    # else:
    #     st.info("No VIN claim summary details available.")

        
        # Display Parts Summary
        st.subheader("Parts Summary")
       
        st.markdown("""
            <div class="intelligence-bar">Intelligence Analysis</div>
        """, unsafe_allow_html=True)
        # Intelligence Analysis Section content
        st.markdown("""
            <div class="expander-box">
                <div class="intelligence-checkbox">
                    <input type="checkbox" checked> Summarization: Summarizing Vehicle information & Parts issues related complaints from customer or service advisor and dealer or technician comments
                </div>
                <div class="intelligence-checkbox">
                    <input type="checkbox" checked> RCA Classification (Root Cause Category): Identifying Root Cause Category for each part based on customer complaints and dealer comments
                </div>
                <button class="run-button">Run</button>
            </div>
        """, unsafe_allow_html=True)

        # Custom CSS for the table
    table_css = """
        <style>
        .custom-intelligence-card {
        padding: 10px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 55px;
        }
        .custom-intelligence-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        .custom-intelligence-table th, .custom-intelligence-table td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        .custom-intelligence-table th {
            background-color: #002C61;
            color: white;
        }
        .custom-intelligence-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .custom-intelligence-table tr:hover {
            background-color: #ddd;
        }
        </style>
        """

        # Insert the CSS into Streamlit
    st.markdown(table_css, unsafe_allow_html=True)
    table_html = "<div class='custom-intelligence-card'>"
    table_html += "<table class='custom-intelligence-table'>"
    table_html += "<tr><th>Claim Number</th><th>Part Name</th><th>Customer/Service Advisor Comments</th><th>Dealer/Technician Comments</th><th>Issue Category</th><th>Root Cause Category</th><th>RCA Source System</th></tr>"
        
    for item in parts_summary:
        table_html += f"<tr><td>{item[0]}</td><td>{item[1]}</td><td>{item[2]}</td><td>{item[3]}</td><td>{item[4]}</td><td>{item[5]}</td><td>{item[6]}</td></tr>"
        
        table_html += "</table>"

        # Display the table in Streamlit
        st.markdown(table_html, unsafe_allow_html=True)

    # else:
    #     st.write("No data found for the entered VIN number.")




