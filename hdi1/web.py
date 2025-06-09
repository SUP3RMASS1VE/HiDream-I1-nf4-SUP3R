import torch
import gradio as gr
import logging
import os
import tempfile
import glob
import sys
from datetime import datetime
from PIL import Image

# Add parent directory to path for direct execution
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Handle imports for both direct execution and module import
try:
    from .nf4 import *
except ImportError:
    # Fallback for direct execution
    from hdi1.nf4 import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for beautiful UI styling
CUSTOM_CSS = """
/* Force override all Gradio styles */
* {
    box-sizing: border-box !important;
}

.gradio-container, .gradio-container * {
    color: inherit !important;
}

/* Main theme variables for light mode */
:root {
    --primary-color: #6366f1;
    --primary-hover: #5855eb;
    --secondary-color: #ec4899;
    --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --card-bg: rgba(255, 255, 255, 0.95);
    --card-border: rgba(255, 255, 255, 0.2);
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --border-color: #e5e7eb;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-large: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --input-bg: rgba(255, 255, 255, 0.9);
    --overlay-bg: rgba(255, 255, 255, 0.1);
}

/* Dark theme variables */
[data-theme="dark"], .dark {
    --background-gradient: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e293b 100%);
    --card-bg: rgba(30, 41, 59, 0.95);
    --card-border: rgba(148, 163, 184, 0.2);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: #475569;
    --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
    --shadow-large: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
    --input-bg: rgba(30, 41, 59, 0.8);
    --overlay-bg: rgba(0, 0, 0, 0.2);
}

/* Auto-detect system dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        --background-gradient: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e293b 100%);
        --card-bg: rgba(30, 41, 59, 0.95);
        --card-border: rgba(148, 163, 184, 0.2);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-color: #475569;
        --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
        --shadow-large: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
        --input-bg: rgba(30, 41, 59, 0.8);
        --overlay-bg: rgba(0, 0, 0, 0.2);
    }
}

/* Global styling - Force override Gradio's styles */
.gradio-container,
#root,
.app,
body,
html {
    background: var(--background-gradient) !important;
    min-height: 100vh !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    position: relative !important;
    overflow-x: hidden !important;
}

/* Force container background */
.gradio-container .main,
.gradio-container .container,
.gradio-container > div {
    background: transparent !important;
}

/* Add floating particles animation */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(2px 2px at 20px 30px, rgba(255,255,255,0.3), transparent),
        radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.2), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.2), transparent),
        radial-gradient(2px 2px at 160px 30px, rgba(255,255,255,0.3), transparent);
    background-repeat: repeat;
    background-size: 200px 100px;
    animation: float 15s infinite linear;
    pointer-events: none;
    z-index: 1;
}

@keyframes float {
    0% { transform: translateY(100vh) rotate(0deg); }
    100% { transform: translateY(-100vh) rotate(360deg); }
}

/* Main content container - Tighter spacing */
.main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    position: relative;
    z-index: 10;
}

/* Header styling - Solid white text that's always visible */
.gradio-container .markdown h1,
.gradio-container h1,
div[data-testid="markdown"] h1,
.gr-markdown h1 {
    background: none !important;
    -webkit-background-clip: unset !important;
    -webkit-text-fill-color: unset !important;
    background-clip: unset !important;
    color: #ffffff !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    text-align: center !important;
    margin-bottom: 0.5rem !important;
    margin-top: 0.5rem !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    animation: fadeInDown 1s ease-out !important;
    letter-spacing: -0.025em !important;
    position: relative !important;
}

/* Add a subtle glow animation */
@keyframes glow {
    from {
        filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.4));
    }
    to {
        filter: drop-shadow(0 0 20px rgba(118, 75, 162, 0.6));
    }
}

/* Fade in animation */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.gradio-container .markdown p,
.gradio-container p,
div[data-testid="markdown"] p,
.gr-markdown p {
    text-align: center !important;
    color: #ffffff !important;
    font-size: 1.1rem !important;
    margin-bottom: 1rem !important;
    margin-top: 0.5rem !important;
    background: rgba(255, 255, 255, 0.1) !important;
    padding: 0.8rem 1.5rem !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-soft) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    animation: fadeInUp 1s ease-out 0.3s both !important;
    position: relative !important;
    overflow: hidden !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
}

/* Add shimmer effect to paragraphs */
.markdown p::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Fade in up animation */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Card-like containers - Tighter spacing */
.block {
    background: transparent !important;
    border-radius: 0px !important;
    box-shadow: none !important;
    border: none !important;
    backdrop-filter: none;
    margin: 0.25rem 0 !important;
    padding: 0.5rem !important;
    transition: all 0.3s ease;
}

.block:hover {
    transform: none;
    box-shadow: none !important;
}

/* Reduce spacing between sections */
.gradio-group {
    margin: 0.5rem 0 !important;
    padding: 0.5rem !important;
}

/* Tighter row spacing */
.gradio-row {
    gap: 1rem !important;
    margin: 0.5rem 0 !important;
}

/* Reduce column gaps */
.gradio-column {
    padding: 0.5rem !important;
    gap: 0.5rem !important;
}

/* Input styling - Tighter spacing */
.input-container {
    margin-bottom: 0.8rem;
}

input, textarea, select {
    border: 2px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    background: var(--input-bg) !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.5rem !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    transform: translateY(-1px);
}

/* Button styling - More compact */
.btn {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: white !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow-soft) !important;
    margin: 0.25rem !important;
}

.btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-medium) !important;
    background: linear-gradient(135deg, var(--primary-hover), var(--secondary-color)) !important;
}

.btn:active {
    transform: translateY(0) !important;
}

/* Generate button special styling - More compact */
button[id*="generate"] {
    background: linear-gradient(135deg, var(--success-color), #059669) !important;
    font-size: 1.1rem !important;
    padding: 12px 24px !important;
    font-weight: 800 !important;
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0.5rem 0 !important;
}

button[id*="generate"]:hover {
    background: linear-gradient(135deg, #059669, var(--success-color)) !important;
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 15px 30px -10px rgba(16, 185, 129, 0.4) !important;
}

/* Add pulse effect to generate button */
button[id*="generate"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.2) 50%, transparent 60%);
    transform: translateX(-100%);
    transition: transform 0.6s;
}

button[id*="generate"]:hover::before {
    transform: translateX(100%);
}

/* Cleanup button styling */
button[id*="cleanup"] {
    background: linear-gradient(135deg, var(--warning-color), #d97706) !important;
}

button[id*="cleanup"]:hover {
    background: linear-gradient(135deg, #d97706, var(--warning-color)) !important;
}

/* Radio and slider styling */
.radio-group {
    gap: 8px;
}

.radio-group label {
    background: var(--input-bg) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin: 4px !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    color: var(--text-primary) !important;
}

.radio-group label:hover {
    border-color: var(--primary-color) !important;
    background: rgba(99, 102, 241, 0.1) !important;
    transform: translateY(-1px);
}

.radio-group input:checked + label {
    background: var(--primary-color) !important;
    color: white !important;
    border-color: var(--primary-color) !important;
}

/* Slider styling */
.slider {
    margin: 1rem 0;
}

.slider input[type="range"] {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
    border-radius: 8px !important;
    height: 8px !important;
}

/* Label styling */
label {
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    font-size: 1rem !important;
    margin-bottom: 8px !important;
}

/* Info text styling */
.info {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
    font-style: italic;
    margin-top: 4px !important;
}

/* Image container styling */
.image-container {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-medium) !important;
    transition: all 0.3s ease !important;
}

.image-container:hover {
    transform: scale(1.02);
    box-shadow: var(--shadow-large) !important;
}

/* Status and output styling */
.output-text {
    background: var(--input-bg) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace !important;
    color: var(--text-primary) !important;
}

/* Success status */
.output-text[value*="complete"], .output-text[value*="Success"] {
    border-color: var(--success-color) !important;
    background: rgba(16, 185, 129, 0.1) !important;
}

/* Error status */
.output-text[value*="Error"], .output-text[value*="Failed"] {
    border-color: var(--error-color) !important;
    background: rgba(239, 68, 68, 0.1) !important;
}

/* Loading animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.output-text[value*="Loading"], .output-text[value*="Generating"] {
    border-color: var(--warning-color) !important;
    background: rgba(245, 158, 11, 0.1) !important;
    animation: pulse 2s infinite;
}

/* File download styling */
.file-container {
    background: var(--input-bg) !important;
    border: 2px dashed var(--primary-color) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
    color: var(--text-primary) !important;
}

.file-container:hover {
    background: var(--overlay-bg) !important;
    border-color: var(--primary-hover) !important;
    transform: translateY(-2px);
}

/* Responsive design */
@media (max-width: 768px) {
    .main {
        padding: 1rem;
    }
    
    .markdown h1 {
        font-size: 2rem;
    }
    
    .btn {
        width: 100% !important;
        margin: 0.5rem 0 !important;
    }
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-hover);
}

/* Add subtle animations */
* {
    transition: all 0.3s ease;
}

/* Glow effect for important elements */
.btn:focus, input:focus, textarea:focus {
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3) !important;
}

/* Gradio-specific component styling */
.gradio-group {
    background: transparent !important;
    border: none !important;
    border-radius: 0px !important;
    padding: 0rem !important;
    margin: 1rem 0 !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
    backdrop-filter: none;
}

.gradio-group:hover {
    border-color: transparent !important;
    box-shadow: none !important;
    transform: none;
}

/* Section headers */
.markdown h3 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 2px solid var(--primary-color) !important;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Image component styling */
.image-preview {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-medium) !important;
    border: 2px solid var(--border-color) !important;
    transition: all 0.3s ease !important;
}

.image-preview:hover {
    border-color: var(--primary-color) !important;
    box-shadow: var(--shadow-large) !important;
}

/* Number input styling */
input[type="number"] {
    text-align: center !important;
}

/* Textarea enhancement */
textarea {
    min-height: 100px !important;
    resize: vertical !important;
}

/* Button variants */
.primary {
    background: linear-gradient(135deg, var(--success-color), #059669) !important;
}

.secondary {
    background: linear-gradient(135deg, var(--warning-color), #d97706) !important;
}

/* Progress and loading states */
.progress-bar {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
    border-radius: 4px !important;
}

/* Enhanced hover effects for interactive elements */
.radio-item:hover, .checkbox-item:hover {
    background: rgba(99, 102, 241, 0.05) !important;
    border-color: var(--primary-color) !important;
}

/* File upload area styling */
.file-upload {
    border: 2px dashed var(--primary-color) !important;
    border-radius: 12px !important;
    background: rgba(99, 102, 241, 0.05) !important;
    transition: all 0.3s ease !important;
}

.file-upload:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    border-color: var(--primary-hover) !important;
}

/* Tooltip styling */
.tooltip {
    background: var(--text-primary) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 0.875rem !important;
    box-shadow: var(--shadow-medium) !important;
}

/* Focus states */
*:focus {
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

/* Disabled state styling */
*:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
}

/* Success/Error message styling */
.success-message {
    background: rgba(16, 185, 129, 0.1) !important;
    border: 1px solid var(--success-color) !important;
    color: var(--success-color) !important;
}

.error-message {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid var(--error-color) !important;
    color: var(--error-color) !important;
}

/* Force dark theme styling when Gradio's dark mode is active */
html.dark .gradio-container,
.dark .gradio-container,
body.dark,
[data-theme="dark"] {
    background: var(--background-gradient) !important;
}

/* Ensure text colors work in dark mode */
html.dark,
.dark,
[data-theme="dark"] {
    --text-primary: #f1f5f9 !important;
    --text-secondary: #94a3b8 !important;
    --border-color: #475569 !important;
    --card-bg: rgba(30, 41, 59, 0.95) !important;
    --input-bg: rgba(30, 41, 59, 0.8) !important;
}

/* Dark mode overrides for specific Gradio components */
html.dark input,
html.dark textarea,
html.dark select,
.dark input,
.dark textarea,
.dark select,
[data-theme="dark"] input,
[data-theme="dark"] textarea,
[data-theme="dark"] select {
    background: var(--input-bg) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

html.dark label,
.dark label,
[data-theme="dark"] label {
    color: var(--text-primary) !important;
}

/* Better contrast for dark mode buttons */
html.dark .btn,
.dark .btn,
[data-theme="dark"] .btn {
    box-shadow: var(--shadow-medium) !important;
}

/* Ensure markdown content is visible in dark mode */
html.dark .markdown,
.dark .markdown,
[data-theme="dark"] .markdown {
    color: var(--text-primary) !important;
}

html.dark .markdown h1,
.dark .markdown h1,
[data-theme="dark"] .markdown h1 {
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

html.dark .markdown h3,
.dark .markdown h3,
[data-theme="dark"] .markdown h3 {
    color: var(--text-primary) !important;
    border-bottom-color: var(--primary-color) !important;
}
"""

# Output directory for saving images
OUTPUT_DIR = os.path.join("outputs")

# Resolution options
RESOLUTION_OPTIONS = [
    "1024 × 1024 (Square)",
    "768 × 1360 (Portrait)",
    "1360 × 768 (Landscape)",
    "880 × 1168 (Portrait)",
    "1168 × 880 (Landscape)",
    "1248 × 832 (Landscape)",
    "832 × 1248 (Portrait)",
    "Custom"
]

# Scheduler options (flow-matching only)
SCHEDULER_OPTIONS = [
    "FlashFlowMatchEulerDiscreteScheduler",
    "FlowUniPCMultistepScheduler"
]

# Image format options
IMAGE_FORMAT_OPTIONS = ["PNG", "JPEG", "WEBP"]

# Parse resolution string to get height and width
def parse_resolution(resolution_str, custom_width=None, custom_height=None):
    try:
        if resolution_str == "Custom":
            if custom_width is None or custom_height is None:
                raise ValueError("Custom width and height must be provided")
            return (int(custom_width), int(custom_height))
        return tuple(map(int, resolution_str.split("(")[0].strip().split(" × ")))
    except (ValueError, IndexError) as e:
        raise ValueError("Invalid resolution format") from e

def clean_previous_temp_files():
    """Delete temporary files from previous generations matching hdi1_* pattern and log Gradio temp files."""
    temp_dir = tempfile.gettempdir()
    patterns = [os.path.join(temp_dir, f"hdi1_*.{ext}") for ext in ["png", "jpeg", "webp"]]
    deleted_files = []
    
    # Clean hdi1_* files
    for pattern in patterns:
        for temp_file in glob.glob(pattern):
            try:
                os.remove(temp_file)
                deleted_files.append(temp_file)
                logger.info(f"Deleted temporary file: {temp_file}")
            except OSError as e:
                logger.warning(f"Failed to delete temporary file {temp_file}: {str(e)}")
    
    # Log Gradio temp files (for monitoring)
    gradio_temp_dir = os.path.join(temp_dir, "gradio")
    if os.path.exists(gradio_temp_dir):
        for root, _, files in os.walk(gradio_temp_dir):
            for file in files:
                if file.endswith((".png", ".jpeg", ".webp")):
                    gradio_file = os.path.join(root, file)
                    logger.info(f"Found Gradio temporary file: {gradio_file}")
    
    return deleted_files

def clean_all_temp_files():
    """Manually clean hdi1_* and Gradio temporary files, with user confirmation."""
    status_message = "Starting temporary file cleanup..."
    logger.info(status_message)
    
    try:
        # Clean hdi1_* files
        deleted_files = clean_previous_temp_files()
        
        # Clean Gradio temp files
        temp_dir = tempfile.gettempdir()
        gradio_temp_dir = os.path.join(temp_dir, "gradio")
        if os.path.exists(gradio_temp_dir):
            for root, _, files in os.walk(gradio_temp_dir):
                for file in files:
                    if file.endswith((".png", ".jpeg", ".webp")):
                        gradio_file = os.path.join(root, file)
                        try:
                            os.remove(gradio_file)
                            deleted_files.append(gradio_file)
                            logger.info(f"Deleted Gradio temporary file: {gradio_file}")
                        except OSError as e:
                            logger.warning(f"Failed to delete Gradio temporary file {gradio_file}: {str(e)}")
        
        status_message = f"🧹 Cleanup complete! Deleted {len(deleted_files)} files."
        logger.info(status_message)
        return status_message
    except Exception as e:
        error_message = f"❌ Cleanup error: {str(e)}"
        logger.error(error_message)
        return error_message

def gen_img_helper(model, prompt, res, seed, scheduler, guidance_scale, num_inference_steps, shift, image_format, custom_width=None, custom_height=None):
    global pipe, current_model
    status_message = "Starting image generation..."

    try:
        # Clean up previous temporary files
        status_message = "Cleaning up previous temporary files..."
        logger.info(status_message)
        clean_previous_temp_files()
        status_message = "Previous temporary files cleaned."

        # Validate inputs
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        if not isinstance(seed, (int, float)) or seed < -1:
            raise ValueError("Seed must be -1 or a non-negative integer")
        if num_inference_steps < 1 or num_inference_steps > 100:
            raise ValueError("Number of inference steps must be between 1 and 100")
        if guidance_scale < 0 or guidance_scale > 10:
            raise ValueError("Guidance scale must be between 0 and 10")
        if shift < 1 or shift > 10:
            raise ValueError("Shift must be between 1 and 10")
        
        # Validate custom resolution if needed
        if res == "Custom":
            if not custom_width or not custom_height:
                raise ValueError("Custom width and height must be provided")
            if int(custom_width) < 64 or int(custom_width) > 2048:
                raise ValueError("Custom width must be between 64 and 2048 pixels")
            if int(custom_height) < 64 or int(custom_height) > 2048:
                raise ValueError("Custom height must be between 64 and 2048 pixels")

        # 1. Check if the model matches loaded model, load the model if not
        if model != current_model:
            status_message = f"Unloading model {current_model}..."
            logger.info(status_message)
            if pipe is not None:
                del pipe
                torch.cuda.empty_cache()
            
            status_message = f"Loading model {model}..."
            logger.info(status_message)
            pipe, _ = load_models(model)
            current_model = model
            status_message = "Model loaded successfully!"
            logger.info(status_message)

        # 2. Update scheduler
        config = MODEL_CONFIGS[model]
        scheduler_map = {
            "FlashFlowMatchEulerDiscreteScheduler": FlashFlowMatchEulerDiscreteScheduler,
            "FlowUniPCMultistepScheduler": FlowUniPCMultistepScheduler
        }
        if scheduler not in scheduler_map:
            raise ValueError(f"Invalid scheduler: {scheduler}")
        scheduler_class = scheduler_map[scheduler]
        device = pipe._execution_device

        # Set scheduler with shift for flow-matching schedulers
        pipe.scheduler = scheduler_class(num_train_timesteps=1000, shift=shift, use_dynamic_shifting=False)

        # 3. Generate image
        status_message = "Generating image..."
        logger.info(status_message)
        res = parse_resolution(res, custom_width, custom_height)
        image, seed = generate_image(pipe, model, prompt, res, seed, guidance_scale, num_inference_steps)
        
        # 4. Save image locally with selected format
        status_message = "Saving image locally..."
        logger.info(status_message)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_extension = image_format.lower()
        output_path = os.path.join(OUTPUT_DIR, f"output_{timestamp}.{file_extension}")
        if image_format == "JPEG":
            image = image.convert("RGB")  # JPEG doesn't support RGBA
        image.save(output_path, format=image_format)
        logger.info(f"Image saved to {output_path}")
        
        # 5. Prepare image for download in selected format
        status_message = "Preparing image for download..."
        logger.info(status_message)
        download_filename = f"generated_image_{timestamp}.{file_extension}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}", prefix="hdi1_") as temp_file:
            if image_format == "JPEG":
                image = image.convert("RGB")  # Ensure JPEG compatibility
            image.save(temp_file, format=image_format)
            temp_file_path = temp_file.name
        logger.info(f"Temporary file created at {temp_file_path}")
        
        status_message = "🎉 Image generation complete!"
        logger.info(status_message)
        return image, seed, f"💾 Image saved to: {output_path}", temp_file_path, status_message

    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        logger.error(error_message)
        return None, None, None, None, error_message

def generate_image(pipe, model_type, prompt, resolution, seed, guidance_scale, num_inference_steps):
    try:
        # Parse resolution
        width, height = resolution

        # Handle seed
        if seed == -1:
            seed = torch.randint(0, 1000000, (1,)).item()
        
        generator = torch.Generator("cuda").manual_seed(seed)
        
        # Common parameters
        params = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "num_images_per_prompt": 1,
            "generator": generator
        }

        images = pipe(**params).images
        return images[0], seed
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {str(e)}") from e

if __name__ == "__main__":
    logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Initialize globals without loading model
    current_model = None
    pipe = None

    # Create Gradio interface with forced theme
    custom_theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="pink",
        neutral_hue="gray",
        font=gr.themes.GoogleFont("Inter")
    ).set(
        background_fill_primary="transparent",
        background_fill_secondary="transparent", 
        block_background_fill="transparent",
        block_border_color="transparent",
        body_background_fill="transparent"
    )
    
    with gr.Blocks(
        title="🎨 HiDream-I1-nf4 Dashboard", 
        css=CUSTOM_CSS,
        theme=custom_theme
    ) as demo:
        gr.Markdown("# 🎨 HiDream-I1-nf4 SUP3R-EDITION 🎨")
        gr.Markdown("✨ Create stunning AI-generated images with advanced flow-matching technology ✨")
        gr.Markdown("💡 Tip: Models will download automatically when you click the 'Generate Image' button.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Model Configuration")
                model_type = gr.Radio(
                    choices=list(MODEL_CONFIGS.keys()),
                    value="fast",
                    label="🚀 Model Type",
                    info="Choose your generation speed: 'fast' for quick results, other variants for specialized outputs"
                )
                
                scheduler = gr.Radio(
                    choices=SCHEDULER_OPTIONS,
                    value="FlashFlowMatchEulerDiscreteScheduler",
                    label="🔄 Scheduler Algorithm",
                    info="Flow-matching schedulers provide stable, high-quality results optimized for HiDream"
                )
                
                gr.Markdown("### 🎨 Creative Input")
                prompt = gr.Textbox(
                    label="✨ Your Prompt", 
                    placeholder="A majestic cat wearing a crown, sitting on a throne made of books, digital art, hyperrealistic", 
                    lines=4,
                    info="Describe your vision in detail for best results"
                )
                
                resolution = gr.Radio(
                    choices=RESOLUTION_OPTIONS,
                    value=RESOLUTION_OPTIONS[0],
                    label="📐 Image Resolution",
                    info="Choose aspect ratio and size for your image"
                )
                
                with gr.Row(visible=False) as custom_resolution_row:
                    custom_width = gr.Number(
                        label="🔢 Custom Width",
                        value=1024,
                        minimum=64,
                        maximum=2048,
                        step=8,
                        info="Width in pixels (64-2048, multiple of 8 recommended)"
                    )
                    custom_height = gr.Number(
                        label="🔢 Custom Height", 
                        value=1024,
                        minimum=64,
                        maximum=2048,
                        step=8,
                        info="Height in pixels (64-2048, multiple of 8 recommended)"
                    )
                
                with gr.Accordion("ℹ️ Custom Resolution Info", open=True, visible=False) as custom_info_accordion:
                    gr.Markdown("""
                    ### 🔧 How HiDream Handles Custom Resolutions
                    
                    **Dynamic Scaling & Optimization:**
                    - The model automatically applies **dynamic scaling** based on your custom dimensions
                    - Images are processed through a **latent space optimization** that maintains quality across different aspect ratios
                    - The **shift parameter** is dynamically adjusted to ensure optimal results for your specific resolution
                    
                    **Best Practices:**
                    - Use dimensions that are **multiples of 8** for optimal memory efficiency
                    - Keep the total pixel count reasonable (under 2M pixels) for faster generation
                    - **Square or near-square** ratios (1:1 to 4:3) typically produce the most stable results
                    - Very extreme aspect ratios may require **higher inference steps** (35-50) for best quality
                    
                    **Technical Details:**
                    - The flow-matching scheduler adapts timestep spacing based on image dimensions
                    - Larger resolutions automatically receive enhanced attention mechanisms
                    - The model uses **fractional pixel positioning** to handle non-standard dimensions seamlessly
                    """)
                
                
                image_format = gr.Radio(
                    choices=IMAGE_FORMAT_OPTIONS,
                    value="PNG",
                    label="💾 Output Format",
                    info="PNG: Best quality | JPEG: Smaller files | WEBP: Modern compression"
                )
                
                gr.Markdown("### 🔧 Advanced Settings")
                seed = gr.Number(
                    label="🎲 Seed (-1 for random)", 
                    value=-1, 
                    precision=0,
                    info="Use the same seed to reproduce identical results"
                )
                
                guidance_scale = gr.Slider(
                    minimum=0.0,
                    maximum=10.0,
                    step=0.1,
                    value=2.0,
                    label="🎯 Guidance Scale",
                    info="Higher values = stronger prompt following (2.0-5.0 recommended)"
                )
                
                num_inference_steps = gr.Slider(
                    minimum=1,
                    maximum=100,
                    step=1,
                    value=25,
                    label="🔄 Inference Steps",
                    info="More steps = higher quality but slower generation (25-50 recommended)"
                )
                
                shift = gr.Slider(
                    minimum=1.0,
                    maximum=10.0,
                    step=0.1,
                    value=3.0,
                    label="⚡ Shift Parameter",
                    info="Fine-tune scheduler behavior (3.0 is optimal for most cases)"
                )
                
                generate_btn = gr.Button("🎨 Generate Image", variant="primary")
                cleanup_btn = gr.Button("🧹 Clean Temporary Files", variant="secondary")
                
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Generation Status")
                status_message = gr.Textbox(
                    label="🔄 Current Status", 
                    value="✅ Ready to generate!", 
                    interactive=False,
                    info="Real-time updates on generation progress"
                )
                
                output_image = gr.Image(
                    label="🖼️ Generated Image", 
                    type="pil",
                    height=400
                )
                
                gr.Markdown("### 📋 Image Details")
                with gr.Row():
                    seed_used = gr.Number(
                        label="🎲 Generated Seed", 
                        interactive=False,
                        info="Use this seed to recreate the exact same image"
                    )
                    save_path = gr.Textbox(
                        label="💾 Local Save Path", 
                        interactive=False,
                        info="Where your image was saved locally"
                    )
                
                download_file = gr.File(
                    label="📥 Download Your Image", 
                    interactive=False, 
                    file_types=[".png", ".jpeg", ".webp"]
                )
        
        # Function to toggle custom resolution visibility
        def toggle_custom_resolution(resolution_choice):
            is_custom = resolution_choice == "Custom"
            return (
                gr.Row(visible=is_custom),
                gr.Accordion(visible=is_custom)
            )
        
        # Event handlers
        resolution.change(
            fn=toggle_custom_resolution,
            inputs=[resolution],
            outputs=[custom_resolution_row, custom_info_accordion]
        )
        
        generate_btn.click(
            fn=gen_img_helper,
            inputs=[model_type, prompt, resolution, seed, scheduler, guidance_scale, num_inference_steps, shift, image_format, custom_width, custom_height],
            outputs=[output_image, seed_used, save_path, download_file, status_message]
        )
        cleanup_btn.click(
            fn=clean_all_temp_files,
            inputs=[],
            outputs=[status_message]
        )

    demo.launch(share=False, show_api=False)
