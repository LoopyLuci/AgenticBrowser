import os
import sys
import zipfile

out = os.path.normpath(sys.argv[1])
src = os.path.normpath(sys.argv[2]) if len(sys.argv) > 2 else "agenticbrowser"
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for dirpath, _, filenames in os.walk(src):
        for name in filenames:
            path = os.path.join(dirpath, name)
            arcname = os.path.relpath(path, src)
            zf.write(path, arcname)
print("Created zip via python:", out)
