"""Exercise real PhotoCraft PSD editing on isolated geometric sample assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
from photocraft_runner import call, convert, info, resolve_cli, run_document, sha256


def layers(document):
    def walk(nodes):
        for node in nodes:
            yield node
            yield from walk(node.get("children", []))
    return list(walk(document["layers"]))


def named(document, name):
    matches = [node for node in layers(document) if node["name"] == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one layer named {name}, got {len(matches)}")
    return matches[0]


def execute(cli, source, steps, output):
    return run_document(cli, source, [steps], output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    try:
        from PIL import Image, ImageChops
    except ImportError:
        parser.error("Pixel verification needs Pillow; nothing was installed or changed.")
    cli = resolve_cli(args.cli)
    out = Path(args.out_dir).resolve()
    if out.exists():
        parser.error("Use a new QA directory; existing output is not overwritten.")
    out.mkdir(parents=True)
    source = out / "complete-source.png"
    execute(cli, {"width": 96, "height": 160, "background": "transparent"}, [
        ("shape.create", {"kind": "ellipse", "rect": [18, 5, 60, 60], "fill": "#2f6bff", "name": "头部"}),
        ("shape.create", {"kind": "rect", "rect": [12, 55, 72, 85], "fill": "#173f9d", "name": "完整身体"}),
        ("shape.create", {"kind": "rect", "rect": [14, 135, 25, 21], "fill": "#252c35", "name": "脚左"}),
        ("shape.create", {"kind": "rect", "rect": [57, 135, 25, 21], "fill": "#252c35", "name": "脚右"}),
    ], source)
    source_pixels = Image.open(source).convert("RGBA")
    source_hash = sha256(source)
    assert source_pixels.getchannel("A").getextrema() == (0, 255)
    native = out / "sample-native.pcraft"
    execute(cli, {"width": 640, "height": 480, "background": "#ffffff"}, [
        ("shape.create", {"kind": "rect", "rect": [0, 0, 640, 480], "fill": "#eaf0fa", "name": "完整底板"}),
        ("shape.create", {"kind": "ellipse", "rect": [440, 260, 80, 80], "fill": "#d4af37", "name": "独立形状"}),
        ("type.create", {"x": 25, "y": 55, "text": "EDITABLE PSD", "font": "Arial", "size": 26, "color": "#252c35", "name": "英文标题"}),
        ("type.create", {"x": 25, "y": 95, "text": "完整素材分层测试", "font": "Microsoft YaHei", "size": 22, "color": "#252c35", "name": "中文标题"}),
        ("file.placeEmbedded", {"path": str(source), "fit": False, "center": [330, 320]}),
        ("layer.renameLayer", {"name": "完整主体"}),
        ("select.rect", {"x": 260, "y": 260, "width": 120, "height": 120}),
        ("layer.layerMask.revealSelection", {}),
        ("layer.layerMask.linked", {"linked": False}),
        ("select.deselect", {}),
    ], native)
    doc = info(cli, native)
    subject = named(doc, "完整主体")
    en = named(doc, "英文标题")
    cn = named(doc, "中文标题")
    grouped = out / "sample-grouped.pcraft"
    execute(cli, native, [
        ("layer.select", {"layer": en["id"]}),
        ("layer.select", {"layer": cn["id"], "mode": "add"}),
        ("layer.groupLayers", {"name": "可编辑文字组"}),
        ("layerComp.new", {"name": "默认成品"}),
        ("layer.setProps", {"layer": subject["id"], "visible": False}),
        ("layerComp.new", {"name": "主体关闭"}),
        ("layerComp.apply", {"comp": "默认成品"}),
    ], grouped)
    psd = out / "sample.psd"
    preview = out / "native-preview.png"
    reopened_preview = out / "reopened-preview.png"
    convert(cli, grouped, psd)
    convert(cli, grouped, preview)
    convert(cli, psd, reopened_preview)
    reopened = info(cli, psd)
    subject = named(reopened, "完整主体")
    en = named(reopened, "英文标题")
    cn = named(reopened, "中文标题")
    edit = out / "edited-copy.psd"
    execute(cli, psd, [
        ("type.edit", {"layer": en["id"], "text": "EDIT VERIFIED"}),
        ("type.edit", {"layer": cn["id"], "text": "中文编辑通过"}),
    ], edit)
    edited = info(cli, edit)
    exported = out / "embedded-export.png"
    execute(cli, psd, [
        ("layer.select", {"layer": subject["id"]}),
        ("layer.smartObjects.exportContents", {"layer": subject["id"], "path": str(exported)}),
    ], out / "export-proof.pcraft")
    moved = out / "moved-copy.psd"
    execute(cli, psd, [
        ("layer.select", {"layer": subject["id"]}),
        ("edit.transform", {"layer": subject["id"], "matrix": [1, 0, 0, 1, 70, 0], "target": "pixels"}),
    ], moved)
    move_preview = out / "move-preview.png"
    convert(cli, moved, move_preview)
    moved_subject = named(info(cli, moved), "完整主体")
    default_pixels = Image.open(reopened_preview).convert("RGBA")
    difference = ImageChops.difference(default_pixels, Image.open(move_preview).convert("RGBA"))
    changed_bounds = difference.convert("RGB").getbbox()
    comp_result = execute(cli, psd, [("layerComp.list", {})], out / "comp-list-proof.pcraft")
    comp_names = [item["name"] for entry in comp_result["results"]
                  if entry.get("command") == "layerComp.list"
                  for item in entry.get("result", {}).get("comps", [])]
    background_doc = out / "subject-off.pcraft"
    execute(cli, psd, [("layerComp.apply", {"comp": "主体关闭"})], background_doc)
    background_png = out / "background-preview.png"
    convert(cli, background_doc, background_png)
    background_pixels = Image.open(background_png).convert("RGBA")
    with psd.open("rb") as stream:
        magic, version, channels, height, width, depth, mode = struct.unpack(
            ">4sH6xHIIHH", stream.read(26))
    checks = {
        "validPSD": magic == b"8BPS" and version == 1 and (width, height, depth) == (640, 480, 8),
        "nativeTextAndShapeAndSmartObject": {"Type", "Shape"}.issubset({node["kind"] for node in layers(reopened)}) and subject["kind"] in ("Smart Object", "SmartObject", "Smart"),
        "textGroupPreserved": named(reopened, "可编辑文字组")["kind"] == "Group",
        "nativeEnglishAndChineseEditReopen": named(edited, "英文标题").get("text", {}).get("text") == "EDIT VERIFIED" and named(edited, "中文标题").get("text", {}).get("text") == "中文编辑通过" and named(edited, "中文标题")["kind"] == "Type",
        "embeddedFullSourcePixels": source_pixels.size == Image.open(exported).size and source_pixels.tobytes() == Image.open(exported).convert("RGBA").tobytes(),
        "sourceHasRealAlpha": source_pixels.getchannel("A").getextrema() == (0, 255),
        "subjectMoveWithMask": moved_subject["bounds"][0] - subject["bounds"][0] == 70 and moved_subject.get("hasMask", False),
        "fixedExternalMaskAfterPSDReopen": changed_bounds is not None and changed_bounds[0] >= 260 and changed_bounds[1] >= 260 and changed_bounds[2] <= 380 and changed_bounds[3] <= 380,
        "defaultPreviewPixelsEqualAfterPSDReopen": default_pixels.tobytes() == Image.open(preview).convert("RGBA").tobytes(),
        "layerCompsPreserved": set(comp_names) == {"默认成品", "主体关闭"},
        "completeBackgroundInSubjectArea": len(background_pixels.crop((260, 260, 380, 380)).getcolors(14400) or []) == 1,
        "sourceFileUnchanged": sha256(source) == source_hash,
    }
    report = {"application": "PhotoCraft", "version": call(cli, ["--version"]).strip(),
              "checks": checks, "changedBounds": changed_bounds, "sourceSize": source_pixels.size,
              "photoshopNativeValidation": "not_run", "scope": "Geometric structural sample; no reference-image fidelity claim.",
              "overallPass": all(checks.values()), "psdSHA256": sha256(psd)}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overallPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
