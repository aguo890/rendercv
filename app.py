import shutil
import subprocess
from pathlib import Path

import streamlit as st
import yaml as pyyaml

# --- Constants & Paths ---
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CV_FILE = BASE_DIR / "Aaron_Guo_CV.yaml"
GENERIC_TEMPLATE = BASE_DIR / "template.yaml"
TEMP_YAML_FILE = BASE_DIR / "temp_cv.yaml"
OUTPUT_DIR = BASE_DIR / "rendercv_output"

# --- Helper Functions ---
def load_initial_data():
    """Loads the default CV YAML into session state if not already present."""
    if "cv_content" not in st.session_state:
        # Check for Aaron's CV first, then fallback to generic
        target_file = DEFAULT_CV_FILE if DEFAULT_CV_FILE.exists() else GENERIC_TEMPLATE
        
        if target_file.exists():
            with open(target_file, encoding="utf-8") as f:
                content = f.read()
                st.session_state["cv_content"] = content
                st.session_state["original_content"] = content
        else:
            st.session_state["cv_content"] = "# Default CV file not found.\n# Paste your RenderCV YAML here."
            st.session_state["original_content"] = st.session_state["cv_content"]

def find_latest_pdf(directory):
    """Finds the most recently modified PDF in the output directory."""
    directory = Path(directory)
    if not directory.exists():
        return None
        
    pdf_files = list(directory.rglob("*.pdf"))
    if not pdf_files:
        return None
        
    return max(pdf_files, key=lambda p: p.stat().st_ctime)

def run_render_cv():
    """Saves the temp file and runs the rendercv command."""
    # 1. Save the current state to a temp file
    with open(TEMP_YAML_FILE, "w", encoding="utf-8") as f:
        f.write(st.session_state["cv_content"])
    
    # Update original_content on successful build if we want to treat build as "save"
    # Actually, let's keep it separate for now.
    
    # 2. Clean output directory to prevent stale files
    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)
        except Exception as e:
            return f"Error cleaning output directory: {e}. Please ensure no PDFs/Images are open."

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 3. Run the command
    cmd = ["rendercv", "render", str(TEMP_YAML_FILE)]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result
    except Exception as e:
        return f"System Error: {e!s}"

def reset_to_original():
    """Resets the editor content to the file on disk."""
    if DEFAULT_CV_FILE.exists():
        with open(DEFAULT_CV_FILE, encoding="utf-8") as f:
            content = f.read()
            st.session_state["cv_content"] = content
            st.session_state["original_content"] = content
        st.toast("Reset to original file!", icon="🔄")
    else:
        st.error(f"Original file {DEFAULT_CV_FILE.name} not found!")

# --- Callbacks ---
def handle_template_change():
    """Logic to handle template switching with data loss prevention."""
    new_choice = st.session_state.get("template_selection")
    # If content is modified, don't overwrite immediately
    has_changes = st.session_state.get("cv_content") != st.session_state.get("original_content")
    
    if has_changes:
        st.session_state["pending_template_load"] = new_choice
        st.session_state["show_overwrite_warning"] = True
    else:
        # Safe to load
        load_template_by_name(new_choice)

def load_template_by_name(name):
    """Actual loading of template data."""
    target = DEFAULT_CV_FILE if name == "My CV" else GENERIC_TEMPLATE
    if target.exists():
        with open(target, encoding="utf-8") as f:
            content = f.read()
            st.session_state["cv_content"] = content
            st.session_state["original_content"] = content
        st.toast(f"Loaded {name}!", icon="📥")
    else:
        st.error(f"Template {target.name} not found.")

def confirm_overwrite():
    """Confirmed overwrite by user."""
    load_template_by_name(st.session_state["pending_template_load"])
    st.session_state["show_overwrite_warning"] = False
    st.session_state["pending_template_load"] = None

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
        st.caption("v2.7 | Enhanced Editor")
        st.divider()

        # Template Selection
        st.subheader("Templates")
        st.selectbox(
            "Select Starting Template",
            options=["My CV", "Generic Template"],
            key="template_selection",
            on_change=handle_template_change
        )
        
        # Overwrite Warning Dialog (Simulation)
        if st.session_state.get("show_overwrite_warning"):
            st.warning("⚠️ Unsaved changes detected! Switching will overwrite your current work.")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("Confirm Overwrite", type="primary"):
                    confirm_overwrite()
                    st.rerun()
            with col_c2:
                if st.button("Cancel"):
                    st.session_state["show_overwrite_warning"] = False
                    st.rerun()

        st.divider()
        st.subheader("Actions")
        
        col_gen, col_reset = st.columns([1, 1])
        with col_gen:
            if st.button("🚀 Build PDF", type="primary", use_container_width=True):
                trigger_render()
        
        with col_reset:
             if st.button("🔄 Reset", use_container_width=True):
                 reset_to_original()
                 st.rerun()

        # Sidebar Download
        pdf_path = find_latest_pdf(OUTPUT_DIR)
        if pdf_path:
            st.divider()
            st.subheader("Export")
            
            # Dynamic Filename Logic
            download_fn = pdf_path.name
            try:
                parsed = pyyaml.safe_load(st.session_state["cv_content"])
                if parsed and 'cv' in parsed and 'name' in parsed['cv']:
                    name_slug = parsed['cv']['name'].replace(" ", "_").lower()
                    download_fn = f"{name_slug}_cv.pdf"
            except:
                pass

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name=download_fn,
                    mime="application/pdf",
                    use_container_width=True
                )

        st.divider()
        st.markdown("[Documentation](https://docs.rendercv.com) • [GitHub](https://github.com/rendercv/rendercv)")

    # --- Main Area ---
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.text_area(
            "Editor",
            key="cv_content",
            height=None,
            label_visibility="collapsed",
            on_change=trigger_render
        )
        
        if st.session_state.get("build_success") is False:
            with st.expander("❌ Failure Logs", expanded=True):
                st.code(st.session_state.get("build_error", "Unknown Error"), language="text")

    with col2:
        pdf_path = find_latest_pdf(OUTPUT_DIR)
        
        if pdf_path:
            # Use Iframe for PDF Preview for high-fidelity/scrolling
            import base64
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
             st.info("👈 Press **Ctrl+Enter** in the editor to build your CV.")

if __name__ == "__main__":
    main()
