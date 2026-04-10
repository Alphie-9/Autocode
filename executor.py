import subprocess
import base64
import os
import tempfile
import uuid
import sys


def execute_python_code(code: str, timeout: int = 60) -> dict:
    """
    Executes Python code in a subprocess with timeout.
    Returns stdout, stderr, and any generated plot as base64.
    """
    plot_path = f"/tmp/plot_{uuid.uuid4().hex}.png"

    wrapped_code = f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

_PLOT_PATH = "{plot_path}"

_orig_savefig = plt.savefig
def _auto_save(*args, **kwargs):
    _orig_savefig(_PLOT_PATH, bbox_inches='tight', dpi=150)
plt.savefig = _auto_save

{code}

import matplotlib.pyplot as _plt
if _plt.get_fignums():
    _orig_savefig("{plot_path}", bbox_inches='tight', dpi=150)
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(wrapped_code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "MPLBACKEND": "Agg"}
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        plot_b64 = None
        if os.path.exists(plot_path):
            with open(plot_path, "rb") as img_file:
                plot_b64 = base64.b64encode(img_file.read()).decode("utf-8")
            os.remove(plot_path)

        return {
            "stdout": stdout,
            "stderr": stderr,
            "plot": plot_b64,
            "success": result.returncode == 0
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out after 30 seconds.",
            "plot": None,
            "success": False
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
