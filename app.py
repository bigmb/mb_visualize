import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import json
import numpy as np
import pandas as pd
from PIL import Image
import base64
import io
import os
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create data directory if it doesn't exist
os.makedirs('data/embeddings', exist_ok=True)
os.makedirs('data/images', exist_ok=True)

def load_embedding_file(filename):
    """Load embedding file and return dataframe with embeddings and metadata"""
    data = pd.read_json(filename)
    return data

def encode_image(image_path):
    """Encode image to base64 for display"""
    try:
        img = Image.open(image_path)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded_image}"
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("3D Embedding Visualization", className="text-center mb-4"),
            dcc.Store(id='embedding-data'),
            dcc.Graph(
                id='embedding-plot',
                style={'height': '70vh'},
                config={'displayModeBar': True}
            ),
        ], width=8),
        dbc.Col([
            html.Div([
                html.H4("Selected Images"),
                html.Div(id='image-display', style={'maxHeight': '70vh', 'overflow': 'auto'}),
            ])
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Metadata"),
                html.Pre(id='metadata-display')
            ])
        ])
    ])
])

@app.callback(
    [Output('embedding-plot', 'figure'),
     Output('embedding-data', 'data')],
    [Input('embedding-data', 'data')]
)
def update_plot(data):
    if data is None:
        # Load default or most recent embedding file
        embedding_files = os.listdir('data/embeddings')
        if not embedding_files:
            return dash.no_update
        
        latest_file = max(embedding_files, key=lambda x: os.path.getctime(os.path.join('data/embeddings', x)))
        df = load_embedding_file(os.path.join('data/embeddings', latest_file))
    else:
        df = pd.DataFrame(data)
    
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
        hovermode='closest'
    )
    
    return fig, df.to_dict('records')

@app.callback(
    [Output('image-display', 'children'),
     Output('metadata-display', 'children')],
    [Input('embedding-plot', 'selectedData'),
     Input('embedding-plot', 'clickData')],
    [State('embedding-data', 'data')]
)
def display_selected_data(selected_data, click_data, data):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not data:
        return [], "No data loaded"
    
    df = pd.DataFrame(data)
    
    if trigger_id == 'embedding-plot':
        if selected_data and len(selected_data['points']) > 0:
            # Handle multiple selected points
            points = selected_data['points']
            images = []
            metadata = []
            
            for point in points:
                idx = point['pointIndex']
                image_path = df.iloc[idx]['image']
                encoded_image = encode_image(image_path)
                if encoded_image:
                    images.append(
                        dbc.Col([
                            html.Img(src=encoded_image, style={'width': '100%', 'marginBottom': '10px'})
                        ])
                    )
                metadata.append({
                    'image': image_path,
                    'date': df.iloc[idx]['date'],
                    'taxcode': df.iloc[idx]['taxcode'],
                    'coordinates': {
                        'x': df.iloc[idx]['x'],
                        'y': df.iloc[idx]['y'],
                        'z': df.iloc[idx]['z']
                    }
                })
            
            return [
                dbc.Row(images)
            ], json.dumps(metadata, indent=2)
        
        elif click_data:
            # Handle single clicked point
            idx = click_data['points'][0]['pointIndex']
            image_path = df.iloc[idx]['image']
            encoded_image = encode_image(image_path)
            
            if encoded_image:
                return [
                    dbc.Row([
                        dbc.Col([
                            html.Img(src=encoded_image, style={'width': '100%'})
                        ])
                    ])
                ], json.dumps({
                    'image': image_path,
                    'date': df.iloc[idx]['date'],
                    'taxcode': df.iloc[idx]['taxcode'],
                    'coordinates': {
                        'x': df.iloc[idx]['x'],
                        'y': df.iloc[idx]['y'],
                        'z': df.iloc[idx]['z']
                    }
                }, indent=2)
    
    return [], "Select points to view images and metadata"

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
