# Manim MCP Server

An MCP (Model Context Protocol) server that enables AI assistants to create mathematical animations using Manim.

## Overview

This server exposes Manim's animation capabilities through MCP tools, allowing AI assistants to programmatically create, preview, and render mathematical animations and visualizations.

![Demo](gif.gif)

## Features

- **Project Management**: Create and manage video projects with configurable quality settings
- **Segment-Based Workflow**: Build animations incrementally using code segments
- **Preview Generation**: Generate static preview images before final rendering
- **Video Rendering**: Render final videos in multiple quality levels

## Installation

Requires Python 3.12+

```bash
# Clone the repository
git clone <repository-url>
cd manim_mcp_server

# Install dependencies with uv
uv sync
```

### Prerequisites

- [Manim](https://www.manim.community/) and its system dependencies (LaTeX, FFmpeg, etc.)
- Python 3.12 or higher

## Usage

### Running the Server

```bash
# Run the MCP server
uv run python -m manim_mcp_server.server
```

Or add to your MCP client configuration.

### Available Tools

#### `create_project`
Initialize a new video project.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Project name |
| `quality` | string | `"medium_quality"` | Video quality: `low_quality`, `medium_quality`, `high_quality`, `fourk_quality` |
| `background_color` | string | `None` | Background color for the video |

#### `add_segment`
Add a code segment to the project.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_id` | string | required | Project ID from `create_project` |
| `manim_code` | string | required | Raw Manim code |
| `description` | string | `""` | Description of what this segment does |
| `code_type` | string | `"construct"` | `"construct"` for code inside `construct()` method, `"preamble"` for imports/helper classes |

#### `edit_segment`
Edit an existing segment's code.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_id` | string | required | Project ID |
| `segment_id` | string | required | Segment ID to edit |
| `manim_code` | string | required | New Manim code |
| `description` | string | `None` | Optional new description |

#### `preview`
Generate a preview image of the current state.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_id` | string | required | Project ID |
| `segment_id` | string | `None` | Optional - preview only this segment |

#### `render`
Render the final video.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_id` | string | required | Project ID |

### Quality Settings

| Quality | Resolution | FPS |
|---------|------------|-----|
| `low_quality` | 480p | 15 |
| `medium_quality` | 720p | 30 |
| `high_quality` | 1080p | 60 |
| `fourk_quality` | 2160p | 60 |

## Project Structure

```
manim_mcp_server/
├── src/manim_mcp_server/
│   ├── __init__.py
│   ├── config.py      # Settings and configuration
│   ├── models.py      # Data models (Project, Segment)
│   └── server.py      # MCP server and tools
├── code/              # Generated Python scene files
├── output/            # Rendered output directory
├── videos/            # Rendered video files
├── images/            # Preview images
└── pyproject.toml
```

## Example Workflow

1. Create a project:
   ```
   create_project(name="my_animation", quality="high_quality")
   ```

2. Add preamble code (if needed):
   ```
   add_segment(project_id="proj_xxx", manim_code="class MyShape(VMobject): ...", code_type="preamble")
   ```

3. Add construct code:
   ```
   add_segment(project_id="proj_xxx", manim_code="circle = Circle()\nself.play(Create(circle))")
   ```

4. Preview the animation:
   ```
   preview(project_id="proj_xxx")
   ```

5. Render the final video:
   ```
   render(project_id="proj_xxx")
   ```

## Configuration

Settings are managed via `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `output_dir` | Project root | Directory for Manim output |
| `code_dir` | `./code` | Directory for generated scene files |
| `timeout` | 300 seconds | Render timeout (10-3600 seconds) |

## Dependencies

- `manim>=0.19.1` - Mathematical animation engine
- `mcp>=1.25.0` - Model Context Protocol SDK
- `pydantic>=2.12.5` - Data validation
- `pydantic-settings>=2.12.0` - Settings management
- `aiofiles>=25.1.0` - Async file operations
- `structlog>=25.5.0` - Structured logging

## License

[Add license information]
