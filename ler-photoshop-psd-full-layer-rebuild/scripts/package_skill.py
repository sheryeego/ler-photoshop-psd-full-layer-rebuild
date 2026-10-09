"""Create and verify a portable backup of one skill using only Python stdlib."""
import argparse
import hashlib
import json
import os
import re
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

def collect(root):
    paths = []
    def walk_error(error):
        raise error
    for parent, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        # Inspect directories before os.walk can descend into a junction.
        for name in sorted(dirs + names):
            path = Path(parent) / name
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError(f"Links are not included in skill backups: {path}")
            if getattr(path.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024):
                raise ValueError(f"Reparse points are not included: {path}")
            if path.is_file() and path.suffix not in (".pyc", ".pyo"):
                paths.append(path)
        dirs[:] = [name for name in dirs if name not in (".git", "__pycache__")]
    return sorted(paths)

def package(skill_dir, output_dir):
    # Test the provided root before resolving, so a linked root cannot be hidden.
    supplied = Path(skill_dir).absolute()
    if supplied.is_symlink() or (hasattr(supplied, "is_junction") and supplied.is_junction()):
        raise ValueError("The skill root must not be a symlink or junction.")
    root = supplied.resolve(strict=True)
    content = (root / "SKILL.md").read_text(encoding="utf-8")
    name_match = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", content)
    version_match = re.search(r"(?m)^  version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", content)
    if not name_match or not version_match:
        raise ValueError("Expected a skill name and semantic metadata version.")
    name, version = name_match.group(1), version_match.group(1)
    if name != root.name:
        raise ValueError("The skill folder name must match its name.")
    out = Path(output_dir).resolve()
    if out == root or root in out.parents:
        raise ValueError("The backup directory must be outside the skill directory.")
    files = collect(root)
    snapshots = [(p.relative_to(root).as_posix(), p.read_bytes()) for p in files]
    manifest = {
        "schemaVersion": 1, "skillName": name, "version": version,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "files": [{"path": rel, "bytes": len(data), "sha256": digest(data)} for rel, data in snapshots],
    }
    restore = (
        "Skill backup / 技能备份\n"
        "1. Verify this ZIP against the adjacent SHA256 file.\n"
        "2. Extract into a fresh directory and verify every skill file against manifest.json.\n"
        "3. After installation-location approval, copy the complete named skill folder.\n"
        "4. Back up an existing installation first; do not merge different versions.\n"
        "创建备份不代表已安装。恢复前先核对哈希，解压到新目录；确认安装位置后复制完整 skill 文件夹。\n"
    ).encode("utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{name}-v{version}-{stamp}.zip"
    expected = {f"{name}/{rel}": data for rel, data in snapshots}
    expected["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    expected["RESTORE.txt"] = restore
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for entry, data in expected.items():
            z.writestr(entry, data)
    with zipfile.ZipFile(archive, "r") as z:
        names = z.namelist()
        if len(names) != len(expected) or len(set(names)) != len(names) or set(names) != set(expected):
            raise ValueError("Archive entry set mismatch.")
        if z.testzip() is not None:
            raise ValueError("ZIP CRC validation failed.")
        for entry, data in expected.items():
            if digest(z.read(entry)) != digest(data):
                raise ValueError(f"Archive content mismatch: {entry}")
    zip_hash = digest(archive.read_bytes())
    hash_path = archive.with_suffix(".zip.sha256")
    with hash_path.open("x", encoding="utf-8") as f:
        f.write(f"{zip_hash}  {archive.name}\n")
    report = {
        "archive": str(archive), "sha256": zip_hash, "skillFileCount": len(snapshots),
        "entryCount": len(expected), "entrySetsMatch": True, "contentHashesMatch": True,
        "crcPass": True, "actualExtractionVerified": False,
        "verificationScope": "ZIP reread and every archived byte compared with in-memory source snapshots",
        "installed": False,
    }
    with archive.with_suffix(".verification.json").open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.skill_dir, args.output_dir), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
