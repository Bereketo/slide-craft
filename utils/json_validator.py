"""
validate_fix_json.py
- Validate a deck JSON against Draft-07 schema
- Lint & auto-fix common issues that cause overlap/misalignment before rendering
- Return (clean_json, warnings)

Usage:
    fixed, warnings = validate_and_fix(deck_json, schema_json)
"""

from copy import deepcopy
from typing import Any, Dict, List, Tuple
import re

from jsonschema import Draft7Validator

# ---------- Tunables (enterprise-safe defaults) ----------

MIN_GUTTER_PX = 12
MIN_MARGIN_PX = 16

# Minimum recommended heights (px) by text type
MIN_ROW_H = {
    "title": 120,
    "h2": 90,
    "body": 72,
    "caption": 40
}
FALLBACK_MIN_ROW_H = 60

# Heuristic line height estimate (px) from font size
def est_block_height_px(text_type: str, font_size: float | None, lines: int = 2) -> int:
    if font_size:
        return int(max(font_size * 1.5 * lines, MIN_ROW_H.get(text_type, FALLBACK_MIN_ROW_H)))
    return MIN_ROW_H.get(text_type, FALLBACK_MIN_ROW_H)

COLOR_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# ---------- Helpers ----------

def _warn(warnings: List[str], where: str, msg: str):
    warnings.append(f"[{where}] {msg}")

def _get(obj: Dict, path: List[str], default=None):
    cur = obj
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _set_if_missing(obj: Dict, path: List[str], value):
    cur = obj
    for k in path[:-1]:
        cur = cur.setdefault(k, {})
    cur.setdefault(path[-1], value)

def _px_to_px(v):  # placeholder if you add inches later
    return v

def _normalize_tokens(deck: Dict[str, Any], warnings: List[str]):
    # Ensure spacing & grid basics exist
    _set_if_missing(deck, ["tokens", "spacing", "gutter"], MIN_GUTTER_PX)
    _set_if_missing(deck, ["tokens", "spacing", "margin"], MIN_MARGIN_PX)
    _set_if_missing(deck, ["tokens", "grid", "columns"], 12)
    _set_if_missing(deck, ["tokens", "grid", "unit"], "px")
    # Ensure fonts exist
    _set_if_missing(deck, ["tokens", "font", "body_family"], "Calibri")
    _set_if_missing(deck, ["tokens", "font", "title_family"], "Calibri")
    _set_if_missing(deck, ["tokens", "font", "body_size"], 18)
    _set_if_missing(deck, ["tokens", "font", "h2_size"], 28)
    _set_if_missing(deck, ["tokens", "font", "title_size"], 44)
    _set_if_missing(deck, ["tokens", "font", "min_body_size"], 14)
    # Colors present?
    if "color" not in deck.get("tokens", {}):
        deck["tokens"]["color"] = {"text": "#111827", "muted": "#6B7280", "bg": "#FFFFFF"}
        _warn(warnings, "tokens.color", "Missing color tokens; set basic defaults.")

def _clamp_col_span(grid: Dict[str, Any], columns: int, where: str, warnings: List[str]):
    col = max(1, int(grid.get("col", 1)))
    span = max(1, int(grid.get("span", 1)))
    if col > columns:
        _warn(warnings, where, f"col {col} > columns {columns}; clamped to {columns}.")
        col = columns
    if col + span - 1 > columns:
        new_span = columns - col + 1
        _warn(warnings, where, f"span {span} overflows grid; clamped to {new_span}.")
        span = new_span
    grid["col"], grid["span"] = col, span

def _ensure_row_h(comp: Dict[str, Any], tokens: Dict[str, Any], where: str, warnings: List[str]):
    # If row_h missing or too small, estimate from text type or table footprint
    if "grid" not in comp:
        return
    if comp.get("ignore_overlaps", False):
        return
    row_h = comp["grid"].get("row_h")
    if not isinstance(row_h, (int, float)) or row_h <= 0:
        text_type = comp.get("text_type", "body")
        font_size = _get(comp, ["style", "font_size"]) or _get(tokens, ["font", "body_size"])
        comp["grid"]["row_h"] = est_block_height_px(text_type, font_size)
        _warn(warnings, where, f"row_h missing; set to {comp['grid']['row_h']}px for {text_type}.")
        return
    # Too small?
    text_type = comp.get("text_type", "body")
    min_h = MIN_ROW_H.get(text_type, FALLBACK_MIN_ROW_H)
    if row_h < min_h:
        comp["grid"]["row_h"] = min_h
        _warn(warnings, where, f"row_h {row_h}px < min {min_h}px for {text_type}; bumped.")

def _is_textual(comp_type: str) -> bool:
    return comp_type in ("text", "richtext", "code")

def _bbox_from_grid(grid: Dict[str, Any], slide_width_px: int, columns: int, margin: int, gutter: int) -> Tuple[int,int,int,int]:
    # Returns (left, top, right, bottom) in px (approximate; used only for overlap checks)
    col = grid["col"]
    span = grid["span"]
    y = int(grid.get("y", margin))
    row_h = int(grid["row_h"])
    inner_w = slide_width_px - 2 * margin
    col_w = (inner_w - gutter * (columns - 1)) / columns
    left = int(margin + (col - 1) * (col_w + gutter))
    width = int(col_w * span + gutter * (span - 1))
    top = int(y)
    return left, top, left + width, top + row_h

def _overlaps(a: Tuple[int,int,int,int], b: Tuple[int,int,int,int]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)

# ---------- Core: validate + fix ----------

def validate_and_fix(deck_json: Dict[str, Any], schema_json: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Returns (cleaned_deck_json, warnings)
    Raises ValueError if schema validation fails on required top-level fields.
    """
    warnings: List[str] = []
    deck = deepcopy(deck_json)

    # 0) Basic schema validation (structure). We still proceed to autofix/layout checks.
    validator = Draft7Validator(schema_json)
    errs = sorted(validator.iter_errors(deck), key=lambda e: e.path)
    hard_fail = []
    for e in errs:
        path = ".".join([str(p) for p in e.path]) or "<root>"
        # Treat missing top-level required as hard fail; others as warnings we try to fix.
        if "deck" in str(e.message) and "is a required property" in e.message:
            hard_fail.append(f"[{path}] {e.message}")
        else:
            _warn(warnings, path, e.message)
    if hard_fail:
        raise ValueError("Schema validation failed: " + " | ".join(hard_fail))

    # 0.5) Remove unwanted footer properties
    if "deck" in deck:
        deck_obj = deck["deck"]
        # Remove footer_left, footer_right, footerleft, footerright
        for prop in ["footerleft", "footerright", "footer_left", "footer_right"]:
            if prop in deck_obj:
                deck_obj.pop(prop)
                _warn(warnings, "deck", f"Removed unnecessary property '{prop}'")

    # 1) Normalize tokens & defaults
    _normalize_tokens(deck, warnings)
    tokens = deck["tokens"]
    spacing = tokens["spacing"]
    grid_cfg = tokens["grid"]
    margin = int(spacing["margin"])
    gutter = int(max(spacing["gutter"], MIN_GUTTER_PX))
    columns = int(grid_cfg["columns"])
    unit = grid_cfg.get("unit", "px")

    # 2) Slide width approximation (px) for overlap checks.
    #    PowerPoint 16:9 default ~ 1280x720 logical px (we'll use 1280 by default).
    slide_width_px = 1280

    # 3) Walk slides and components: clamp, fill y, avoid overlaps
    for si, slide in enumerate(deck.get("slides", [])):
        where_slide = f"slide[{si}]"
        y_cursor = margin  # per-slide flow when y is not provided
        placed_boxes: List[Tuple[int,int,int,int]] = []
        placed_comps: List[Dict[str, Any]] = []  # Track placed components for shape+text logic

        if "components" not in slide or not isinstance(slide["components"], list):
            _warn(warnings, where_slide, "No components array found; skipping slide.")
            continue

        for ci, comp in enumerate(slide["components"]):
            where = f"{where_slide}.components[{ci}]"
            ctype = comp.get("type")
            
            # Fix empty fill values for all component types
            if "style" in comp and "fill" in comp["style"]:
                fill = comp["style"]["fill"]
                if fill == "" or not fill:
                    del comp["style"]["fill"]
                    _warn(warnings, where, "Removed empty 'fill' value from style.")
            
            # Remove z_index and image_metadata (not needed in output JSON)
            if "z_index" in comp:
                del comp["z_index"]
                _warn(warnings, where, "Removed 'z_index' property.")
            if "image_metadata" in comp:
                del comp["image_metadata"]
                _warn(warnings, where, "Removed 'image_metadata' property.")

            # Grid vs absolute box
            has_grid = isinstance(comp.get("grid"), dict)
            has_box = isinstance(comp.get("box"), dict)
            if not (has_grid or has_box):
                # Auto-attach a default grid block (full width body) as a safe fallback
                comp["grid"] = {"col": 1, "span": columns, "row_h": MIN_ROW_H.get("body", 72), "y": y_cursor}
                has_grid = True
                _warn(warnings, where, "Missing grid/box; attached full-width default grid block.")

            if has_grid:
                g = comp["grid"]
                # Clamp col/span to grid
                _clamp_col_span(g, columns, where, warnings)
                # Ensure row_h minimums for text-ish blocks
                _ensure_row_h(comp, tokens, where, warnings)
                # Fill missing y using flow cursor
                if "y" not in g or not isinstance(g["y"], (int, float)):
                    g["y"] = y_cursor

                # Build bbox & nudge down to avoid overlap
                bbox = _bbox_from_grid(g, slide_width_px, columns, margin, gutter)
                bumped = False

                def _should_ignore_overlap_with(prev_comp, prev_bbox):
                    # Only for previous component being a shape with text
                    if not prev_comp:
                        return False
                    if prev_comp.get("type") != "shape":
                        return False
                    # Check if shape has text: either 'value' (like text), or 'text' property, or 'text_type'
                    if prev_comp.get("value") or prev_comp.get("text") or prev_comp.get("text_type"):
                        # Only ignore overlap if the overlap is with this shape
                        return True
                    return False

                # Only ignore overlap with previous shape+text, not all shapes
                ignore_overlaps=comp.get("ignore_overlaps",False)
                while True and not ignore_overlaps:  # Only run overlap fixing if not ignored
                    overlap_found = False
                    for prev_idx, other in enumerate(placed_boxes):
                        prev_comp = placed_comps[prev_idx] if prev_idx < len(placed_comps) else None
                        if _overlaps(bbox, other):
                            if _should_ignore_overlap_with(prev_comp, other):
                                continue  # ignore this overlap
                            else:
                                overlap_found = True
                                break
                    if overlap_found:
                        g["y"] = g["y"] + gutter + 8  # bump slightly more than gutter to clear
                        bbox = _bbox_from_grid(g, slide_width_px, columns, margin, gutter)
                        bumped = True
                    else:
                        break

                if bumped:
                    _warn(warnings, where, "Adjusted 'y' downward to prevent overlap.")

                # Update flow cursor for next block if same column region (simple heuristic)
                y_cursor = max(y_cursor, g["y"] + g["row_h"] + gutter)
                placed_boxes.append(bbox)
                placed_comps.append(comp)

            elif has_box:
                b = comp["box"]
                for k in ("x", "y", "w", "h"):
                    if k not in b:
                        _warn(warnings, where, f"box.{k} missing; set to 0/10 fallback.")
                        b.setdefault(k, 0 if k in ("x","y") else 10)
                # Minimal sanity: non-zero size
                if b["w"] <= 0 or b["h"] <= 0:
                    _warn(warnings, where, "box has non-positive size; set to 10x10.")
                    b["w"], b["h"] = 10, 10
                # For absolute boxes, still track for shape+text logic
                placed_boxes.append((b["x"], b["y"], b["x"]+b["w"], b["y"]+b["h"]))
                placed_comps.append(comp)

            # Content sanity checks
            if ctype == "text":
                if not comp.get("value"):
                    _warn(warnings, where, "Empty text value.")
                # Ensure text_type exists
                comp.setdefault("text_type", "body")
                # Ensure colors are valid hex or token keys; warn if not hex
                color = _get(comp, ["style", "color"])
                if color and not COLOR_HEX_RE.match(color):
                    # allow token names (e.g., "text"); just warn if neither hex nor token present
                    if color not in deck["tokens"].get("color", {}):
                        _warn(warnings, where, f"style.color '{color}' not hex and not a known token key.")
            elif ctype == "richtext":
                runs = comp.get("runs", [])
                if not isinstance(runs, list) or not runs:
                    _warn(warnings, where, "richtext has no runs; converting to empty body text.")
                    comp["type"] = "text"
                    comp["text_type"] = "body"
                    comp["value"] = ""
                    comp.pop("runs", None)
            elif ctype == "table":
                content = comp.get("content", {})
                cols = content.get("columns") or []
                rows = content.get("rows") or []
                if not cols:
                    _warn(warnings, where, "table has no columns; inserting placeholder col.")
                    content["columns"] = ["Column 1"]
                # Mark big tables to paginate
                if len(rows) > 15 and comp.get("fit") != "paginate":
                    comp["fit"] = "paginate"
                    _warn(warnings, where, "Large table; set fit='paginate'.")
            elif ctype == "image":
                if not comp.get("src"):
                    _warn(warnings, where, "image missing 'src'.")
            elif ctype == "chart":
                content = comp.get("content", {})
                if not content.get("categories") or not content.get("series"):
                    _warn(warnings, where, "chart missing categories/series.")

    return deck, warnings