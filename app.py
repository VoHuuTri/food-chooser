import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# Set page title
st.set_page_config(page_title="Google Sheet Data Viewer", layout="wide")

# Add custom CSS
st.markdown("""
<style>
    .filter-section {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .filter-title {
        font-weight: bold;
        color: #0066cc;
    }
    .highlight-text {
        font-weight: bold;
        color: #ff5722;
        font-size: 1.1em;
    }
    /* CSS cho các container filter */
    .filter-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #dee2e6;
    }
    .filter-header {
        font-weight: bold;
        margin-bottom: 8px;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 5px;
        color: #0066cc;
    }
    .filter-status {
        margin-top: 5px;
        margin-bottom: 5px;
        font-size: 0.9em;
    }
    .warning-text {
        color: #ff9800;
    }
    .info-text {
        color: #2196F3;
    }
    .error-text {
        color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

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

# Main app
def main():
    st.title("📊 Google Sheet Data Viewer")
    
    # Input for Google Sheet URL
    sheet_url = st.text_input(
        "Enter your public Google Sheet URL",
        placeholder="https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=0"
    )
    
    # Option to skip first row
    skip_first_row = st.checkbox("Skip first row (start from row 2)", value=True)
    
    if not sheet_url:
        st.info("Please enter a public Google Sheet URL to get started.")
        return
    
    # Load the data
    data = load_data(sheet_url, skip_first_row)
    
    if data is None or data.empty:
        st.warning("No data found or unable to access the sheet.")
        return
    
    # Show basic info
    st.subheader("Data Overview")
    st.write(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns")
    
    # Create filters
    st.subheader("Filter Data")
    
    # Add explanation for multi-column filtering
    st.markdown('<div class="highlight-text">💡 You can filter multiple columns simultaneously - just select values from any number of columns!</div>', unsafe_allow_html=True)
    
    # Filter settings
    col1, col2 = st.columns(2)
    with col1:
        max_unique = st.slider("Max unique values for filters", min_value=20, max_value=1000, value=100, 
                             help="Maximum number of unique values to display in a filter dropdown. Higher values may cause performance issues.")
    with col2:
        filter_all_columns = st.checkbox("Show filters for all columns", value=True, 
                                      help="If unchecked, only columns with <= 20 unique values will have filters")
    
    # Phân loại các cột dựa trên số lượng giá trị duy nhất
    columns_with_few_values = []  # <= 20 giá trị duy nhất
    columns_with_many_values = []  # > 20 nhưng <= max_unique
    columns_with_too_many_values = []  # > max_unique
    
    for column in data.columns:
        unique_count = data[column].nunique()
        if unique_count <= 20:
            columns_with_few_values.append((column, unique_count))
        elif unique_count <= max_unique:
            columns_with_many_values.append((column, unique_count))
        else:
            columns_with_too_many_values.append((column, unique_count))
    
    # Create a container for filters
    filter_container = st.container()
    
    with filter_container:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<p class="filter-title">Select filter values for each column:</p>', unsafe_allow_html=True)
        
        # Tạo filters
        filters = {}
        filter_count = 0
        
        # Hiển thị các cột có ít giá trị duy nhất
        if columns_with_few_values:
            st.subheader("Columns with few unique values")
            
            # Tạo 3 cột cho mỗi hàng filter
            cols_per_row = 3
            for i in range(0, len(columns_with_few_values), cols_per_row):
                # Tạo các cột trong một hàng
                cols = st.columns(cols_per_row)
                # Lấy một batch các cột để hiển thị trong hàng này
                batch = columns_with_few_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    with cols[j]:
                        with st.container():
                            st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                            
                            # Tạo multiselect cho filter
                            unique_values = sorted(data[column].dropna().unique())
                            selected_values = st.multiselect(
                                "Select values",
                                options=unique_values,
                                default=[],
                                key=f"few_{column}"
                            )
                            
                            if selected_values:
                                filters[column] = selected_values
                                filter_count += 1
        
        # Hiển thị các cột có nhiều giá trị duy nhất
        if columns_with_many_values and filter_all_columns:
            st.subheader("Columns with many unique values")
            
            cols_per_row = 3
            for i in range(0, len(columns_with_many_values), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = columns_with_many_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    with cols[j]:
                        with st.container():
                            st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="filter-status warning-text">⚠️ Column has {count} unique values</div>', unsafe_allow_html=True)
                            
                            # Tạo multiselect cho filter
                            unique_values = sorted(data[column].dropna().unique())
                            selected_values = st.multiselect(
                                "Select values",
                                options=unique_values,
                                default=[],
                                key=f"many_{column}"
                            )
                            
                            if selected_values:
                                filters[column] = selected_values
                                filter_count += 1
        
        # Hiển thị các cột có quá nhiều giá trị duy nhất
        if columns_with_too_many_values and filter_all_columns:
            st.subheader("Columns with too many unique values")
            
            cols_per_row = 3
            for i in range(0, len(columns_with_too_many_values), cols_per_row):
                cols = st.columns(cols_per_row)
                batch = columns_with_too_many_values[i:i+cols_per_row]
                
                for j, (column, count) in enumerate(batch):
                    if j < len(cols):  # Đảm bảo không vượt quá số lượng cột đã tạo
                        with cols[j]:
                            with st.container():
                                st.markdown(f'<div class="filter-header">Filter by {column}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="filter-status error-text">🚫 Too many values ({count})</div>', unsafe_allow_html=True)
                                
                                if count <= 1000:  # Giới hạn cao hơn cho UI
                                    st.markdown(f'<div class="filter-status info-text">ℹ️ Showing only first {max_unique} values</div>', unsafe_allow_html=True)
                                    
                                    # Tạo multiselect với số lượng giá trị bị giới hạn
                                    unique_values = sorted(data[column].dropna().unique())[:max_unique]
                                    selected_values = st.multiselect(
                                        "Select values",
                                        options=unique_values,
                                        default=[],
                                        key=f"toomany_{column}"
                                    )
                                    
                                    if selected_values:
                                        filters[column] = selected_values
                                        filter_count += 1
                                else:
                                    st.markdown(f'<div class="filter-status error-text">Cannot display filter for this column</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters to the data
    filtered_data = data.copy()
    for column, values in filters.items():
        if values:
            filtered_data = filtered_data[filtered_data[column].isin(values)]
    
    # Show filtered data info
    st.subheader("Filtered Data")
    if filter_count > 0:
        st.write(f"Showing {filtered_data.shape[0]} rows after filtering by {filter_count} column(s)")
    else:
        st.write(f"Showing all {filtered_data.shape[0]} rows (no filters applied)")
    
    # Add active filters display
    if filters:
        st.markdown("**Active Filters:**")
        filter_text = ""
        for column, values in filters.items():
            filter_text += f"- **{column}**: {', '.join(str(v) for v in values)}\n"
        st.markdown(filter_text)
    
    # Random selection button
    if st.button("Select 10 Random Rows"):
        if filtered_data.shape[0] > 0:
            if filtered_data.shape[0] <= 10:
                st.success(f"All {filtered_data.shape[0]} rows selected as there are fewer than 10 rows after filtering")
                st.dataframe(filtered_data)
            else:
                random_indices = random.sample(range(filtered_data.shape[0]), 10)
                random_selection = filtered_data.iloc[random_indices]
                st.success("Randomly selected 10 rows from filtered data")
                st.dataframe(random_selection)
        else:
            st.warning("No data to select after applying filters")
    else:
        # Display the filtered data
        st.dataframe(filtered_data)

if __name__ == "__main__":
    main() 