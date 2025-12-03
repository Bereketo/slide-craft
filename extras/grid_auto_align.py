#!/usr/bin/env python3
"""
Grid Auto-Alignment System
Automatically adjusts grid positioning to prevent overlapping components.
"""

import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class GridRect:
    """Represents a grid rectangle with position and dimensions."""
    col: int
    span: int
    y: float
    row_h: float
    component_id: str
    component_type: str
    
    @property
    def end_col(self) -> int:
        return self.col + self.span - 1
    
    @property
    def bottom_y(self) -> float:
        return self.y + self.row_h
    
    def overlaps_with(self, other: 'GridRect', margin: float = 0) -> bool:
        """Check if this rectangle overlaps with another rectangle."""
        # Check horizontal overlap
        horizontal_overlap = not (self.end_col < other.col or other.end_col < self.col)
        
        # Check vertical overlap (with optional margin)
        vertical_overlap = not (self.bottom_y + margin < other.y or other.bottom_y + margin < self.y)
        
        return horizontal_overlap and vertical_overlap
    
    def __str__(self) -> str:
        return f"GridRect(col={self.col}, span={self.span}, y={self.y}, h={self.row_h}, type={self.component_type})"


class GridAutoAligner:
    """Automatically adjusts grid positioning to prevent overlaps."""
    
    def __init__(self, tokens: Dict[str, Any]):
        self.tokens = tokens
        self.grid_columns = tokens["grid"]["columns"]
        self.margin = tokens["spacing"]["margin"]
        self.gutter = tokens["spacing"]["gutter"]
        self.min_gap = 8  # Minimum gap between components in pixels
        
    def _would_overlap(self, test: GridRect, placed_rects: List[GridRect]) -> bool:
        """Return True if test rectangle overlaps any placed rectangle (with min_gap)."""
        for existing in placed_rects:
            if test.overlaps_with(existing, self.min_gap):
                return True
        return False

    def _max_overlap_bottom_y(self, test: GridRect, placed_rects: List[GridRect]) -> float:
        """Return maximum bottom_y among placed rects that overlap horizontally with test.
        If none overlap horizontally, returns test.y.
        """
        max_bottom = test.y
        for existing in placed_rects:
            # Horizontal overlap only; vertical will be resolved by pushing down
            horiz_overlap = not (test.end_col < existing.col or existing.end_col < test.col)
            if horiz_overlap:
                if existing.bottom_y + self.min_gap > max_bottom:
                    max_bottom = existing.bottom_y + self.gutter
        return max_bottom

    def place_rect(self, rect: GridRect, placed_rects: List[GridRect]) -> Tuple[int, float]:
        """Smart placement: try keep column and y, then try other columns, else push down and retry.
        Special rule: for images, NEVER move horizontally; only push down to avoid overlap.
        Returns (col, y).
        """
        max_iters = 100
        # Determine which columns to try. For images/charts/tables, lock to original column.
        if rect.component_type in ("image", "chart", "table"):
            tried_cols = [rect.col]
        else:
            tried_cols = list(range(1, self.grid_columns - rect.span + 2))
            # Prefer original column first
            if rect.col in tried_cols:
                tried_cols.remove(rect.col)
                tried_cols.insert(0, rect.col)

        current_y = rect.y
        for _ in range(max_iters):
            # Try each column at current_y
            for col in tried_cols:
                test = GridRect(col=col, span=rect.span, y=current_y, row_h=rect.row_h,
                                component_id=rect.component_id, component_type=rect.component_type)
                if not self._would_overlap(test, placed_rects):
                    return col, current_y
            # All columns at this y overlap; push down just below the lowest overlapping item in preferred column span
            preferred_col = rect.col if 1 <= rect.col <= self.grid_columns - rect.span + 1 else 1
            test_pref = GridRect(col=preferred_col, span=rect.span, y=current_y, row_h=rect.row_h,
                                 component_id=rect.component_id, component_type=rect.component_type)
            new_y = self._max_overlap_bottom_y(test_pref, placed_rects)
            if new_y <= current_y:
                # Fallback incremental push
                new_y = current_y + self.gutter
            current_y = new_y
        # Fallback: place at last computed position in original column
        return rect.col, current_y

    def extract_grid_rects(self, components: List[Dict[str, Any]]) -> List[GridRect]:
        """Extract grid rectangles from components."""
        rects = []
        
        for i, comp in enumerate(components):
            if "grid" not in comp:
                continue
                
            grid = comp["grid"]
            rect = GridRect(
                col=grid["col"],
                span=grid["span"],
                y=grid.get("y", 0),
                row_h=grid["row_h"],
                component_id=f"comp_{i}",
                component_type=comp.get("type", "unknown")
            )
            rects.append(rect)
            
        return rects
    
    def detect_overlaps(self, rects: List[GridRect]) -> List[Tuple[GridRect, GridRect]]:
        """Detect overlapping rectangles."""
        overlaps = []
        
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if rects[i].overlaps_with(rects[j], self.min_gap):
                    overlaps.append((rects[i], rects[j]))
                    
        return overlaps
    
    def find_available_position(self, rect: GridRect, existing_rects: List[GridRect], 
                              preferred_col: Optional[int] = None) -> Tuple[int, float]:
        """Find an available position for a rectangle."""
        # Try preferred column first
        if preferred_col and 1 <= preferred_col <= self.grid_columns - rect.span + 1:
            test_rect = GridRect(
                col=preferred_col,
                span=rect.span,
                y=rect.y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            )
            
            if not any(test_rect.overlaps_with(existing, self.min_gap) for existing in existing_rects):
                return preferred_col, rect.y
        
        # Try different columns
        for col in range(1, self.grid_columns - rect.span + 2):
            test_rect = GridRect(
                col=col,
                span=rect.span,
                y=rect.y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            )
            
            if not any(test_rect.overlaps_with(existing, self.min_gap) for existing in existing_rects):
                return col, rect.y
        
        # If no horizontal space, try moving down
        max_bottom = max((r.bottom_y for r in existing_rects), default=0)
        new_y = max_bottom + self.gutter
        
        # Try original column with new Y
        test_rect = GridRect(
            col=rect.col,
            span=rect.span,
            y=new_y,
            row_h=rect.row_h,
            component_id=rect.component_id,
            component_type=rect.component_type
        )
        
        if not any(test_rect.overlaps_with(existing, self.min_gap) for existing in existing_rects):
            return rect.col, new_y
        
        # Try other columns with new Y
        for col in range(1, self.grid_columns - rect.span + 2):
            test_rect = GridRect(
                col=col,
                span=rect.span,
                y=new_y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            )
            
            if not any(test_rect.overlaps_with(existing, self.min_gap) for existing in existing_rects):
                return col, new_y
        
        # Fallback: return original position
        return rect.col, rect.y
    
    def auto_align_components(self, components: List[Dict[str, Any]], 
                            strategy: str = "preserve_order") -> List[Dict[str, Any]]:
        """
        Auto-align components to prevent overlaps.
        
        Strategies:
        - "preserve_order": Keep original order, adjust positions
        - "compact": Try to minimize total height
        - "balanced": Balance components across columns
        """
        if not components:
            return components
            
        # Extract grid rectangles
        rects = self.extract_grid_rects(components)
        if not rects:
            return components
            
        # Create a copy of components to modify
        aligned_components = deepcopy(components)
        
        if strategy == "preserve_order":
            return self._align_preserve_order(aligned_components, rects)
        elif strategy == "compact":
            return self._align_compact(aligned_components, rects)
        elif strategy == "balanced":
            return self._align_balanced(aligned_components, rects)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _align_preserve_order(self, components: List[Dict[str, Any]], 
                            rects: List[GridRect]) -> List[Dict[str, Any]]:
        """Align components preserving their original order."""
        # Sort by original y to respect top-down flow; stable to preserve order among equals
        order = sorted(range(len(rects)), key=lambda i: rects[i].y)
        placed_rects: List[GridRect] = []
        
        for idx in order:
            comp = components[idx]
            rect = rects[idx]
            if "grid" not in comp:
                continue

            # Smart placement: try best fit then push down iteratively
            new_col, new_y = self.place_rect(rect, placed_rects)

            # Update component
            comp["grid"]["col"] = new_col
            comp["grid"]["y"] = new_y

            # Track placement
            placed_rects.append(GridRect(
                col=new_col,
                span=rect.span,
                y=new_y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            ))
            
        return components
    
    def _align_compact(self, components: List[Dict[str, Any]], 
                      rects: List[GridRect]) -> List[Dict[str, Any]]:
        """Align components to minimize total height."""
        # Sort by height (tallest first) to place them optimally
        sorted_indices = sorted(range(len(rects)), key=lambda i: rects[i].row_h, reverse=True)
        placed_rects = []
        
        for idx in sorted_indices:
            comp = components[idx]
            rect = rects[idx]
            
            if "grid" not in comp:
                continue
                
            # Find best position (prefer leftmost available)
            best_col, best_y = self.find_available_position(rect, placed_rects)
            
            # Update component
            comp["grid"]["col"] = best_col
            comp["grid"]["y"] = best_y
            
            # Create new rect for tracking
            new_rect = GridRect(
                col=best_col,
                span=rect.span,
                y=best_y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            )
            placed_rects.append(new_rect)
            
        return components
    
    def _align_balanced(self, components: List[Dict[str, Any]], 
                       rects: List[GridRect]) -> List[Dict[str, Any]]:
        """Balance components across columns."""
        # Track column heights
        column_heights = [0.0] * self.grid_columns
        placed_rects = []
        
        for i, (comp, rect) in enumerate(zip(components, rects)):
            if "grid" not in comp:
                continue
                
            # Find column with minimum height that can accommodate this component
            best_col = 1
            min_height = float('inf')
            
            for col in range(1, self.grid_columns - rect.span + 2):
                # Check if this column range is available
                max_height_in_range = max(column_heights[col-1:col-1+rect.span])
                
                if max_height_in_range < min_height:
                    min_height = max_height_in_range
                    best_col = col
            
            # Place component
            new_y = min_height + self.gutter
            comp["grid"]["col"] = best_col
            comp["grid"]["y"] = new_y
            
            # Update column heights
            for col in range(best_col, best_col + rect.span):
                column_heights[col-1] = new_y + rect.row_h
            
            # Create new rect for tracking
            new_rect = GridRect(
                col=best_col,
                span=rect.span,
                y=new_y,
                row_h=rect.row_h,
                component_id=rect.component_id,
                component_type=rect.component_type
            )
            placed_rects.append(new_rect)
            
        return components
    
    def validate_alignment(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the final alignment and return statistics."""
        rects = self.extract_grid_rects(components)
        overlaps = self.detect_overlaps(rects)
        
        total_height = max((r.bottom_y for r in rects), default=0)
        column_usage = [0] * self.grid_columns
        
        for rect in rects:
            for col in range(rect.col, rect.col + rect.span):
                column_usage[col-1] += 1
        
        return {
            "overlaps_detected": len(overlaps),
            "overlapping_pairs": [(r1.component_id, r2.component_id) for r1, r2 in overlaps],
            "total_height": total_height,
            "column_usage": column_usage,
            "components_count": len(rects),
            "is_valid": len(overlaps) == 0
        }


def auto_align_slide_components(slide_data: Dict[str, Any], tokens: Dict[str, Any], 
                               strategy: str = "preserve_order") -> Dict[str, Any]:
    """
    Auto-align components in a single slide.
    
    Args:
        slide_data: Slide data with components
        tokens: Design tokens with grid configuration
        strategy: Alignment strategy ("preserve_order", "compact", "balanced")
    
    Returns:
        Updated slide data with aligned components
    """
    aligner = GridAutoAligner(tokens)
    
    if "components" not in slide_data:
        return slide_data
    
    aligned_components = aligner.auto_align_components(
        slide_data["components"], 
        strategy
    )
    
    # Validate the result
    validation = aligner.validate_alignment(aligned_components)
    
    # Create updated slide data (don't add validation metadata to avoid schema issues)
    updated_slide = deepcopy(slide_data)
    updated_slide["components"] = aligned_components
    
    return updated_slide


def auto_align_presentation(presentation_data: Dict[str, Any], 
                           strategy: str = "preserve_order") -> Dict[str, Any]:
    """
    Auto-align components across all slides in a presentation.
    
    Args:
        presentation_data: Full presentation JSON data
        strategy: Alignment strategy ("preserve_order", "compact", "balanced")
    
    Returns:
        Updated presentation data with aligned components
    """
    if "slides" not in presentation_data or "tokens" not in presentation_data:
        raise ValueError("Presentation data must contain 'slides' and 'tokens'")
    
    tokens = presentation_data["tokens"]
    updated_slides = []
    
    for slide in presentation_data["slides"]:
        aligned_slide = auto_align_slide_components(slide, tokens, strategy)
        updated_slides.append(aligned_slide)
    
    # Create updated presentation
    updated_presentation = deepcopy(presentation_data)
    updated_presentation["slides"] = updated_slides
    
    return updated_presentation


# Example usage and testing
if __name__ == "__main__":
    # Example JSON data with overlapping components
    example_data = {
        "tokens": {
            "grid": {"columns": 12, "unit": "px"},
            "spacing": {"margin": 48, "gutter": 12}
        },
        "slides": [
            {
                "title": "Test Slide",
                "components": [
                    {
                        "type": "text",
                        "text_type": "h2",
                        "value": "Title",
                        "grid": {"col": 1, "span": 6, "row_h": 60, "y": 100}
                    },
                    {
                        "type": "text", 
                        "text_type": "body",
                        "value": "Content",
                        "grid": {"col": 4, "span": 6, "row_h": 100, "y": 100}  # Overlaps with title
                    },
                    {
                        "type": "table",
                        "grid": {"col": 1, "span": 12, "row_h": 200, "y": 200}
                    }
                ]
            }
        ]
    }
    
    # Test auto-alignment
    print("Original data:")
    print(json.dumps(example_data["slides"][0]["components"], indent=2))
    
    # Apply auto-alignment
    aligned_data = auto_align_presentation(example_data, strategy="preserve_order")
    
    print("\nAligned data:")
    print(json.dumps(aligned_data["slides"][0]["components"], indent=2))
    
    # Show validation results
    validation = aligned_data["slides"][0]["_alignment_validation"]
    print(f"\nValidation:")
    print(f"Overlaps detected: {validation['overlaps_detected']}")
    print(f"Total height: {validation['total_height']}")
    print(f"Is valid: {validation['is_valid']}")
