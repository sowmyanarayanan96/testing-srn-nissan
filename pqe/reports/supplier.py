import streamlit as st
import snowflake.connector
import plotly.graph_objects as go


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
            .custom-title {
        color: #000000;
        font-size: 32px;
        text-align: left;
        margin-top: 0;
        margin-bottom: 10px;
        padding:0;
    }
            
    </style>""",unsafe_allow_html=True)

# st.title("Supplier 360° Analysis")
st.markdown("<h1 class='custom-title'>Supplier 360° Analysis</h1>", unsafe_allow_html=True)



SNOWFLAKE_USER = "arampur"
SNOWFLAKE_PASSWORD = "Arampur17"
SNOWFLAKE_ACCOUNT = "VJB64387.us-east-1"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "SPDBCOSMIC"
SNOWFLAKE_SCHEMA = "SCM_SYS_STRGY_DA"

def execute_query(query, params=None):
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    columns = [col[0].lower() for col in cursor.description]
    data = [dict(zip(columns, row)) for row in result]
    cursor.close()
    conn.close()
    return data

def fetch_supplier_id(supplier_name):
    query = """
    SELECT SUPL_SPLR_ID 
    FROM SUPPLIER_CATALOG
    WHERE SUPL_SPLR_NM ILIKE %s
    LIMIT 1
    """
    data = execute_query(query, (f"%{supplier_name}%",))
    return data[0]['supl_splr_id'] if data else None

def fetch_supplier_performance(supplier_number, facility, year, months):
    time_period_pattern = get_time_period_pattern(year, months)
    facility_pattern = ".*" if facility == "All" else facility
    query = f"""
    SELECT 
        SDPS_TIME_PERIOD AS sdps_time_period,
        SDPS_IMPACT_SCORE AS sdps_impact_score,
        SDPS_FINANCIAL_IMPACT_SCORE AS sdps_financial_impact_score,
        SDPS_OPERATIONAL_IMPACT_SCORE AS sdps_operational_impact_score
    FROM SUPPLIER_DELIVERY_PERFORMANCE_SCORECARD
    WHERE SUPPLIER_NUMBER = %s
    AND FACILITY_ID RLIKE %s
    AND ({' OR '.join(['SDPS_TIME_PERIOD LIKE %s' for _ in time_period_pattern])})
    """
    params = [supplier_number, facility_pattern] + time_period_pattern
    return execute_query(query, params)

def fetch_ran_shipment(supplier_number, facility, year, months):
    time_period_pattern = get_time_period_pattern(year, months)
    facility_pattern = ".*" if facility == "All" else facility
    query = f"""
    SELECT 
        SDPS_TIME_PERIOD AS sdps_time_period,
        SDPS_RAN_COUNT AS sdps_ran_count
    FROM SUPPLIER_DELIVERY_PERFORMANCE_SCORECARD
    WHERE SUPPLIER_NUMBER = %s
    AND FACILITY_ID RLIKE %s
    AND ({' OR '.join(['SDPS_TIME_PERIOD LIKE %s' for _ in time_period_pattern])})
    """
    params = [supplier_number, facility_pattern] + time_period_pattern
    return execute_query(query, params)

def fetch_trend_analysis(supplier_number, facility, year, months):
    time_period_pattern = get_time_period_pattern(year, months)
    facility_pattern = ".*" if facility == "All" else facility
    query = f"""
    SELECT 
        SDPS_TIME_PERIOD AS sdps_time_period,
        SDPS_DOWN_TIME_MINUTE_COUNT AS sdps_down_time_minute_count,
        SDPS_PPOF_COUNT AS sdps_ppof_count,
        SDPS_RDR_COUNT AS sdps_rdr_count,
        SDPS_AETC_COUNT AS sdps_aetc_count
    FROM SUPPLIER_DELIVERY_PERFORMANCE_SCORECARD
    WHERE SUPPLIER_NUMBER = %s
    AND FACILITY_ID RLIKE %s
    AND ({' OR '.join(['SDPS_TIME_PERIOD LIKE %s' for _ in time_period_pattern])})
    """
    params = [supplier_number, facility_pattern] + time_period_pattern
    return execute_query(query, params)

def fetch_financial_impact(supplier_number, facility, year, months):
    time_period_pattern = get_time_period_pattern(year, months)
    facility_pattern = ".*" if facility == "All" else facility
    query = f"""
    SELECT 
        SDPS_TIME_PERIOD AS sdps_time_period,
        SDPS_TOTAL_FINANCIAL_IMPACT_AMOUNT AS sdps_total_financial_impact_amount,
        SDPS_DOWN_TIME_FINANCIAL_IMPACT_AMOUNT AS sdps_down_time_minute_fin_imp,
        SDPS_PPOF_FINANCIAL_IMPACT_AMOUNT AS sdps_ppof_fin_imp,
        SDPS_RDR_FINANCIAL_IMPACT_AMOUNT AS sdps_rdr_fin_imp,
        SDPS_AETC_FINANCIAL_IMPACT_AMOUNT AS sdps_aetc_fin_imp
    FROM SUPPLIER_DELIVERY_PERFORMANCE_SCORECARD
    WHERE SUPPLIER_NUMBER = %s
    AND FACILITY_ID RLIKE %s
    AND ({' OR '.join(['SDPS_TIME_PERIOD LIKE %s' for _ in time_period_pattern])})
    """
    params = [supplier_number, facility_pattern] + time_period_pattern
    return execute_query(query, params)

def get_time_period_pattern(year, months):
    if months == "All":
        return [f"{year}-%"]
    else:
        month_mapping = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        selected_months = [month_mapping.get(month.strip(), None) for month in months.split(",") if month.strip()]
        return [f"{year}-{month}%" for month in selected_months]

# st.set_page_config(layout="wide")


with st.container():
    col1, col2, col3, col4 = st.columns(4)
    supplier_name = col1.text_input("Supplier Name")
    facility = col2.selectbox("Facility Name", ["All", "Canton Plant (CP)", "Smyrna Plant (SP)", "Decherd Plant (DP)"], index=0)
    year = col3.selectbox("Select Year", ["2023", "2024"])
    months = col4.multiselect("Select Month(s)", ["All", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], default="All")

facility_map = {"Canton Plant (CP)": "CP", "Smyrna Plant (SP)": "SP", "Decherd Plant (DP)": "DP"}
facility_filter = facility_map.get(facility, "All")
months_filter = ",".join(months) if months != ["All"] else "All"

if supplier_name:
    supplier_id = fetch_supplier_id(supplier_name)
    if supplier_id:
        st.write(f"Supplier Number: **{supplier_id}**")

        col1, col2 = st.columns(2)

        supplier_performance_data = fetch_supplier_performance(supplier_id, facility_filter, year, months_filter)
        with col1.expander("Supplier Performance", expanded=True):
            fig_performance = go.Figure()
            fig_performance.add_trace(go.Bar(
                x=[d['sdps_time_period'] for d in supplier_performance_data],
                y=[d['sdps_impact_score'] for d in supplier_performance_data],
                name="Impact Score",
                marker=dict(color="lightblue", line=dict(color="#0000FF", width=1))
            ))
            fig_performance.add_trace(go.Bar(
                x=[d['sdps_time_period'] for d in supplier_performance_data],
                y=[d['sdps_financial_impact_score'] for d in supplier_performance_data],
                name="Financial Impact Score",
                marker=dict(color="lightcoral", line=dict(color="#FF0000", width=1))
            ))
            fig_performance.add_trace(go.Bar(
                x=[d['sdps_time_period'] for d in supplier_performance_data],
                y=[d['sdps_operational_impact_score'] for d in supplier_performance_data],
                name="Operational Impact Score",
                marker=dict(color="lightgreen", line=dict(color="#00FF00", width=1))
            ))
            fig_performance.update_layout(
                title="",
                barmode="group",
                xaxis=dict(title="Period"),
                yaxis=dict(title="Scores"),
                template="plotly_white",
            )
            st.plotly_chart(fig_performance, use_container_width=True)

        ran_shipment_data = fetch_ran_shipment(supplier_id, facility_filter, year, months_filter)
        with col2.expander("RAN Shipment", expanded=True):
            fig_ran = go.Figure([go.Bar(
                x=[d['sdps_time_period'] for d in ran_shipment_data],
                y=[d['sdps_ran_count'] for d in ran_shipment_data],
                marker=dict(color="purple", opacity=0.8, line=dict(color="#800080", width=1))
            )])
            fig_ran.update_layout(
                title="",
                xaxis=dict(title="Period"),
                yaxis=dict(title="RAN Count"),
                template="plotly_white",
            )
            st.plotly_chart(fig_ran, use_container_width=True)

        trend_data = fetch_trend_analysis(supplier_id, facility_filter, year, months_filter)
        with col1.expander("Trend Analysis", expanded=True):
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in trend_data],
                y=[d['sdps_down_time_minute_count'] for d in trend_data],
                mode='lines+markers',
                name="Downtime",
                line=dict(color="blue"),
                hovertemplate="<b>Downtime</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_trend.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in trend_data],
                y=[d['sdps_ppof_count'] for d in trend_data],
                mode='lines+markers',
                name="PPOF",
                line=dict(color="orange"),
                hovertemplate="<b>PPOF (Past Point of Fit)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_trend.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in trend_data],
                y=[d['sdps_rdr_count'] for d in trend_data],
                mode='lines+markers',
                name="RDR",
                line=dict(color="green"),
                hovertemplate="<b>RDR (Receipt Discrepancy Report)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_trend.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in trend_data],
                y=[d['sdps_aetc_count'] for d in trend_data],
                mode='lines+markers',
                name="AETC",
                line=dict(color="red"),
                hovertemplate="<b>AETC (Expedited Transportation)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_trend.update_layout(
                title="",
                xaxis=dict(title="Period"),
                yaxis=dict(title="Counts"),
                template="plotly_white",
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        financial_data = fetch_financial_impact(supplier_id, facility_filter, year, months_filter)
        with col2.expander("Financial Impact", expanded=True):
            fig_financial = go.Figure()
            fig_financial.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in financial_data],
                y=[d['sdps_total_financial_impact_amount'] for d in financial_data],
                mode='lines+markers',
                name="Total Financial Impact",
                line=dict(color="darkblue"),
                hovertemplate="<b>Total Financial Impact</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_financial.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in financial_data],
                y=[d['sdps_down_time_minute_fin_imp'] for d in financial_data],
                mode='lines+markers',
                name="Downtime Impact",
                line=dict(color="purple"),
                hovertemplate="<b>Downtime Financial Impact</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_financial.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in financial_data],
                y=[d['sdps_ppof_fin_imp'] for d in financial_data],
                mode='lines+markers',
                name="PPOF Impact",
                line=dict(color="darkgreen"),
                hovertemplate="<b>PPOF Financial Impact (Past Point of Fit)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_financial.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in financial_data],
                y=[d['sdps_rdr_fin_imp'] for d in financial_data],
                mode='lines+markers',
                name="RDR Impact",
                line=dict(color="darkred"),
                hovertemplate="<b>RDR Financial Impact (Receipt Discrepancy Report)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_financial.add_trace(go.Scatter(
                x=[d['sdps_time_period'] for d in financial_data],
                y=[d['sdps_aetc_fin_imp'] for d in financial_data],
                mode='lines+markers',
                name="AETC Impact",
                line=dict(color="orange"),
                hovertemplate="<b>AETC Financial Impact (Expedited Transportation)</b>: %{y}<br><b>Period</b>: %{x}<extra></extra>"
            ))
            fig_financial.update_layout(
                title="",
                xaxis=dict(title="Period"),
                yaxis=dict(title="Financial Impact Amount"),
                template="plotly_white",
            )
            st.plotly_chart(fig_financial, use_container_width=True)

    else:
        st.warning("No Supplier ID found for the entered supplier name.")
else:
    st.info("Please enter a supplier name to search.")
