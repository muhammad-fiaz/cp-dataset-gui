# cp-dataset-gui

[![License](https://img.shields.io/github/license/muhammad-fiaz/cp-dataset-gui?style=flat)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Build](https://github.com/muhammad-fiaz/cp-dataset-gui/actions/workflows/python-app.yml/badge.svg)](https://github.com/muhammad-fiaz/cp-dataset-gui/actions)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-blue?logo=python)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Downloads](https://static.pepy.tech/badge/cp-dataset-gui)](https://pepy.tech/project/cp-dataset-gui)
[![Last Commit](https://img.shields.io/github/last-commit/muhammad-fiaz/cp-dataset-gui.svg?style=flat)](https://github.com/muhammad-fiaz/cp-dataset-gui/commits)
[![Issues](https://img.shields.io/github/issues/muhammad-fiaz/cp-dataset-gui.svg)](https://github.com/muhammad-fiaz/cp-dataset-gui/issues)
[![PRs](https://img.shields.io/github/issues-pr/muhammad-fiaz/cp-dataset-gui.svg)](https://github.com/muhammad-fiaz/cp-dataset-gui/pulls)


A collection and GUI for managing, visualizing, and analyzing competitive programming datasets with a user-friendly PyQt6-based interface.

## Features

- **Dataset Management**: Add, update, remove, and organize competitive programming datasets.
- **Visualization**: Visualize problem statistics and dataset distributions.
- **Analysis Tools**: Analyze dataset contents for insights and trends.
- **SQLite Integration**: Works with SQLite databases for flexible data storage.
- **Modern GUI**: Built with PyQt6 for a responsive and cross-platform experience.

## Installation

### Clone the Repository

First, clone the repository from GitHub:
```sh
git clone https://github.com/muhammad-fiaz/cp-dataset-gui.git
cd cp-dataset-gui
```

### Prerequisites

- Python 3.12 or higher
- [pip](https://pip.pypa.io/en/stable/installation/)
- *(Optional but recommended for speed)* [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)

### Install dependencies with pip

```sh
pip install -r requirements.txt
```
Or, if using a PEP 621-compliant build system:

```sh
pip install .
```

### Install dependencies with uv (recommended for speed)

First, install `uv` if you don't have it:
```sh
pip install uv
```
Or use Homebrew (on macOS/Linux):
```sh
brew install uv
```

Then, install dependencies:
```sh
uv pip install -r requirements.txt
```
Or, for editable/development mode:
```sh
uv pip install -e .[dev]
```

## Usage

Run the app from the root directory:

```sh
python main.py
```

## Building Standalone Executables

You can build a standalone executable for your platform (Windows, Linux, or macOS) with one click using the provided build script. The executable will include all required Python dependencies and the `assets` folder (including icons/images).

### Instructions

1. **Ensure your `assets` folder (with all images/icons) and `main.py` are present in the project root.**
2. **Place your app icon at `assets/images/logo.ico` (for Windows) or `assets/images/logo.icns` (for macOS).**
3. **Run the build script for your platform:**

    ```sh
    python build.py
    ```

    - The script will:
        - Clean previous builds
        - Install PyInstaller if not already installed
        - Bundle all dependencies and assets into a single executable
        - Set your application icon (if present)
        - Output the final executable in the `dist/` folder

4. **Note:**  
    - You must run the build on the OS you want to target (Windows for `.exe`, Linux for Linux binary, macOS for `.app`/binary).
    - Cross-compiling is not supported by PyInstaller.

#### Example

For Windows:
```sh
python build.py
```
Your standalone `.exe` will be in the `dist/` folder.

For Linux or macOS:
```sh
python build.py
```
Your platform-specific binary will be in the `dist/` folder.

## Development

### Install development dependencies

With pip:
```sh
pip install .[dev]
```
With uv:
```sh
uv pip install -e .[dev]
```

### Linting

```sh
ruff .
```

### Project Structure

```
cp-dataset-gui/
├── main.py
├── cp_dataset.db
├── assets/
│   └── images/
│       ├── logo.png
│       ├── logo.ico
│       └── logo_rounded.png
├── pyproject.toml
├── requirements.txt
├── build.py
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/muhammad-fiaz/cp-dataset-gui).

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Author

**Muhammad Fiaz**  
[Email Me](mailto:contact@muhammadfiaz.com)