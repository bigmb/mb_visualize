# Embedding Visualization Tool

A Docker-based visualization tool for exploring embeddings with associated metadata and images. The tool provides an interactive scatter plot visualization with image display capabilities and metadata exploration.

## Features

- Interactive scatter plot visualization of embeddings
- Click on points to view associated images
- Select multiple points to view multiple images
- Display metadata (image path, date, taxcode) for selected points
- GUI application for easy file selection and viewer launch
- Real-time monitoring of new embedding files
- Docker containerization for easy deployment

## Project Structure

```
.
├── data/
│   ├── embeddings/    # Store embedding JSON files here
│   └── images/        # Store referenced images here
├── app.py            # Main Dash application
├── gui.py            # GUI for file selection and viewer launch
├── Dockerfile        # Docker container configuration
├── docker-compose.yml # Docker Compose configuration
└── requirements.txt  # Python dependencies
```

## Setup Instructions

1. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Docker Setup:
   - Install Docker and Docker Compose
   - Ensure Docker daemon is running

## Usage

1. Place your embedding files in the `data/embeddings` directory
   - Files should be in JSON format with the following structure:
   ```json
   {
     "embeddings": [[x1, y1], [x2, y2], ...],
     "metadata": [
       {
         "image": "path/to/image.jpg",
         "date": "2023-11-20",
         "taxcode": "ABC123"
       },
       ...
     ]
   }
   ```

2. Place corresponding images in the `data/images` directory

3. Launch the GUI:
   ```bash
   python gui.py
   ```

4. Using the GUI:
   - Select an embedding file from the list
   - Click "Launch Viewer" to start the visualization
   - The viewer will open in your default web browser

5. Interacting with the Visualization:
   - Click individual points to view the corresponding image
   - Click and drag to select multiple points
   - Hover over points to see metadata
   - Use the plot toolbar for zooming and panning

## Docker Management

Manual Docker commands (alternative to GUI):

```bash
# Build and start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f
```

## Notes

- The GUI automatically monitors the embeddings directory for new files
- Images are displayed in real-time when points are selected
- The Docker container mounts the local data directory, so files can be added without rebuilding
- The viewer runs on port 8050 by default

## Troubleshooting

1. If the viewer doesn't launch:
   - Check if Docker is running
   - Ensure port 8050 is available
   - Check the Docker logs for errors

2. If images don't display:
   - Verify image paths in the embedding file are correct
   - Ensure images are present in the data/images directory
   - Check file permissions

3. For GUI issues:
   - Restart the GUI application
   - Check if previous Docker containers are still running
