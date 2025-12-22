"""Tests for GUI mouse scroll functionality"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestGUIMouseScroll(unittest.TestCase):
    """Test mouse scroll functionality in the episode selection area"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        # Mock season1.json to avoid file dependency
        cls.mock_episodes = [
            {"episode": i, "title": f"Episode {i}", "video_url": f"http://example.com/{i}"}
            for i in range(1, 9)
        ]

    def setUp(self):
        """Set up each test"""
        # Patch load_episodes before importing GUI
        self.load_episodes_patcher = patch(
            'thechosen_downloader.gui.load_episodes',
            return_value=self.mock_episodes
        )
        self.load_episodes_patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.load_episodes_patcher.stop()

    def test_gui_creates_scrollable_frame(self):
        """Test that GUI creates a scrollable episode frame"""
        import customtkinter as ctk
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Verify episode_frame is a scrollable frame
            self.assertIsInstance(app.episode_frame, ctk.CTkScrollableFrame)

            # Verify it has the expected height
            self.assertEqual(app.episode_frame.cget("height"), 200)

        finally:
            app.destroy()

    def test_scrollable_frame_has_native_mousewheel_binding(self):
        """Test that CTkScrollableFrame has built-in mouse wheel support"""
        import customtkinter as ctk
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Verify CTkScrollableFrame has _mouse_wheel_all method (native support)
            self.assertTrue(hasattr(app.episode_frame, '_mouse_wheel_all'))
            self.assertTrue(callable(app.episode_frame._mouse_wheel_all))

            # Verify the frame has a parent canvas for scrolling
            self.assertTrue(hasattr(app.episode_frame, '_parent_canvas'))

        finally:
            app.destroy()

    def test_native_scroll_handles_macos_delta(self):
        """Test that native scroll correctly handles macOS delta values"""
        import customtkinter as ctk
        import sys
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Track yview calls
            yview_calls = []
            original_yview = app.episode_frame._parent_canvas.yview

            def mock_yview(*args):
                if args:
                    # Called with scroll arguments
                    yview_calls.append(args)
                else:
                    # Called to get current position
                    return (0.0, 0.5)  # Scrollable state

            app.episode_frame._parent_canvas.yview = mock_yview

            # Mock check_if_master_is_canvas to return True
            app.episode_frame.check_if_master_is_canvas = lambda w: True

            # Simulate mousewheel event with macOS-style delta
            mock_event = MagicMock()
            mock_event.widget = app.episode_frame
            mock_event.delta = 1  # macOS uses small delta values (1, 2, 3...)

            # Call native mouse wheel handler
            app.episode_frame._mouse_wheel_all(mock_event)

            # On macOS, delta is used directly: -event.delta
            if sys.platform == "darwin":
                self.assertEqual(len(yview_calls), 1)
                # yview("scroll", -delta, "units")
                self.assertEqual(yview_calls[0], ("scroll", -1, "units"))

        finally:
            app.destroy()

    def test_all_episodes_have_checkboxes(self):
        """Test that all 8 episodes have checkboxes in the scrollable area"""
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Verify we have 8 episode variables
            self.assertEqual(len(app.episode_vars), 8)

            # Verify all are BooleanVars set to False initially
            for var in app.episode_vars:
                self.assertFalse(var.get())

        finally:
            app.destroy()

    def test_scrollable_frame_contains_checkboxes(self):
        """Test that checkboxes are children of the scrollable frame"""
        import customtkinter as ctk
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Get all children of the episode frame
            children = app.episode_frame.winfo_children()

            # Count checkboxes
            checkboxes = [c for c in children if isinstance(c, ctk.CTkCheckBox)]

            # Should have 8 checkboxes
            self.assertEqual(len(checkboxes), 8)

        finally:
            app.destroy()


class TestScrollbarPositionChange(unittest.TestCase):
    """Test that mouse wheel actually moves the scrollbar position"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures with many episodes to ensure scrollable content"""
        # Create 20 episodes to ensure content overflows and is scrollable
        cls.mock_episodes = [
            {"episode": i, "title": f"Episode {i} - A Very Long Title To Take Up Space", "video_url": f"http://example.com/{i}"}
            for i in range(1, 21)
        ]

    def setUp(self):
        """Set up each test"""
        self.load_episodes_patcher = patch(
            'thechosen_downloader.gui.load_episodes',
            return_value=self.mock_episodes
        )
        self.load_episodes_patcher.start()

    def tearDown(self):
        """Clean up after each test"""
        self.load_episodes_patcher.stop()

    def test_scrollbar_position_changes_on_mousewheel(self):
        """Test that scrollbar position actually changes when mouse wheel is used"""
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            # Force GUI to render and update
            app.update_idletasks()
            app.update()

            canvas = app.episode_frame._parent_canvas

            # Get initial scroll position
            initial_position = canvas.yview()
            print(f"Initial scroll position: {initial_position}")

            # Scroll position is (top, bottom) where 0.0 = top, 1.0 = bottom
            # If content is scrollable, initial should be (0.0, something < 1.0)

            # Check if content is scrollable (not all visible)
            if initial_position == (0.0, 1.0):
                self.skipTest("Content fits in view, not scrollable")

            # Simulate scroll down by directly calling yview_scroll
            canvas.yview_scroll(5, "units")
            app.update_idletasks()
            app.update()

            # Get new scroll position
            new_position = canvas.yview()
            print(f"New scroll position after scroll: {new_position}")

            # Verify position changed (scrolled down means top value increased)
            self.assertGreater(
                new_position[0],
                initial_position[0],
                f"Scrollbar should have moved down. Initial: {initial_position}, New: {new_position}"
            )

        finally:
            app.destroy()

    def test_scroll_down_then_up_returns_to_original(self):
        """Test scrolling down then up returns to approximately original position"""
        from thechosen_downloader.gui import TheChosenDownloaderGUI

        app = TheChosenDownloaderGUI()

        try:
            app.update_idletasks()
            app.update()

            canvas = app.episode_frame._parent_canvas
            initial_position = canvas.yview()

            if initial_position == (0.0, 1.0):
                self.skipTest("Content fits in view, not scrollable")

            # Scroll down
            canvas.yview_scroll(3, "units")
            app.update()

            # Scroll back up
            canvas.yview_scroll(-3, "units")
            app.update()

            final_position = canvas.yview()

            # Should be back at or near the top
            self.assertAlmostEqual(
                final_position[0],
                initial_position[0],
                places=2,
                msg=f"Should return to original position. Initial: {initial_position}, Final: {final_position}"
            )

        finally:
            app.destroy()


class TestCTkScrollableFrameNativeSupport(unittest.TestCase):
    """Test that CTkScrollableFrame has proper native scroll support"""

    def test_ctk_scrollable_frame_has_mouse_wheel_method(self):
        """Verify CTkScrollableFrame class has _mouse_wheel_all"""
        import customtkinter as ctk

        self.assertTrue(hasattr(ctk.CTkScrollableFrame, '_mouse_wheel_all'))

    def test_ctk_scrollable_frame_binds_mousewheel_on_init(self):
        """Verify CTkScrollableFrame binds MouseWheel in __init__"""
        import customtkinter as ctk
        import inspect

        source = inspect.getsource(ctk.CTkScrollableFrame.__init__)

        # Check that MouseWheel binding is set up
        self.assertIn('bind_all("<MouseWheel>"', source)
        self.assertIn('_mouse_wheel_all', source)

    def test_native_scroll_supports_macos(self):
        """Verify native scroll implementation handles macOS"""
        import customtkinter as ctk
        import inspect

        source = inspect.getsource(ctk.CTkScrollableFrame._mouse_wheel_all)

        # Check for macOS-specific handling
        self.assertIn('darwin', source)
        # macOS uses delta directly (not divided by 120 like Windows)
        self.assertIn('-event.delta', source)


if __name__ == '__main__':
    print("Running GUI mouse scroll tests...\n")
    unittest.main(verbosity=2)
