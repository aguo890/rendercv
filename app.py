import streamlit as st
import subprocess
import os
import glob
import shutil
import yaml as pyyaml

# --- Constants ---
DEFAULT_CV_FILE = "Aaron_Guo_CV.yaml"
TEMP_YAML_FILE = "temp_cv.yaml"
OUTPUT_DIR = "rendercv_output"

# --- Helper Functions ---
def load_initial_data():
    """Loads the default CV YAML into session state if not already present."""
    if "cv_content" not in st.session_state:
        if os.path.exists(DEFAULT_CV_FILE):
            with open(DEFAULT_CV_FILE, "r", encoding="utf-8") as f:
                st.session_state["cv_content"] = f.read()
        else:
            st.session_state["cv_content"] = "# Default CV file not found.\n# Paste your RenderCV YAML here."

def find_latest_pdf(directory):
    """Finds the most recently modified PDF in the output directory."""
    # RenderCV output structure can vary, so we search recursively if needed
    # For now, we stick to the plan's flat search in the output folder
    search_pattern = os.path.join(directory, '*.pdf')
    list_of_files = glob.glob(search_pattern)
    
    if not list_of_files:
        # Fallback: RenderCV might put it in a subdirectory named after the person
        # Let's try a recursive search if the flat search fails
        search_pattern_recursive = os.path.join(directory, '**', '*.pdf')
        list_of_files = glob.glob(search_pattern_recursive, recursive=True)
    
    if not list_of_files:
        return None
        
    return max(list_of_files, key=os.path.getctime)

def run_render_cv():
    """Saves the temp file and runs the rendercv command."""
    # 1. Save the current state to a temp file
    with open(TEMP_YAML_FILE, "w", encoding="utf-8") as f:
        f.write(st.session_state["cv_content"])
    
    # 2. Clean output directory to prevent stale files
    if os.path.exists(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
        except Exception as e:
            # If we can't delete (e.g. file open), we return an error to notify user
            return f"Error cleaning output directory: {e}. Please ensure no PDFs/Images are open."

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 3. Run the command
    # We explicitly verify the output directory exists or let rendercv create it
    cmd = ["rendercv", "render", TEMP_YAML_FILE]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False # We handle the return code manually
        )
        return result
    except Exception as e:
        return f"System Error: {str(e)}"

def reset_to_original():
    """Resets the editor content to the file on disk."""
    if os.path.exists(DEFAULT_CV_FILE):
        with open(DEFAULT_CV_FILE, "r", encoding="utf-8") as f:
            st.session_state["cv_content"] = f.read()
        st.toast("Reset to original file!", icon="🔄")
    else:
        st.error(f"Original file {DEFAULT_CV_FILE} not found!")

# --- Helper Wrapper for Callback ---
def trigger_render():
    """Callback to run render on text area change."""
    with st.spinner("Auto-rendering..."):
        result = run_render_cv()
        if isinstance(result, subprocess.CompletedProcess) and result.returncode == 0:
            st.toast("Auto-build Successful!", icon="✅")
            st.session_state["build_success"] = True
        else:
            st.toast("Auto-build Failed!", icon="❌")
            st.session_state["build_success"] = False
            if isinstance(result, subprocess.CompletedProcess):
                # Combine stdout and stderr to capture all failure details
                st.session_state["build_error"] = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            else:
                st.session_state["build_error"] = str(result)

# --- Main App ---
def main():
    st.set_page_config(page_title="RenderCV Editor", page_icon="📄", layout="wide")

    # Custom CSS for sleek look and floating button
    st.markdown("""
        <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        .stButton button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
        }
        /* Make the text area fill the screen height */
        .stTextArea textarea {
            font-family: 'Source Code Pro', monospace;
            border-radius: 8px;
            height: 85vh !important; /* Force height to 85% of viewport */
        }
        /* Floating Download Button - Absolute Position in Column */
        div[data-testid="column"]:nth-of-type(2) .stDownloadButton {
            position: absolute !important;
            top: 10px;
            right: 20px;
            z-index: 99999;
            width: auto !important;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }
        div[data-testid="column"]:nth-of-type(2):hover .stDownloadButton {
            opacity: 1;
        }
        div[data-testid="column"]:nth-of-type(2) .stDownloadButton button {
            width: auto !important;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
            background-color: white !important; /* Ensure visibility over images */
            color: black !important;
            border: 1px solid #ddd !important;
        }
        
        /* Hide scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888; 
            border-radius: 4px;
        }
        
        /* Fixed Bottom-Right Download Link */
        .fixed-download {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            background-color: #ff4b4b;
            color: white !important;
            padding: 10px 20px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .fixed-download:hover {
            transform: translateY(-2px);
            box-shadow: 0px 6px 12px rgba(0,0,0,0.3);
            text-decoration: none;
        }
        </style>
    """, unsafe_allow_html=True)

    load_initial_data()

    # --- Sidebar Controls ---
    with st.sidebar:
        st.title("📄 RenderCV")
        st.caption("v2.6 | Streamlit Editor")
        st.divider()

        st.subheader("Actions")
        
        # Generator Button
        col_gen, col_reset = st.columns([1, 1])
        with col_gen:
            if st.button("🚀 Generate PDF", type="primary", use_container_width=True):
                trigger_render()
        
        with col_reset:
             if st.button("🔄 Reset", use_container_width=True):
                 reset_to_original()
                 st.rerun()

        st.divider()
        st.subheader("Data")
        
        # File Uploader
        uploaded_file = st.file_uploader("Upload YAML", type=["yaml", "yml"])
        if uploaded_file is not None:
            string_data = uploaded_file.getvalue().decode("utf-8")
            st.session_state["cv_content"] = string_data
            st.toast("File uploaded successfully!", icon="📂")

        st.divider()
        st.markdown("[Documentation](https://docs.rendercv.com) • [GitHub](https://github.com/rendercv/rendercv)")

    # --- Main Area ---
    # Use container to control width? Streamlit 'wide' layout is usually good.
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.text_area(
            "Editor",
            key="cv_content",
            height=None, # Height is controlled by CSS
            label_visibility="collapsed",
            on_change=trigger_render # Triggers when user presses Ctrl+Enter
        )
        
        # Show Error Logs if failed
        if st.session_state.get("build_success") is False:
            with st.expander("❌ Failure Logs", expanded=True):
                st.code(st.session_state.get("build_error", "Unknown Error"), language="text")

    with col2:
        # Check for PDF to show download button
        pdf_path = find_latest_pdf(OUTPUT_DIR)
        
        # Find and Display PNGs
        png_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.png")))
        
        if png_files:
            # Scrollable container for preview
            with st.container(height=850, border=True):
                for i, png_file in enumerate(png_files):
                    st.image(png_file, caption=f"Page {i+1}", use_container_width=True, output_format="PNG")
        else:
            if not pdf_path:
                 st.info("👈 Press **Ctrl+Enter** in the editor to build your CV.")

    # --- Fixed Download Link ---
    if pdf_path:
        import base64
        # Derive download filename from YAML settings if available
        download_name = os.path.basename(pdf_path)
        try:
            parsed = pyyaml.safe_load(st.session_state.get("cv_content", ""))
            if parsed and isinstance(parsed, dict):
                custom_path = (parsed
                    .get("settings", {})
                    .get("render_command", {})
                    .get("pdf_path", ""))
                if custom_path:
                    download_name = os.path.basename(custom_path)
        except Exception:
            pass
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{download_name}" class="fixed-download">⬇️ Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
