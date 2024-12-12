import streamlit as st
import plotly.express as px
import json
import numpy as np
import pandas as pd
from PIL import Image
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="3D Embedding Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create data directory if it doesn't exist
os.makedirs('data/embeddings', exist_ok=True)
os.makedirs('data/images', exist_ok=True)

@st.cache_data
def load_embedding_file(filename):
    """Load embedding file and return dataframe with embeddings and metadata"""
    data = pd.read_json(filename)
    return data

@st.cache_data
def load_image(image_path):
    """Load and return image"""
    try:
        return Image.open(image_path)
    except Exception as e:
        st.error(f"Error loading image {image_path}: {e}")
        return None

def main():
    st.title("3D Embedding Visualization")

    # Sidebar for file selection
    with st.sidebar:
        st.header("Settings")
        embedding_files = os.listdir('data/embeddings')
        if embedding_files:
            latest_file = max(embedding_files, key=lambda x: os.path.getctime(os.path.join('data/embeddings', x)))
            selected_file = st.selectbox(
                "Select embedding file",
                embedding_files,
                index=embedding_files.index(latest_file)
            )
        else:
            st.error("No embedding files found")
            return

    # Load data
    df = load_embedding_file(os.path.join('data/embeddings', selected_file))

    # Main content area with two columns
    col1, col2 = st.columns([2, 1])

    with col1:
        # Create 3D scatter plot
        fig = px.scatter_3d(
            df,
            x='x',
            y='y',
            z='z',
            hover_data=['image', 'date', 'taxcode'],
            title='3D Embedding Visualization'
        )

        fig.update_layout(
            scene=dict(
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ),
            dragmode='turntable',
            hovermode='closest',
            height=800
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("Selected Point Details")
        
        # Get selected point from plotly click event
        selected_point = st.session_state.get('selected_point', None)
        if selected_point:
            point_index = selected_point['pointIndex']
            row = df.iloc[point_index]
            
            # Display image
            image = load_image(row['image'])
            if image:
                st.image(image, use_column_width=True)
            
            # Display metadata
            st.subheader("Metadata")
            metadata = {
                'Image': row['image'],
                'Date': row['date'],
                'Tax Code': row['taxcode'],
                'Coordinates': {
                    'x': row['x'],
                    'y': row['y'],
                    'z': row['z']
                }
            }
            st.json(metadata)
        else:
            st.info("Click on a point in the plot to view details")

    # Handle plot click events
    st.markdown("""
        <script>
            var plot = document.querySelector('.js-plotly-plot');
            if (plot) {
                plot.on('plotly_click', function(data) {
                    if (data.points.length > 0) {
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: data.points[0]
                        }, '*');
                    }
                });
            }
        </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
