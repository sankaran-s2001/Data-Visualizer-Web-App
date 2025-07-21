import os
import pandas as pd
import streamlit as st
import plotly.express as px
import glob

# Add this to check file permissions
st.write("Current directory:", os.getcwd())
st.write("Files in data directory:", os.listdir("data"))

st.write("Current working directory:", os.getcwd())
st.write("Directory contents:", os.listdir('.'))





# Set page configuration
st.set_page_config(page_title="Data Visualizer Pro",
                   layout="centered",
                   page_icon="📊")

# Title
st.title("📊 Data Visualizer Pro - Web App")

# Data Source Selection
st.subheader("📁 Choose Your Data Source")

data_source = st.radio(
    "Select data source:",
    options=["Use built-in datasets", "Upload your own CSV file"],
    index=0
)

df = None  # Initialize dataframe variable

# Built-in CSV files option
if data_source == "Use built-in datasets":    
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Find all CSV files in the data folder
        file_list = glob.glob("data/*.csv")
        
        if file_list:
            # Extract just the filenames for display
            file_names = [os.path.basename(f) for f in file_list]
            selected_file = st.selectbox("Select a built-in dataset", file_names, index=None)
            
            if selected_file:
                # Find the full path of the selected file
                file_path = os.path.join("data", selected_file)
                df = pd.read_csv(file_path)
                st.success(f"✅ Loaded dataset: {selected_file}")
        else:
            st.warning("⚠️ No CSV files found in the data folder. Please add CSV files to the 'data' folder.")
    except Exception as e:
        st.error(f"❌ Error accessing data: {str(e)}")

# File upload option
elif data_source == "Upload your own CSV file":
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV file from your computer"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Successfully uploaded: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Main
if df is not None:
    st.subheader("📊 Data Overview & Visualization")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    # Get column names
    columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    with col1:
        st.write("**Dataset Preview:**")
        st.dataframe(df.head(), use_container_width=True)
        
        # Dataset info
        st.write("**Dataset Info:**")
        st.write(f"• **Rows:** {len(df)}")
        st.write(f"• **Columns:** {len(df.columns)}")
        st.write(f"• **Numeric columns:** {len(numeric_columns)}")
        st.write(f"• **Categorical columns:** {len(categorical_columns)}")
    
    with col2:
        st.write("**Chart Configuration:**")
        
        # Plot type selection
        plot_list = ["Line chart", "Bar chart", "Scatter plot", "Distribution plot", "Count plot"]
        selected_plot = st.selectbox("Select chart type", options=plot_list, index=None)
        
        # Axis selection
        x_axis = st.selectbox("Select X-axis", options=columns + ["None"], index=None)
        y_axis = st.selectbox("Select Y-axis", options=columns + ["None"], index=None)
        
        # Color selection
        color_by = st.selectbox(
            "Color by (optional):",
            options=["None"] + columns,
            index=0,
            help="Choose a column to color"
        )
        
        # Additional options based on plot type
        if selected_plot == "Distribution plot":
            bins = st.slider("Number of bins", min_value=10, max_value=100, value=30)
        
        # Size selection for scatter plots
        if selected_plot == "Scatter plot":
            size_by = st.selectbox(
                "Size by (optional):",
                options=["None"] + numeric_columns,
                index=0,
                help="Choose a numeric column to size points"
            )

    # Plot generation
    if selected_plot and x_axis and x_axis != "None":
        if st.button("📊Generate Plot", type="primary"):
            try:
                # Prepare color parameter
                color_param = None if color_by == "None" else color_by
                
                # Create plots based on selection
                if selected_plot == "Line chart":
                    if y_axis and y_axis != "None":
                        fig = px.line(df, x=x_axis, y=y_axis, color=color_param,
                                      title=f"Line Chart: {y_axis} vs {x_axis}")
                    else:
                        st.error("❌ Line chart requires both X and Y axis")
                        st.stop()
                
                elif selected_plot == "Bar chart":
                    if y_axis and y_axis != "None":
                        fig = px.bar(df, x=x_axis, y=y_axis, color=color_param,
                                     title=f"Bar Chart: {y_axis} vs {x_axis}", text_auto = True)
                    else:
                        # Count plot style bar chart
                        fig = px.histogram(df, x=x_axis, color=color_param,
                                           title=f"Count Bar Chart: {x_axis}")
                
                elif selected_plot == "Scatter plot":
                    if y_axis and y_axis != "None":
                        size_param = None if 'size_by' not in locals() or size_by == "None" else size_by
                        fig = px.scatter(df, x=x_axis, y=y_axis, color=color_param, size=size_param,
                                         title=f"Scatter Plot: {y_axis} vs {x_axis}",
                                         hover_data=columns)
                    else:
                        st.error("❌ Scatter plot requires both X and Y axis")
                        st.stop()
                
                elif selected_plot == "Distribution plot":
                    fig = px.histogram(df, x=x_axis, color=color_param, nbins=bins,
                                       title=f"Distribution of {x_axis}", text_auto = True)
                
                elif selected_plot == "Count plot":
                    fig = px.histogram(df, x=x_axis, color=color_param,
                                       title=f"Count Plot: {x_axis}", text_auto = True)
                
                # Customize the layout
                fig.update_layout(
                    width=900,
                    height=600,
                    font=dict(size=12),
                    title_font_size=18,
                    showlegend=True,
                    hovermode='closest'
                )
                
                # Display the interactive plot
                st.plotly_chart(fig, use_container_width=True)
                
                
            except Exception as e:
                st.error(f"❌ Error creating plot: {str(e)}")
                st.write("**Troubleshooting tips:**")
                st.write("• Make sure selected columns contain appropriate data types")
                st.write("• Check for missing values in selected columns")
                st.write("• Ensure numeric columns are selected for Y-axis in line/scatter plots")

else:
    st.info("👆 Please select a data source and load a dataset to start visualizing!")
    
    # Sample data info
    st.subheader("📖 How to Use This App")
    
    with st.expander("🔍 Built-in Datasets Option"):
        st.write("""
        - Create a `data` folder in the same directory as this script
        - Add your CSV files to the `data` folder  
        - Select from the dropdown to load any dataset
        """)
    
    with st.expander("⬆️ Upload CSV Option"):
        st.write("""
        - Click 'Browse files' to upload any CSV from your computer
        - Supports standard CSV format with headers
        - File will be processed immediately after upload
        """)
    
    with st.expander("🎨 Color Coding Feature"):
        st.write("""
        - Use the 'Color by' dropdown to add a categorical dimension
        - Perfect for comparing groups in bar charts
        - Creates legend automatically for easy interpretation
        - Works with both numeric and categorical columns
        """)
