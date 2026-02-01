import subprocess
import sys

required_libraries = ["scipy", "numpy", "matplotlib","pandas","seaborn","pygame","plotly","biosspy"]

for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
