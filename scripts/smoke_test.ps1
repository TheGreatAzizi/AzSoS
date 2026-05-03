$ErrorActionPreference = "Stop"
python azsos.py --version
python azsos.py verify sample-packages/first-aid-demo.azsos
pytest
