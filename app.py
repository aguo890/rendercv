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
    target = DEFAULT_CV_FILE if name == "Aaron's CV (Master)" else GENERIC_TEMPLATE
    if target.exists():
        with open(target, encoding="utf-8") as f:
            content = f.read()
            st.session_state["cv_content"] = content
            st.session_state["original_content"] = content
            st.session_state["show_overwrite_warning"] = False
    else:
        st.error(f"Template {name} not found!")

def trigger_render():
    """Callback to trigger the build process."""
    result = run_render_cv()
    if isinstance(result, str): # Error message
        st.session_state["build_success"] = False
        st.session_state["build_error"] = result
    else:
        st.session_state["build_success"] = result.returncode == 0
        if result.returncode != 0:
            st.session_state["build_error"] = result.stderr
        else:
            st.session_state["build_error"] = ""
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

    # Initialize state
    if "focus_mode" not in st.session_state:
        st.session_state["focus_mode"] = False
    if "ai_loading" not in st.session_state:
        st.session_state["ai_loading"] = False
    if "ai_insights" not in st.session_state:
        st.session_state["ai_insights"] = None

    # Custom CSS for Focus Mode and Styling
    st.markdown(f"""
        <style>
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }}
        .stTextArea textarea {{
            font-family: 'Source Code Pro', monospace;
            border-radius: 8px;
            height: 80vh !important;
        }}
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: #f8f9fa;
        }}
        </style>
    """, unsafe_allow_html=True)

    load_initial_data()

    # --- Sidebar Controls ---
    with st.sidebar:
        st.title("📄 RenderCV")
        st.caption("v2.8 | AI-Enhanced Suite")
        st.divider()

        # 1. Trigger Info
        st.info("💡 **Build PDF**: Click the button below or press **Ctrl+Enter** in the editor.")

        # 2. AI Prompt Guide
        with st.expander("🤖 AI Ghostwriter (JD Tailoring)", expanded=st.session_state.get("ai_insights") is None):
            tailor_title = st.text_input("Job Title", placeholder="e.g. Senior Software Engineer", key="jd_title", disabled=st.session_state.ai_loading)
            tailor_company = st.text_input("Company", placeholder="e.g. Google", key="jd_company", disabled=st.session_state.ai_loading)
            tailor_jd = st.text_area("Job Description", height=200, placeholder="Paste JD here...", key="jd_text", disabled=st.session_state.ai_loading)
            
            if st.button("✨ Tailor with AI", type="primary", use_container_width=True, disabled=st.session_state.ai_loading):
                if not tailor_jd or not tailor_title:
                    st.error("Please provide a Job Title and Description.")
                else:
                    st.session_state.ai_loading = True
                    st.rerun()

        st.divider()

        # 3. Control Group
        st.subheader("Actions")
        
        # Build Button
        if st.button("🚀 Build PDF", type="primary", use_container_width=True, disabled=st.session_state.ai_loading):
            trigger_render()
            
        col_draft, col_reset = st.columns(2)
        with col_draft:
            if st.button("💾 Save Draft", use_container_width=True, help="Save to tailored_draft.yaml"):
                try:
                    with open(BASE_DIR / "tailored_draft.yaml", "w", encoding="utf-8") as f:
                        f.write(st.session_state["cv_content"])
                    st.toast("Draft Saved!", icon="✅")
                except Exception as e:
                    st.error(f"Save failed: {e}")

        with col_reset:
             if st.button("🔄 Reset", use_container_width=True):
                 reset_to_original()
                 st.rerun()

        # Download Section
        pdf_path = find_latest_pdf(OUTPUT_DIR)
        if pdf_path:
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

        # 4. View Mode
        st.divider()
        st.subheader("View")
        focus_label = "📖 Focus Mode: ON" if st.session_state.focus_mode else "🖥️ Focus Mode: OFF"
        if st.button(focus_label, use_container_width=True):
            st.session_state.focus_mode = not st.session_state.focus_mode
            st.rerun()

        # 5. Templates
        with st.expander("📂 Switch Base Template"):
            st.selectbox(
                "Select starting structure",
                options=["My CV", "Generic Template"],
                key="template_selection",
                on_change=handle_template_change
            )

        st.divider()
        st.markdown("[Documentation](https://docs.rendercv.com) • [GitHub](https://github.com/rendercv/rendercv)")

    # --- Handling AI Loading State ---
    if st.session_state.ai_loading:
        with st.spinner("🤖 Ghostwriter is optimizing your CV..."):
            try:
                from ai_tailor import generate_tailored_resume
                brief, tailored_yaml, gaps, reasoning = generate_tailored_resume(
                    st.session_state["cv_content"],
                    st.session_state["jd_text"],
                    st.session_state["jd_title"],
                    st.session_state["jd_company"]
                )
                st.session_state["cv_content"] = tailored_yaml
                st.session_state["original_content"] = tailored_yaml
                st.session_state["ai_insights"] = {
                    "brief": brief,
                    "gaps": gaps,
                    "reasoning": reasoning
                }
                st.toast("CV Tailored Successfully!", icon="🚀")
            except Exception as e:
                st.error(f"AI Tailoring failed: {e}")
            finally:
                st.session_state.ai_loading = False
                st.rerun()

    load_initial_data()

    # Dynamic Column Layout
    if st.session_state.focus_mode:
        # Full Preview Mode
        preview_col = st.container()
        with preview_col:
            pdf_path = find_latest_pdf(OUTPUT_DIR)
            if pdf_path:
                import base64
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                 st.info("👈 Press **Ctrl+Enter** in the editor to build your CV.")
    else:
        # Split Mode
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            st.text_area(
                "Editor",
                key="cv_content",
                height=None,
                label_visibility="collapsed",
                on_change=trigger_render,
                disabled=st.session_state.ai_loading
            )
            
            if st.session_state.get("build_success") is False:
                with st.expander("❌ Failure Logs", expanded=True):
                    st.code(st.session_state.get("build_error", "Unknown Error"), language="text")

        with col2:
            pdf_path = find_latest_pdf(OUTPUT_DIR)
            if pdf_path:
                import base64
                with open(pdf_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                 st.info("👈 Press **Ctrl+Enter** in the editor to build your CV.")

if __name__ == "__main__":
    main()
