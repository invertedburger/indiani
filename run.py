"""Entry point — builds the static site into results/.

    python run.py

Then open results/index.html, or use serve.bat to build + serve on :8000.
"""
from indiani.builder import build

if __name__ == '__main__':
    build()
