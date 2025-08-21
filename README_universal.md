# 🌍 Universal Data Analyzer Dashboard

**The Ultimate Tool for Analyzing Any Data Files from Any Country or Dataset!**

This universal data analyzer automatically detects, reads, cleans, analyzes, and visualizes any type of data file you throw at it. Perfect for researchers, analysts, and anyone who needs to quickly understand their data.

## 🚀 What Makes This Special?

### ✨ **Universal File Support**
- **CSV/TSV**: Tabular data with automatic column detection
- **Excel**: .xlsx and .xls files with multiple sheet support
- **TIF/GeoTIFF**: Spatial raster data with metadata extraction
- **JSON**: Structured data with automatic parsing
- **Parquet**: High-performance columnar data
- **Pickle**: Python serialized objects
- **HDF5**: Scientific data formats

### 🌍 **Country-Agnostic**
- Works with data from **any country** (Ghana, USA, India, Brazil, etc.)
- Automatically detects data structure and content
- No hardcoded country names or assumptions
- Perfect for international research and analysis

### 🧠 **Smart Analysis**
- **Automatic Data Type Detection**: Numeric, categorical, spatial, temporal
- **Data Quality Assessment**: Missing values, duplicates, outliers
- **Statistical Summaries**: Mean, median, std dev, correlations
- **Intelligent Visualizations**: Charts automatically chosen based on data type

## 📋 Quick Start

### 1. **Install Dependencies**
```bash
# Basic installation
pip install -r requirements_universal.txt

# Or install manually
pip install pandas numpy plotly matplotlib
```

### 2. **Add Your Data Files**
Simply drop any supported data files into the same folder:
```
your_project_folder/
├── universal_data_analyzer.py
├── country_data.csv          # Your CSV data
├── spatial_data.tif          # Your TIF data
├── survey_results.xlsx       # Your Excel data
└── population.json           # Your JSON data
```

### 3. **Run the Analyzer**
```bash
python universal_data_analyzer.py
```

### 4. **View Your Dashboard**
Open `universal_dashboard.html` in your web browser!

## 🔧 How It Works

### **1. Automatic File Discovery**
The analyzer scans your folder and automatically detects all supported data files:
```
🔍 Discovering data files...
📁 Found CSV file: country_data.csv
📁 Found TIF file: spatial_data.tif
📁 Found EXCEL file: survey_results.xlsx
```

### **2. Smart Data Reading**
Each file type is read using the appropriate library:
- **CSV**: pandas with automatic encoding detection
- **Excel**: openpyxl with sheet selection
- **TIF**: rasterio with metadata extraction
- **JSON**: pandas with automatic parsing

### **3. Intelligent Analysis**
The analyzer automatically determines what to analyze:
- **Tabular Data**: Column types, missing values, correlations
- **Spatial Data**: Dimensions, CRS, data ranges, valid pixels
- **Mixed Data**: Combines insights from multiple sources

### **4. Automatic Visualization**
Creates appropriate charts based on data type:
- **Numeric Columns**: Histograms, correlation matrices
- **Categorical Columns**: Bar charts, value counts
- **Spatial Data**: Heatmaps, statistics charts
- **Time Series**: Line plots, trends

## 📊 What You Get

### **Dashboard Overview**
- **Files Analyzed**: Total count of processed files
- **File Types**: Different formats detected
- **Total Size**: Combined file sizes
- **Visualizations**: Number of charts created

### **Per-File Analysis**
Each file gets its own section with:

#### **📋 File Summary**
- File dimensions and structure
- Data types and memory usage
- Missing values and duplicates
- Column information

#### **📈 Automatic Visualizations**
- **Distribution Plots**: For numeric data
- **Correlation Matrices**: For multiple numeric columns
- **Value Counts**: For categorical data
- **Spatial Heatmaps**: For TIF files
- **Statistical Charts**: For data summaries

## 🌍 Use Cases

### **International Research**
- **Ghana**: Community vulnerability data
- **USA**: Economic indicators
- **India**: Population demographics
- **Brazil**: Environmental data
- **Any Country**: Drop your data and get instant insights!

### **Data Types**
- **Survey Data**: CSV/Excel with responses
- **Satellite Imagery**: TIF files with spatial data
- **Economic Data**: JSON with financial metrics
- **Scientific Data**: HDF5 with research results
- **Mixed Datasets**: Combine multiple formats

### **Industries**
- **Research**: Academic studies and papers
- **Business**: Market analysis and reports
- **Government**: Policy research and planning
- **Non-Profit**: Impact assessment and monitoring
- **Education**: Teaching data analysis concepts

## 🛠️ Installation Options

### **Basic Installation** (CSV, JSON support)
```bash
pip install pandas numpy plotly matplotlib
```

### **Full Installation** (All file types)
```bash
pip install -r requirements_universal.txt
```

### **Custom Installation** (Choose what you need)
```bash
# For TIF files
pip install rasterio

# For Excel files
pip install openpyxl

# For Parquet files
pip install pyarrow

# For HDF5 files
pip install tables
```

## 🧪 Testing Your Setup

### **Run the Test Script**
```bash
python test_universal.py
```

This will:
- ✅ Check if all required libraries are installed
- 📁 Verify data files are present
- 🎯 Confirm everything is ready to run

### **Expected Output**
```
🧪 Testing Universal Data Analyzer...
==================================================
✅ Basic libraries imported successfully
✅ rasterio available for TIF files
✅ openpyxl available for Excel files
📁 Found 3 supported data files:
   - country_data.csv
   - spatial_data.tif
   - survey_results.xlsx
==================================================
🎉 Ready to run Universal Data Analyzer!
```

## 🚀 Advanced Usage

### **Custom Data Folder**
```python
from universal_data_analyzer import UniversalDataAnalyzer

# Analyze data in a specific folder
analyzer = UniversalDataAnalyzer("path/to/your/data")
output_file = analyzer.run_full_analysis()
```

### **Batch Processing**
```python
# Process multiple folders
folders = ["ghana_data", "usa_data", "india_data"]
for folder in folders:
    analyzer = UniversalDataAnalyzer(folder)
    analyzer.run_full_analysis()
```

### **Custom Analysis**
```python
# Access analysis results
analyzer = UniversalDataAnalyzer()
analyzer.discover_data_files()
analyzer.read_data_file("data.csv", "csv")
analysis = analyzer.analyze_data(data, "data.csv", "csv")
print(analysis['insights'])
```

## 🎨 Dashboard Features

### **Responsive Design**
- Works on desktop, tablet, and mobile
- Automatically adjusts layout for different screen sizes
- Touch-friendly navigation

### **Dark/Light Theme**
- Toggle between themes with one click
- Theme preference saved in browser
- Easy on the eyes for long analysis sessions

### **Interactive Charts**
- **Zoom & Pan**: Explore data in detail
- **Hover Information**: Get precise values
- **Responsive**: Charts adapt to container size
- **Export**: Save charts as images

### **Smart Navigation**
- **Auto-generated**: Based on your data files
- **Quick Access**: Jump to any file section
- **Sticky Header**: Always accessible navigation

## 🔍 Troubleshooting

### **Common Issues**

#### **"No supported data files found"**
- Check file extensions (.csv, .xlsx, .tif, etc.)
- Ensure files are in the same folder as the script
- Verify file permissions

#### **"Error reading file"**
- Check file format and encoding
- Ensure file isn't corrupted
- Install required libraries for that format

#### **"Import error"**
- Install missing dependencies
- Check Python version compatibility
- Use virtual environment if needed

#### **"Memory error"**
- Large TIF files are automatically downsampled
- Close other applications to free memory
- Consider splitting very large files

### **Getting Help**
1. **Check the console output** for specific error messages
2. **Run the test script** to diagnose issues
3. **Verify file formats** are supported
4. **Check file permissions** and accessibility

## 📈 Performance Tips

### **Large Files**
- **TIF files > 100MB**: Automatically downsampled for visualization
- **CSV files > 1GB**: Consider chunking or sampling
- **Excel files**: Multiple sheets processed separately

### **Memory Management**
- **Automatic cleanup**: Memory freed after each file
- **Efficient processing**: Only loads what's needed
- **Progress tracking**: See processing status in real-time

## 🔄 Updating and Maintenance

### **Adding New File Types**
The analyzer is designed to be easily extensible:
1. Add new file extension to `supported_extensions`
2. Implement `_read_[type]_file()` method
3. Add analysis logic in `_analyze_[type]_data()`
4. Create visualizations in `_create_[type]_visualizations()`

### **Updating Dependencies**
```bash
# Update all packages
pip install --upgrade -r requirements_universal.txt

# Update specific package
pip install --upgrade pandas plotly
```

## 🌟 Why This Tool?

### **Traditional Approach**
- ❌ Manual file reading for each format
- ❌ Hardcoded analysis for specific data types
- ❌ Country-specific assumptions
- ❌ Time-consuming setup for each project
- ❌ Limited visualization options

### **Universal Data Analyzer**
- ✅ **One script** handles all file types
- ✅ **Automatic analysis** based on data content
- ✅ **Country-agnostic** - works anywhere
- ✅ **Instant setup** - just drop your data
- ✅ **Rich visualizations** automatically generated

## 🎯 Perfect For

- **Researchers**: Quick data exploration and analysis
- **Analysts**: Rapid insights from multiple data sources
- **Students**: Learning data analysis concepts
- **Business Users**: Understanding customer or market data
- **Government**: Policy research and planning
- **Non-Profits**: Impact assessment and reporting
- **Journalists**: Data-driven storytelling
- **Anyone**: Who needs to understand their data quickly!

## 🚀 Ready to Get Started?

1. **Download** the universal data analyzer
2. **Install** the required dependencies
3. **Drop** your data files in the folder
4. **Run** the analyzer
5. **Explore** your data with the interactive dashboard!

---

**Transform any data into insights with the Universal Data Analyzer!** 🌍✨

*Works with data from any country, any format, any industry - truly universal!* 