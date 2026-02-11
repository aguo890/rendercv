<div align="center">

# RenderCV — Personal Fork

_A Dockerized, live-preview CV editor built on top of [RenderCV](https://github.com/rendercv/rendercv)_

[![Upstream RenderCV](https://img.shields.io/badge/upstream-rendercv%2Frendercv-blue)](https://github.com/rendercv/rendercv)

</div>

## About

This is a personal fork of the excellent [**RenderCV**](https://github.com/rendercv/rendercv) project by [@sinaatalay](https://github.com/sinaatalay).

RenderCV lets you write your CV/resume as a YAML file and renders it into a beautifully typeset PDF — no LaTeX or design skills required. This fork extends it with a **Streamlit-based web editor**, a **Dockerized development environment**, and several quality-of-life features for rapid iteration on tailored resumes.

> [!NOTE]
> All credit for the core RenderCV engine, themes, and CLI goes to the [upstream project](https://github.com/rendercv/rendercv). Please see their [documentation](https://docs.rendercv.com) for full details on YAML schema, themes, and design options.

---

## Features Added in This Fork

### 🖥️ Streamlit Web Editor (`app.py`)
A browser-based, two-panel CV editor with:
- **Live Preview** — Press `Ctrl+Enter` to render your CV and instantly see the result as page-by-page PNG previews alongside the YAML editor.
- **One-Click PDF Download** — A floating download button appears on hover over the preview panel.
- **YAML File Upload** — Upload any RenderCV-compatible YAML directly into the editor.
- **Reset to Disk** — Instantly revert the editor to the original file on disk.
- **Error Feedback** — Build failures surface full `stdout`/`stderr` logs in an expandable panel.

### 🐳 Dockerized Development Environment
- **`Dockerfile.dev`** — Based on `uv` + Python 3.12, with all dependencies pre-installed and cached for fast rebuilds.
- **`docker-compose.yml`** — One-command orchestration, volume-mounting the project directory for live code changes.
- No need to install Python, `uv`, or any dependencies locally.

### ⚡ Makefile Shortcuts
| Command | Description |
|---|---|
| `make app` | Start the Streamlit editor at [localhost:8502](http://localhost:8502) |
| `make reload` | Rebuild and restart the container (picks up code changes) |
| `make logs` | Tail Docker container logs |
| `make stop` | Stop the running container |
| `make install` | Install dependencies locally via `uv` |
| `make test` | Run the test suite |
| `make format` | Format code with `ruff` |

### 📝 Custom Output Filenames via YAML
Set the output PDF/PNG filename directly in the YAML — useful for tracking which resume version targets which job:

```yaml
settings:
  render_command:
    pdf_path: "rendercv_output/Aaron_Guo_CV_Google_SWE_Feb_2026.pdf"
    png_path: "rendercv_output/Aaron_Guo_CV_Google_SWE_Feb_2026.png"
```

Available placeholders: `NAME_IN_SNAKE_CASE`, `MONTH_ABBREVIATION`, `YEAR`, and [more](https://github.com/rendercv/rendercv).

The download button in the Streamlit editor automatically uses this custom filename.

---

## Quick Start

**Prerequisites:** [Docker](https://www.docker.com/products/docker-desktop/) and `make`.

```bash
# 1. Clone this repository
git clone https://github.com/aguo890/rendercv.git
cd rendercv

# 2. Start the editor
make app

# 3. Open in your browser
#    → http://localhost:8502
```

Edit the YAML in the left panel, press **Ctrl+Enter**, and the rendered CV appears on the right. Click the floating **⬇️ Download PDF** button to save.

To pick up code changes after editing `app.py` or other files:
```bash
make reload
```

---

## Upstream RenderCV

This fork is built on top of [**RenderCV v2.5+**](https://github.com/rendercv/rendercv) which provides:

- ✅ YAML-to-PDF rendering with professional typography
- ✅ Multiple built-in themes (Classic, Sb2nov, ModernCV, Engineeringresumes, etc.)
- ✅ JSON Schema with autocompletion and inline validation
- ✅ Extensive design customization (margins, fonts, colors, spacing)
- ✅ Multi-language/locale support
- ✅ Strict input validation with clear error messages

For the full upstream documentation, visit [docs.rendercv.com](https://docs.rendercv.com).

---

## License

This fork inherits the license from the upstream [RenderCV](https://github.com/rendercv/rendercv) project. See [LICENSE](LICENSE) for details.
