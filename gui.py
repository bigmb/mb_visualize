import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import time
import webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

class EmbeddingViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Embedding Viewer")
        self.geometry("600x400")

        # Create data directories if they don't exist
        os.makedirs('data/embeddings', exist_ok=True)
        os.makedirs('data/images', exist_ok=True)

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Embedding files list
        self.file_list = tk.Listbox(main_frame, width=50, height=15)
        self.file_list.grid(row=0, column=0, columnspan=2, pady=5)

        # Buttons
        ttk.Button(main_frame, text="Refresh", command=self.refresh_files).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Launch Viewer", command=self.launch_viewer).grid(row=1, column=1, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=2, column=0, columnspan=2, pady=5)

        # Initialize file watcher
        self.setup_file_watcher()
        
        # Initial file list population
        self.refresh_files()

    def setup_file_watcher(self):
        class EmbeddingHandler(FileSystemEventHandler):
            def __init__(self, callback):
                self.callback = callback

            def on_created(self, event):
                if not event.is_directory and event.src_path.endswith('.json'):
                    self.callback()

        self.observer = Observer()
        self.observer.schedule(
            EmbeddingHandler(self.refresh_files),
            path='data/embeddings',
            recursive=False
        )
        self.observer.start()

    def refresh_files(self):
        """Refresh the list of embedding files"""
        self.file_list.delete(0, tk.END)
        try:
            files = [f for f in os.listdir('data/embeddings') if f.endswith('.json')]
            for file in sorted(files, key=lambda x: os.path.getctime(os.path.join('data/embeddings', x)), reverse=True):
                self.file_list.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh file list: {str(e)}")

    def launch_viewer(self):
        """Launch the Streamlit viewer in Docker"""
        if not self.file_list.curselection():
            messagebox.showwarning("Warning", "Please select an embedding file first")
            return

        try:
            # Check if Docker is running
            subprocess.run(['docker', 'info'], check=True, capture_output=True)
            
            # Build and run Docker container
            self.status_var.set("Building Docker image...")
            subprocess.run(['docker', 'build', '-t', 'embedding-viewer', '.'], check=True)
            
            self.status_var.set("Starting container...")
            subprocess.run([
                'docker', 'run', '-d',
                '-p', '8501:8501',
                '-v', f'{os.path.abspath("data")}:/app/data',
                '--name', 'embedding-viewer-container',
                'embedding-viewer'
            ], check=True)

            # Wait for the server to start
            time.sleep(3)
            
            # Open web browser
            webbrowser.open('http://localhost:8501')
            self.status_var.set("Viewer launched successfully")

        except subprocess.CalledProcessError as e:
            if 'embedding-viewer-container' in str(e.stderr):
                # Container already exists, try to remove it and retry
                try:
                    subprocess.run(['docker', 'rm', '-f', 'embedding-viewer-container'], check=True)
                    self.launch_viewer()  # Retry launch
                    return
                except subprocess.CalledProcessError as e2:
                    messagebox.showerror("Error", f"Failed to remove existing container: {str(e2)}")
            else:
                messagebox.showerror("Error", f"Failed to launch viewer: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch viewer: {str(e)}")

    def on_closing(self):
        """Clean up resources when closing the application"""
        try:
            self.observer.stop()
            self.observer.join()
            # Stop Docker container if running
            subprocess.run(['docker', 'rm', '-f', 'embedding-viewer-container'], 
                         check=True, capture_output=True)
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = EmbeddingViewer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
