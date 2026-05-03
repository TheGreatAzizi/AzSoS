$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path build\packages | Out-Null
python azsos.py keygen --out-dir keys
python azsos.py pack `
  --content examples/first-aid/content `
  --id first-aid.fa.demo `
  --title "First Aid Demo" `
  --version 0.1.0 `
  --publisher-name "AZSOS Demo Publisher" `
  --key keys/publisher_private.pem `
  --out build/packages/first-aid-demo.azsos
python azsos.py verify build/packages/first-aid-demo.azsos
