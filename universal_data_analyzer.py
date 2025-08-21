#!/usr/bin/env python3
"""
Universal Data Analyzer Dashboard
Automatically detects, reads, cleans, analyzes, and visualizes any data files
Supports: CSV, TIF, Excel, JSON, Parquet, and more
Works with any country or dataset
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Try to import optional libraries
try:
    import rasterio
    TIF_SUPPORT = True
except ImportError:
    TIF_SUPPORT = False
    print("⚠️  rasterio not available - TIF files will be skipped")

try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False
    print("⚠️  openpyxl not available - Excel files will be skipped")

try:
    import pyarrow
    PARQUET_SUPPORT = True
except ImportError:
    PARQUET_SUPPORT = False
    print("⚠️  pyarrow not available - Parquet files will be skipped")

class UniversalDataAnalyzer:
    """Universal data analyzer that can handle any data type"""
    
    def __init__(self, data_folder: str = "."):
        self.data_folder = Path(data_folder)
        self.data_files = {}
        self.analysis_results = {}
        self.dashboard_config = {}
        
    def discover_data_files(self) -> Dict[str, Dict]:
        """Automatically discover all data files in the folder"""
        print("🔍 Discovering data files...")
        
        supported_extensions = {
            '.csv': 'csv',
            '.xlsx': 'excel' if EXCEL_SUPPORT else None,
            '.xls': 'excel' if EXCEL_SUPPORT else None,
            '.tif': 'tif' if TIF_SUPPORT else None,
            '.tiff': 'tif' if TIF_SUPPORT else None,
            '.json': 'json',
            '.parquet': 'parquet' if PARQUET_SUPPORT else None,
            '.pkl': 'pickle',
            '.h5': 'hdf5'
        }
        
        discovered_files = {}
        
        for file_path in self.data_folder.glob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in supported_extensions and supported_extensions[ext]:
                    file_type = supported_extensions[ext]
                    discovered_files[file_path.name] = {
                        'path': file_path,
                        'type': file_type,
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    }
                    print(f"📁 Found {file_type.upper()} file: {file_path.name}")
        
        self.data_files = discovered_files
        return discovered_files
    
    def read_data_file(self, file_path: Path, file_type: str) -> Any:
        """Read data file based on its type"""
        try:
            if file_type == 'csv':
                return pd.read_csv(file_path)
            elif file_type == 'excel':
                return pd.read_excel(file_path)
            elif file_type == 'json':
                return pd.read_json(file_path)
            elif file_type == 'parquet':
                return pd.read_parquet(file_path)
            elif file_type == 'pickle':
                return pd.read_pickle(file_path)
            elif file_type == 'hdf5':
                return pd.read_hdf(file_path)
            elif file_type == 'tif':
                return self._read_tif_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
            return None
    
    def _read_tif_file(self, file_path: Path) -> Dict:
        """Read TIF file and extract metadata and data"""
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)  # Read first band
                
                # Handle no-data values more robustly
                nodata_value = src.nodata
                if nodata_value is None:
                    # If no explicit no-data value, detect extreme values
                    # Often very large negative numbers indicate no-data
                    data_flat = data.flatten()
                    data_flat = data_flat[np.isfinite(data_flat)]  # Remove inf/nan
                    if len(data_flat) > 0:
                        q1, q99 = np.percentile(data_flat, [1, 99])
                        # If we have extremely low values compared to the rest, treat as no-data
                        if data_flat.min() < (q1 - 100 * (q99 - q1)):
                            # Use the minimum reasonable value as threshold
                            reasonable_min = q1 - 10 * (q99 - q1)
                            nodata_value = reasonable_min
                            print(f"🔍 Detected likely no-data values below {reasonable_min:.2f}")
                
                return {
                    'data': data,
                    'metadata': {
                        'width': src.width,
                        'height': src.height,
                        'bands': src.count,
                        'crs': str(src.crs),
                        'bounds': src.bounds,
                        'nodata': nodata_value,
                        'dtype': str(data.dtype)
                    }
                }
        except Exception as e:
            print(f"❌ Error reading TIF file {file_path.name}: {e}")
            return None
    
    def analyze_data(self, data: Any, file_name: str, file_type: str) -> Dict:
        """Analyze data and generate insights"""
        print(f"📊 Analyzing {file_name}...")
        
        analysis = {
            'file_name': file_name,
            'file_type': file_type,
            'summary': {},
            'visualizations': [],
            'insights': []
        }
        
        if file_type == 'tif':
            analysis.update(self._analyze_tif_data(data))
        else:
            analysis.update(self._analyze_tabular_data(data))
        
        self.analysis_results[file_name] = analysis
        return analysis
    
    def _analyze_tabular_data(self, data: pd.DataFrame) -> Dict:
        """Analyze tabular data (CSV, Excel, etc.)"""
        analysis = {}
        
        # Basic info
        analysis['summary'] = {
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'memory_usage': data.memory_usage(deep=True).sum(),
            'missing_values': data.isnull().sum().to_dict(),
            'duplicates': data.duplicated().sum()
        }
        
        # Data quality insights
        insights = []
        if data.isnull().sum().sum() > 0:
            insights.append(f"⚠️  Found {data.isnull().sum().sum()} missing values")
        
        if data.duplicated().sum() > 0:
            insights.append(f"⚠️  Found {data.duplicated().sum()} duplicate rows")
        
        # Numeric columns analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis['numeric_summary'] = data[numeric_cols].describe().to_dict()
            insights.append(f"📈 Found {len(numeric_cols)} numeric columns for analysis")
        
        # Categorical columns analysis
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            analysis['categorical_summary'] = {}
            for col in categorical_cols:
                analysis['categorical_summary'][col] = {
                    'unique_values': data[col].nunique(),
                    'top_values': data[col].value_counts().head(5).to_dict()
                }
            insights.append(f"📝 Found {len(categorical_cols)} categorical columns")
        
        analysis['insights'] = insights
        return analysis
    
    def _analyze_tif_data(self, data: Dict) -> Dict:
        """Analyze TIF/raster data"""
        analysis = {}
        
        raster_data = data['data']
        metadata = data['metadata']
        
        # Basic stats
        valid_data = raster_data[raster_data != metadata['nodata']] if metadata['nodata'] is not None else raster_data
        
        analysis['summary'] = {
            'dimensions': f"{metadata['width']} × {metadata['height']}",
            'bands': metadata['bands'],
            'crs': metadata['crs'],
            'data_type': metadata['dtype'],
            'valid_pixels': len(valid_data),
            'total_pixels': raster_data.size
        }
        
        if len(valid_data) > 0:
            analysis['numeric_summary'] = {
                'min': float(np.min(valid_data)),
                'max': float(np.max(valid_data)),
                'mean': float(np.mean(valid_data)),
                'median': float(np.median(valid_data)),
                'std': float(np.std(valid_data))
            }
        
        # Insights
        insights = []
        if metadata['nodata'] is not None:
            nodata_count = np.sum(raster_data == metadata['nodata'])
            insights.append(f"🗺️  Spatial data with {nodata_count} no-data pixels")
        else:
            insights.append("🗺️  Spatial raster data")
        
        if len(valid_data) > 0:
            insights.append(f"📊 Data range: {analysis['numeric_summary']['min']:.4f} to {analysis['numeric_summary']['max']:.4f}")
        
        analysis['insights'] = insights
        return analysis
    
    def create_visualizations(self, data: Any, file_name: str, file_type: str) -> List[Dict]:
        """Create appropriate visualizations for the data"""
        visualizations = []
        
        if file_type == 'tif':
            visualizations.extend(self._create_tif_visualizations(data, file_name))
        else:
            visualizations.extend(self._create_tabular_visualizations(data, file_name))
        
        return visualizations
    
    def _create_tif_visualizations(self, data: Dict, file_name: str) -> List[Dict]:
        """Create visualizations for TIF data"""
        viz = []
        
        # Heatmap
        try:
            raster_data = data['data']
            metadata = data['metadata']
            nodata_value = metadata['nodata']
            
            # Filter out no-data values for visualization
            if nodata_value is not None:
                valid_mask = raster_data != nodata_value
                # Also filter out extreme values that might be no-data
                valid_mask = valid_mask & (raster_data > -1e10) & (raster_data < 1e10)
                clean_data = np.where(valid_mask, raster_data, np.nan)
            else:
                # If no explicit no-data value, filter extreme values
                clean_data = np.where(
                    (raster_data > -1e10) & (raster_data < 1e10) & np.isfinite(raster_data), 
                    raster_data, 
                    np.nan
                )
            
            # Sample data for visualization (to avoid memory issues)
            step = 4
            sample_data = clean_data[::step, ::step]
            
            # Create coordinates for better visualization
            x_coords = np.linspace(0, sample_data.shape[1], sample_data.shape[1])
            y_coords = np.linspace(0, sample_data.shape[0], sample_data.shape[0])
            
            # Get valid data range for better color scaling
            valid_sample = sample_data[np.isfinite(sample_data)]
            if len(valid_sample) > 0:
                vmin, vmax = 6.0, 12.0  # fixed range for consistent look
                fig = go.Figure(data=go.Heatmap(
                    z=sample_data,
                    x=x_coords,
                    y=y_coords,
                    colorscale='Viridis',
                    hoverongaps=False,
                    zmin=vmin,
                    zmax=vmax,
                    hovertemplate='<b>Vulnerability Score</b><br>Value: %{z:.4f}<br>X: %{x:.0f}<br>Y: %{y:.0f}<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f"Spatial Vulnerability Heatmap - {file_name}",
                    xaxis_title="X Coordinate (Pixels)",
                    yaxis_title="Y Coordinate (Pixels)",
                    width=800,
                    height=600
                )
                
                viz.append({
                    'type': 'heatmap',
                    'title': 'Spatial Vulnerability Heatmap',
                    'plotly_fig': fig
                })
                print(f"✅ Created heatmap for {file_name} (range: {vmin:.4f} to {vmax:.4f})")
            else:
                print(f"⚠️  No valid data found for heatmap in {file_name}")
        except Exception as e:
            print(f"⚠️  Could not create heatmap: {e}")
            import traceback
            traceback.print_exc()
        
        # Statistics chart
        try:
            # Get clean data for statistics (same filtering as heatmap)
            if nodata_value is not None:
                valid_mask = (raster_data != nodata_value) & (raster_data > -1e10) & (raster_data < 1e10) & np.isfinite(raster_data)
                valid_data = raster_data[valid_mask]
            else:
                valid_mask = (raster_data > -1e10) & (raster_data < 1e10) & np.isfinite(raster_data)
                valid_data = raster_data[valid_mask]
            
            if len(valid_data) > 0:
                stats = {
                    'Min': float(np.min(valid_data)),
                    'Max': float(np.max(valid_data)),
                    'Mean': float(np.mean(valid_data)),
                    'Median': float(np.median(valid_data)),
                    'Std Dev': float(np.std(valid_data))
                }
                
                fig = go.Figure(data=go.Bar(
                    x=list(stats.keys()),
                    y=list(stats.values()),
                    text=[f'{v:.4f}' for v in stats.values()],
                    textposition='auto',
                    marker_color='lightcoral'
                ))
                
                fig.update_layout(
                    title=f"Vulnerability Data Statistics - {file_name}",
                    xaxis_title="Statistic",
                    yaxis_title="Value",
                    width=600,
                    height=400
                )
                
                viz.append({
                    'type': 'statistics',
                    'title': 'Vulnerability Data Statistics',
                    'plotly_fig': fig
                })
                print(f"✅ Created statistics chart for {file_name} ({len(valid_data):,} valid pixels)")
            else:
                print(f"⚠️  No valid data found for statistics in {file_name}")
        except Exception as e:
            print(f"⚠️  Could not create statistics chart: {e}")
            import traceback
            traceback.print_exc()
        
        # Data distribution histogram
        try:
            # Use the same valid_data from statistics
            if len(valid_data) > 0:
                # Sample data if too large for histogram
                if len(valid_data) > 100000:
                    sample_indices = np.random.choice(len(valid_data), 100000, replace=False)
                    hist_data = valid_data[sample_indices]
                else:
                    hist_data = valid_data
                
                fig = go.Figure(data=go.Histogram(
                    x=hist_data,
                    nbinsx=50,
                    marker_color='skyblue',
                    opacity=0.7
                ))
                
                fig.update_layout(
                    title=f"Vulnerability Score Distribution - {file_name}",
                    xaxis_title="Vulnerability Score",
                    yaxis_title="Frequency",
                    width=600,
                    height=400
                )
                
                viz.append({
                    'type': 'histogram',
                    'title': 'Vulnerability Score Distribution',
                    'plotly_fig': fig
                })
                print(f"✅ Created distribution histogram for {file_name}")
        except Exception as e:
            print(f"⚠️  Could not create distribution histogram: {e}")
        
        return viz
    
    def _create_tabular_visualizations(self, data: pd.DataFrame, file_name: str) -> List[Dict]:
        """Create visualizations for tabular data"""
        viz = []
        
        # Numeric columns visualizations
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            # Distribution plots
            for col in numeric_cols[:3]:  # Limit to first 3 columns
                try:
                    fig = px.histogram(data, x=col, title=f"Distribution of {col}")
                    viz.append({
                        'type': 'histogram',
                        'title': f'Distribution of {col}',
                        'plotly_fig': fig
                    })
                except Exception as e:
                    print(f"⚠️  Could not create histogram for {col}: {e}")
            
            # Correlation heatmap if multiple numeric columns
            if len(numeric_cols) > 1:
                try:
                    corr_matrix = data[numeric_cols].corr()
                    fig = px.imshow(
                        corr_matrix,
                        title="Correlation Matrix",
                        color_continuous_scale='RdBu',
                        aspect='auto'
                    )
                    viz.append({
                        'type': 'correlation',
                        'title': 'Correlation Matrix',
                        'plotly_fig': fig
                    })
                except Exception as e:
                    print(f"⚠️  Could not create correlation matrix: {e}")
        
        # Categorical columns visualizations
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:  # Limit to first 2 columns
                try:
                    value_counts = data[col].value_counts().head(10)
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"Top Values in {col}"
                    )
                    viz.append({
                        'type': 'bar',
                        'title': f'Top Values in {col}',
                        'plotly_fig': fig
                    })
                except Exception as e:
                    print(f"⚠️  Could not create bar chart for {col}: {e}")
        
        return viz
    
    def generate_dashboard(self, output_file: str = "universal_dashboard.html"):
        """Generate the complete dashboard HTML"""
        print("🚀 Generating universal dashboard...")
        
        # Convert all visualizations to HTML
        all_viz_html = []
        first_plot = True
        for file_name, analysis in self.analysis_results.items():
            if 'visualizations' in analysis:
                for viz in analysis['visualizations']:
                    html = pio.to_html(viz['plotly_fig'], include_plotlyjs=False, full_html=False, config={"responsive": True})
                    all_viz_html.append({
                        'file_name': file_name,
                        'title': viz['title'],
                        'html': html
                    })
        
        # Create navigation
        nav_links = ""
        for file_name, analysis in self.analysis_results.items():
            nav_links += f'<a href="#{file_name.replace(".", "_")}">{file_name}</a>'
        
        # Create dashboard sections
        dashboard_sections = ""
        for file_name, analysis in self.analysis_results.items():
            section_id = file_name.replace(".", "_")
            
            # File summary
            summary_html = self._create_summary_html(analysis)
            
            # Visualizations
            viz_html = ""
            if 'visualizations' in analysis and analysis['visualizations']:
                for viz in analysis['visualizations']:
                    viz_html += f'''
                    <div class="chart">
                        <h3>{viz["title"]}</h3>
                        <div class="chart-container">
                            {pio.to_html(viz["plotly_fig"], include_plotlyjs=False, full_html=False, config={'responsive': True})}
                        </div>
                    </div>
                    '''
            else:
                viz_html = '<div class="no-viz"><p>No visualizations available for this file type.</p></div>'
            
            dashboard_sections += f'''
            <section id="{section_id}" class="section">
                <h2>📊 {file_name}</h2>
                <div class="file-summary">{summary_html}</div>
                {viz_html}
            </section>
            '''
        
        # Generate complete HTML with improved styling
        html_content = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Universal Data Analyzer Dashboard</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --text: #1e293b;
            --muted: #64748b;
            --card: #ffffff;
            --accent: #3b82f6;
            --accent-light: #60a5fa;
            --shadow: 0 10px 25px rgba(0,0,0,0.1);
            --border: #e2e8f0;
        }}
        body.dark {{
            --bg: #0f172a;
            --text: #f1f5f9;
            --muted: #94a3b8;
            --card: #1e293b;
            --accent: #60a5fa;
            --accent-light: #93c5fd;
            --shadow: 0 10px 25px rgba(0,0,0,0.3);
            --border: #334155;
        }}
        html, body {{ height: 100%; }}
        body {{ 
            margin: 0; padding: 0; 
            background: var(--bg); color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            line-height: 1.6;
        }}
        .navbar {{ 
            position: sticky; top: 0; z-index: 50; 
            backdrop-filter: saturate(180%) blur(20px);
            background: rgba(255,255,255,0.8); 
            border-bottom: 1px solid var(--border);
            box-shadow: var(--shadow);
        }}
        body.dark .navbar {{ 
            background: rgba(30,41,59,0.8); 
            border-color: var(--border);
        }}
        .nav-inner {{ 
            display: flex; align-items: center; justify-content: space-between; 
            padding: 15px 20px; 
        }}
        .brand {{ 
            font-weight: 800; letter-spacing: 0.4px; 
            font-size: 1.2rem; color: var(--accent);
        }}
        .links {{ 
            display: flex; gap: 15px; flex-wrap: wrap;
        }}
        .links a {{ 
            color: var(--text); text-decoration: none; 
            padding: 8px 16px; border-radius: 20px;
            background: var(--card); border: 1px solid var(--border);
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }}
        .links a:hover {{ 
            background: var(--accent); color: white; 
            transform: translateY(-2px); box-shadow: var(--shadow);
        }}
        .toggle {{ 
            border: 1px solid var(--border); background: var(--card); 
            color: var(--text); border-radius: 25px; padding: 8px 16px; 
            cursor: pointer; transition: all 0.3s ease;
        }}
        .toggle:hover {{ background: var(--accent); color: white; }}
        body.dark .toggle {{ border-color: var(--border); }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 20px; }}
        
        .header {{ 
            position: relative; text-align: center; color: white; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 80px 20px; border-radius: 0 0 30px 30px;
            margin-bottom: 40px; box-shadow: var(--shadow);
        }}
        .header h1 {{ 
            margin: 0; font-size: 3rem; font-weight: 800;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        .header p {{ 
            margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.9;
        }}
        
        .overview {{ 
            background: var(--card); border-radius: 20px; padding: 30px; 
            margin-bottom: 40px; box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }}
        .overview h2 {{ 
            margin: 0 0 25px 0; color: var(--accent); 
            font-size: 1.8rem; border-bottom: 3px solid var(--accent);
            padding-bottom: 15px;
        }}
        .stats-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px; 
        }}
        .stat {{ 
            text-align: center; padding: 25px; 
            background: var(--bg); border-radius: 15px;
            border: 1px solid var(--border); transition: transform 0.3s ease;
        }}
        .stat:hover {{ transform: translateY(-5px); }}
        .stat h3 {{ margin: 0 0 15px 0; font-size: 1rem; color: var(--muted); }}
        .stat .value {{ font-size: 2rem; font-weight: 800; color: var(--accent); }}
        
        .section {{ 
            margin: 40px 0; scroll-margin-top: 100px; 
            background: var(--card); border-radius: 20px; padding: 30px;
            box-shadow: var(--shadow); border: 1px solid var(--border);
        }}
        .section h2 {{ 
            margin: 0 0 25px 0; font-size: 2rem; 
            color: var(--text); border-bottom: 3px solid var(--accent);
            padding-bottom: 15px; display: flex; align-items: center;
        }}
        .section h2::before {{ content: "📊 "; margin-right: 10px; }}
        
        .file-summary {{ 
            background: var(--bg); border-radius: 15px; padding: 25px; 
            margin-bottom: 30px; border: 1px solid var(--border);
        }}
        .file-summary h3 {{ 
            margin: 0 0 20px 0; color: var(--accent); 
            font-size: 1.3rem; border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
        }}
        .summary-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px; 
        }}
        .summary-item {{ 
            background: var(--card); padding: 20px; border-radius: 12px;
            border-left: 4px solid var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .summary-item h4 {{ margin: 0 0 10px 0; font-size: 0.9rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .summary-item .value {{ font-size: 1.2rem; font-weight: 600; color: var(--text); }}
        
        .chart {{ 
            margin: 30px 0; padding: 25px; 
            background: var(--bg); border-radius: 15px;
            border: 1px solid var(--border);
        }}
        .chart h3 {{ 
            margin: 0 0 20px 0; color: var(--text); 
            font-size: 1.4rem; border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
        }}
        .chart-container {{
            min-height: 400px; background: var(--card); border-radius: 10px;
            padding: 20px; border: 1px solid var(--border);
            width: 100%; overflow: hidden;
        }}
        .chart-container .plotly-graph-div {{
            width: 100% !important;
            height: 100% !important;
        }}
        .no-viz {{
            text-align: center; padding: 60px 20px; color: var(--muted);
            font-style: italic; background: var(--card); border-radius: 10px;
            border: 2px dashed var(--border);
        }}
        
        footer {{ 
            color: var(--muted); font-size: 1rem; text-align: center; 
            padding: 60px 0; margin-top: 80px;
            border-top: 1px solid var(--border);
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .header p {{ font-size: 1.1rem; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .summary-grid {{ grid-template-columns: 1fr; }}
            .links {{ flex-direction: column; gap: 10px; }}
        }}
    </style>

    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="container nav-inner">
            <div class="brand">🌍 Universal Data Analyzer</div>
            <div class="links">{nav_links}</div>
            <button id="themeToggle" class="toggle" aria-label="Toggle theme">🌙</button>
        </div>
    </nav>

    <div class="header">
        <h1>Universal Data Analyzer Dashboard</h1>
        <p>🔍 Automatically analyzes any data files - CSV, TIF, Excel, JSON, and more</p>
    </div>

    <div class="container">
        <div class="overview">
            <h2>📊 Analysis Overview</h2>
            <div class="stats-grid">
                <div class="stat">
                    <h3>Files Analyzed</h3>
                    <div class="value">{len(self.data_files)}</div>
                </div>
                <div class="stat">
                    <h3>File Types</h3>
                    <div class="value">{len(set(f['type'] for f in self.data_files.values()))}</div>
                </div>
                <div class="stat">
                    <h3>Total Size</h3>
                    <div class="value">{sum(f['size'] for f in self.data_files.values()) / 1024 / 1024:.1f} MB</div>
                </div>
                <div class="stat">
                    <h3>Visualizations</h3>
                    <div class="value">{len(all_viz_html)}</div>
                </div>
            </div>
        </div>

        {dashboard_sections}

        <footer>
            🚀 Built with Universal Data Analyzer • Supports CSV, TIF, Excel, JSON, and more • 
            Toggle dark mode for better viewing • Works with data from any country!
        </footer>
    </div>

    
    <script>
        (function(){{
            const key = 'universal_dashboard_theme';
            const body = document.body;
            const btn = document.getElementById('themeToggle');
            const saved = localStorage.getItem(key);
            if (saved === 'dark') {{ body.classList.add('dark'); btn.textContent = '☀️'; }}
            btn.addEventListener('click', function(){{
                body.classList.toggle('dark');
                const isDark = body.classList.contains('dark');
                btn.textContent = isDark ? '☀️' : '🌙';
                localStorage.setItem(key, isDark ? 'dark' : 'light');
            }});
        }})();
    </script>
</body>
</html>
        """
        
        # Write to file
        output_path = Path(output_file)
        output_path.write_text(html_content, encoding='utf-8')
        print(f"✅ Dashboard generated: {output_file}")
        
        return output_file
    
    def _create_summary_html(self, analysis: Dict) -> str:
        """Create HTML summary for a file analysis"""
        summary = analysis.get('summary', {})
        
        summary_items = []
        for key, value in summary.items():
            if isinstance(value, dict):
                # Handle nested summaries
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        display_value = f"{sub_value:,}" if isinstance(sub_value, int) else f"{sub_value:.4f}"
                    else:
                        display_value = str(sub_value)
                    summary_items.append(f'<div class="summary-item"><h4>{sub_key.replace("_", " ").title()}</h4><div class="value">{display_value}</div></div>')
            else:
                if isinstance(value, (int, float)):
                    display_value = f"{value:,}" if isinstance(value, int) else f"{value:.4f}"
                else:
                    display_value = str(value)
                summary_items.append(f'<div class="summary-item"><h4>{key.replace("_", " ").title()}</h4><div class="value">{display_value}</div></div>')
        
        return f'''
        <h3>📋 File Summary</h3>
        <div class="summary-grid">
            {''.join(summary_items)}
        </div>
        '''
    
    def run_full_analysis(self) -> str:
        """Run complete analysis pipeline"""
        print("🚀 Starting Universal Data Analysis...")
        
        # 1. Discover files
        self.discover_data_files()
        
        if not self.data_files:
            print("❌ No supported data files found!")
            return None
        
        # 2. Read and analyze each file
        for file_name, file_info in self.data_files.items():
            print(f"\n📖 Processing {file_name}...")
            
            # Read data
            data = self.read_data_file(file_info['path'], file_info['type'])
            if data is None:
                print(f"❌ Failed to read {file_name}")
                continue
            
            # Analyze data
            analysis = self.analyze_data(data, file_name, file_info['type'])
            
            # Create visualizations
            print(f"🎨 Creating visualizations for {file_name}...")
            visualizations = self.create_visualizations(data, file_name, file_info['type'])
            analysis['visualizations'] = visualizations
            
            print(f"✅ {file_name} processed successfully with {len(visualizations)} visualizations")
        
        # 3. Generate dashboard
        print(f"\n🌐 Generating dashboard with {sum(len(analysis.get('visualizations', [])) for analysis in self.analysis_results.values())} total visualizations...")
        output_file = self.generate_dashboard()
        
        print(f"\n🎉 Analysis complete! Dashboard saved to: {output_file}")
        return output_file

def main():
    """Main function to run the universal data analyzer"""
    analyzer = UniversalDataAnalyzer()
    
    try:
        output_file = analyzer.run_full_analysis()
        if output_file:
            print(f"\n🌐 Open {output_file} in your web browser to view the dashboard!")
        else:
            print("\n❌ Analysis failed. Check the error messages above.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 