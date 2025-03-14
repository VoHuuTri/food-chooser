import streamlit as st
import pandas as pd
import numpy as np
import random
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Google Sheet Data Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2196F3;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    .info-box {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .filter-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ff9800;
    }
    .filter-section {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .filter-title {
        font-weight: bold;
        color: #ff5722;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .active-filters {
        background-color: #e0f7fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #00bcd4;
    }
    .filter-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 1rem;
        background-color: #e1f5fe;
        color: #0277bd;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .warning-text {
        color: #ff9800;
        font-size: 0.9rem;
    }
    .info-text {
        color: #2196F3;
        font-size: 0.9rem;
    }
    .error-text {
        color: #f44336;
        font-size: 0.9rem;
    }
    .filter-container {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
        height: 100%;
    }
    .filter-header {
        font-weight: bold;
        margin-bottom: 8px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 5px;
    }
    .filter-status {
        margin-top: 5px;
        margin-bottom: 5px;
        min-height: 20px;
    }
    .filter-control {
        margin-top: 10px;
    }
    /* CSS để làm cho các hàng filter thẳng hàng */
    .filter-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-gap: 15px;
    }
    .filter-grid-item {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #e0e0e0;
        display: flex;
        flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# Function to download DataFrame as CSV
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download CSV File</a>'
    return href

# Function to download DataFrame as Excel
def download_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_data.xlsx">Download Excel File</a>'
    return href

# Function to get data from Google Sheet
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_data(sheet_url, skip_first_row=True):
    try:
        # Get sheet ID from URL
        if "spreadsheets/d/" in sheet_url:
            sheet_id = sheet_url.split("spreadsheets/d/")[1].split("/")[0]
        else:
            st.error("Invalid Google Sheet URL")
            return None
        
        # For public sheets, we can use the export CSV link directly
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        if skip_first_row:
            # Skip the first row (row 1) and use the second row (row 2) as header
            df = pd.read_csv(csv_export_url, skiprows=1)
        else:
            # Use the first row as header (default behavior)
            df = pd.read_csv(csv_export_url)
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Sidebar for inputs and settings
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Google_Sheets_Logo.svg/1200px-Google_Sheets_Logo.svg.png", width=100)
    st.title("Google Sheet Viewer")
    
    # Input for Google Sheet URL
    sheet_url = st.text_input(
        "Enter your public Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=0"
    )
    
    # Option to skip first row
    skip_first_row = st.checkbox("Start from row 2 (skip first row)", value=True, help="Select this if you want to ignore the first row and use the second row as header")
    
    st.divider()
    
    st.subheader("Settings")
    
    # Filter settings
    st.subheader("Filter Settings")
    max_unique_values = st.slider("Max unique values for filters", 20, 1000, 100, 
                                help="Maximum number of unique values to display in dropdown filters")
    filter_all_columns = st.checkbox("Enable filters for all columns", value=True, 
                                   help="If unchecked, only columns with few unique values will have filters")
    
    # Other settings
    random_count = st.slider("Number of random rows to select", 1, 50, 10)
    show_stats = st.checkbox("Show statistics", value=True)
    dark_mode = st.checkbox("Dark mode", value=False)
    
    st.divider()
    
    if dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #121212;
                color: #FFFFFF;
            }
            .main-header {
                color: #81C784;
            }
            .section-header {
                color: #64B5F6;
            }
            .info-box {
                background-color: #1A237E;
                color: #E8EAF6;
            }
            .success-box {
                background-color: #1B5E20;
                color: #E8F5E9;
            }
            .filter-box {
                background-color: #3e2723;
                color: #ffecb3;
                border-left: 4px solid #ff9800;
            }
            .filter-section {
                background-color: #212121;
                color: #ffffff;
            }
            .filter-badge {
                background-color: #263238;
                color: #80deea;
            }
            .active-filters {
                background-color: #263238;
                color: #b2ebf2;
                border-left: 4px solid #00bcd4;
            }
            .warning-text {
                color: #ffb74d;
            }
            .info-text {
                color: #64b5f6;
            }
            .error-text {
                color: #e57373;
            }
            .filter-container {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            .filter-header {
                border-bottom: 1px solid #333333;
            }
            .filter-grid-item {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("### About")
    st.info("This app allows you to view and filter data from public Google Sheets.")
    
    st.markdown("### Instructions")
    st.markdown("""
    1. Enter your Google Sheet URL
    2. Choose whether to start from row 1 or row 2
    3. Use filters to narrow down data - you can filter multiple columns simultaneously
    4. Click "Select Random Rows" to pick random rows
    5. Download the filtered data as CSV or Excel
    """)

# Main content
st.markdown('<h1 class="main-header">📊 Google Sheet Data Viewer</h1>', unsafe_allow_html=True)

if not sheet_url:
    st.markdown('<div class="info-box">Please enter a public Google Sheet URL in the sidebar to get started.</div>', unsafe_allow_html=True)
else:
    # Load the data
    with st.spinner("Loading data from Google Sheet..."):
        data = load_data(sheet_url, skip_first_row)
    
    if data is None or data.empty:
        st.warning("No data found or unable to access the sheet.")
    else:
        # Show basic info
        st.markdown(f'<h2 class="section-header">Data Overview</h2>', unsafe_allow_html=True)
        first_row_info = "Starting from row 2 (skipping first row)" if skip_first_row else "Starting from row 1"
        st.markdown(f'<div class="info-box">Loaded {data.shape[0]} rows and {data.shape[1]} columns. {first_row_info}.</div>', unsafe_allow_html=True)
        
        # Show basic statistics if enabled
        if show_stats:
            st.markdown(f'<h2 class="section-header">Data Statistics</h2>', unsafe_allow_html=True)
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Count of non-null values for each column
                st.subheader("Non-null values count")
                non_null_counts = data.count()
                st.bar_chart(non_null_counts)
            
            with col2:
                # For numeric columns, show mean values
                numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    st.subheader("Mean values for numeric columns")
                    mean_values = data[numeric_cols].mean()
                    st.bar_chart(mean_values)
        
        # Create filters
        st.markdown(f'<h2 class="section-header">Filter Data</h2>', unsafe_allow_html=True)
        
        # Explanation for filtering multiple columns
        st.markdown('<div class="filter-box"><h3>💡 Multi-Column Filtering</h3><p>You can filter multiple columns simultaneously! Select filter values for any number of columns below. All filters will be applied together to find rows that match <b>ALL</b> selected criteria.</p></div>', unsafe_allow_html=True)
        
        # Phân loại các cột theo loại dữ liệu và số lượng giá trị duy nhất
        columns_with_few_values = []  # <= 20 giá trị duy nhất
        columns_with_many_values = []  # > 20 nhưng <= max_unique_values
        columns_with_too_many_values = []  # > max_unique_values
        numeric_columns = []
        
        for column in data.columns:
            dtype = data[column].dtype
            unique_count = data[column].nunique()
            
            if pd.api.types.is_numeric_dtype(dtype) and unique_count > 1:
                numeric_columns.append((column, unique_count))
            elif unique_count <= 20:
                columns_with_few_values.append((column, unique_count))
            elif unique_count <= max_unique_values:
                columns_with_many_values.append((column, unique_count))
            else:
                columns_with_too_many_values.append((column, unique_count))
        
        # Tạo filters
        filters = {}
        
        # Container cho các filter
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">Select filter values for columns:</div>', unsafe_allow_html=True)
        
        # Hiển thị các cột với ít giá trị trước
        if columns_with_few_values:
            st.subheader("Columns with few unique values")
            
            # Tạo lưới cho các filter này
            cols_per_row = 3
            for i in range(0, len(columns_with_few_values), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = columns_with_few_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    with cols[j]:
                        with st.container():
                            st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                            
                            unique_values = sorted(data[column].dropna().unique())
                            selected_values = st.multiselect(
                                f"Select values",
                                options=unique_values,
                                default=[],
                                key=f"few_{column}"
                            )
                            
                            if selected_values:
                                filters[column] = selected_values
        
        # Hiển thị các cột với nhiều giá trị
        if columns_with_many_values and filter_all_columns:
            st.subheader("Columns with many unique values")
            
            # Tạo lưới cho các filter này
            cols_per_row = 3
            for i in range(0, len(columns_with_many_values), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = columns_with_many_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    with cols[j]:
                        with st.container():
                            st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="filter-status warning-text">⚠️ {count} unique values</div>', unsafe_allow_html=True)
                            
                            unique_values = sorted(data[column].dropna().unique())
                            selected_values = st.multiselect(
                                f"Select values",
                                options=unique_values,
                                default=[],
                                key=f"many_{column}"
                            )
                            
                            if selected_values:
                                filters[column] = selected_values
        
        # Hiển thị các cột số
        if numeric_columns:
            st.subheader("Numeric columns")
            
            # Tạo lưới cho các filter này
            cols_per_row = 3
            for i in range(0, len(numeric_columns), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = numeric_columns[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    if j < len(cols):
                        with cols[j]:
                            with st.container():
                                min_val = float(data[column].min())
                                max_val = float(data[column].max())
                                
                                # Bỏ qua nếu khoảng quá nhỏ
                                if max_val - min_val < 1e-9:
                                    st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                                    st.markdown(f'<div class="filter-status error-text">🚫 No range to filter</div>', unsafe_allow_html=True)
                                    continue
                                
                                st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                                
                                values = st.slider(
                                    f"Range",
                                    min_value=min_val,
                                    max_value=max_val,
                                    value=(min_val, max_val),
                                    key=f"numeric_{column}"
                                )
                                
                                if values != (min_val, max_val):
                                    filters[f"{column}_range"] = values
        
        # Hiển thị các cột với quá nhiều giá trị
        if columns_with_too_many_values and filter_all_columns:
            st.subheader("Columns with too many unique values")
            
            # Tạo lưới cho các filter này
            cols_per_row = 3
            for i in range(0, len(columns_with_too_many_values), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = columns_with_too_many_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    if j < len(cols):
                        with cols[j]:
                            with st.container():
                                st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="filter-status error-text">🚫 {count} values (too many)</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="filter-status info-text">ℹ️ Showing only first {max_unique_values} values</div>', unsafe_allow_html=True)
                                
                                try:
                                    unique_values = sorted(data[column].astype(str).dropna().unique())[:max_unique_values]
                                    selected_values = st.multiselect(
                                        f"Select values",
                                        options=unique_values,
                                        default=[],
                                        key=f"toomany_{column}"
                                    )
                                    
                                    if selected_values:
                                        filters[column] = selected_values
                                except:
                                    st.markdown(f'<div class="filter-status error-text">Cannot create filter</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters to the data
        filtered_data = data.copy()
        active_filters = []
        
        for column, values in filters.items():
            if column.endswith("_range"):
                # Handle range filters
                col_name = column.replace("_range", "")
                min_val, max_val = values
                filtered_data = filtered_data[(filtered_data[col_name] >= min_val) & (filtered_data[col_name] <= max_val)]
                active_filters.append(f"{col_name}: {min_val} to {max_val}")
            else:
                # Handle multiselect filters
                filtered_data = filtered_data[filtered_data[column].isin(values)]
                active_filters.append(f"{column}: {', '.join(str(v) for v in values)}")
        
        # Show filtered data info
        st.markdown(f'<h2 class="section-header">Filtered Data</h2>', unsafe_allow_html=True)
        
        # Display active filters
        if active_filters:
            st.markdown(f'<div class="active-filters">', unsafe_allow_html=True)
            st.markdown(f"<b>Active Filters ({len(active_filters)}):</b>", unsafe_allow_html=True)
            badges_html = ""
            for filter_item in active_filters:
                badges_html += f'<span class="filter-badge">{filter_item}</span>'
            st.markdown(badges_html, unsafe_allow_html=True)
            st.markdown(f'<p>Showing {filtered_data.shape[0]} rows after applying {len(active_filters)} filter(s)</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-box">Showing all {filtered_data.shape[0]} rows (no filters applied)</div>', unsafe_allow_html=True)
        
        # Buttons for actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Random selection button
            if st.button(f"Select {random_count} Random Rows"):
                if filtered_data.shape[0] > 0:
                    if filtered_data.shape[0] <= random_count:
                        st.markdown(f'<div class="success-box">All {filtered_data.shape[0]} rows selected as there are fewer than {random_count} rows after filtering</div>', unsafe_allow_html=True)
                        st.dataframe(filtered_data, height=400)
                    else:
                        random_indices = random.sample(range(filtered_data.shape[0]), random_count)
                        random_selection = filtered_data.iloc[random_indices]
                        st.markdown(f'<div class="success-box">Randomly selected {random_count} rows from filtered data</div>', unsafe_allow_html=True)
                        st.dataframe(random_selection, height=400)
                else:
                    st.warning("No data to select after applying filters")
        
        with col2:
            # Download as CSV
            if st.button("Download as CSV"):
                st.markdown(download_csv(filtered_data), unsafe_allow_html=True)
        
        with col3:
            # Download as Excel
            if st.button("Download as Excel"):
                st.markdown(download_excel(filtered_data), unsafe_allow_html=True)
        
        # Display the filtered data
        st.dataframe(filtered_data, height=500)