"""
Tests for modules/vision_analyzers.py - all pure logic, no camera needed.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.vision_analyzers import analyze_lighting, analyze_details, analyze_focus, analyze_motion


def solid_gray_frame(value, size=(100, 100)):
    return np.full(size, value, dtype=np.uint8)


class TestAnalyzeLighting:
    def test_low_light(self):
        frame = solid_gray_frame(10)
        result = analyze_lighting(frame, low_threshold=50, high_threshold=200)
        assert result["status"] == "LOW LIGHT"
        assert result["color"] == (0, 0, 255)

    def test_bright(self):
        frame = solid_gray_frame(230)
        result = analyze_lighting(frame, low_threshold=50, high_threshold=200)
        assert result["status"] == "BRIGHT"
        assert result["color"] == (0, 255, 255)

    def test_optimal(self):
        frame = solid_gray_frame(120)
        result = analyze_lighting(frame, low_threshold=50, high_threshold=200)
        assert result["status"] == "OPTIMAL"
        assert result["color"] == (0, 255, 0)

    def test_brightness_value_matches_mean(self):
        frame = solid_gray_frame(77)
        result = analyze_lighting(frame, low_threshold=50, high_threshold=200)
        assert result["brightness"] == 77.0


class TestAnalyzeDetails:
    def test_solid_frame_has_zero_edge_density(self):
        frame = solid_gray_frame(128)
        result = analyze_details(frame)
        assert result["edge_density"] == 0.0

    def test_high_contrast_checkerboard_has_edges(self):
        frame = np.zeros((100, 100), dtype=np.uint8)
        frame[::2, ::2] = 255  # checkerboard pattern -> lots of edges
        result = analyze_details(frame)
        assert result["edge_density"] > 0.0


class TestAnalyzeFocus:
    def test_solid_frame_is_blurry(self):
        # A perfectly flat frame has zero variance -> definitely "blurry"
        frame = solid_gray_frame(128)
        result = analyze_focus(frame)
        assert result["is_blurry"] is True
        assert result["focus_score"] == 0.0

    def test_sharp_pattern_has_higher_focus_score(self):
        frame = np.zeros((100, 100), dtype=np.uint8)
        frame[::2, :] = 255  # sharp alternating stripes -> strong Laplacian response
        result = analyze_focus(frame)
        assert result["focus_score"] > 0.0


class TestAnalyzeMotion:
    def test_none_prev_frame_reports_no_motion(self):
        frame = solid_gray_frame(100)
        result = analyze_motion(None, frame)
        assert result["motion_detected"] is False
        assert result["motion_percent"] == 0.0

    def test_identical_frames_report_no_motion(self):
        frame = solid_gray_frame(100)
        result = analyze_motion(frame.copy(), frame)
        assert result["motion_detected"] is False
        assert result["motion_percent"] == 0.0

    def test_large_change_detected_as_motion(self):
        prev_frame = solid_gray_frame(0)
        curr_frame = solid_gray_frame(255)
        result = analyze_motion(prev_frame, curr_frame)
        assert result["motion_detected"] is True
        assert result["motion_percent"] > 90.0

    def test_mismatched_frame_shapes_report_no_motion(self):
        prev_frame = solid_gray_frame(100, size=(50, 50))
        curr_frame = solid_gray_frame(100, size=(100, 100))
        result = analyze_motion(prev_frame, curr_frame)
        assert result["motion_detected"] is False
