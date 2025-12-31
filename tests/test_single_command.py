import unittest
import os
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capcat import run_app

class TestSingleCommand(unittest.TestCase):
    def setUp(self):
        self.output_dir = 'test_output_single'
        # Ensure the output directory doesn't exist before each test
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def tearDown(self):
        # Clean up the output directory after each test
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_output_directory_is_respected_for_single_command(self):
        """Tests if the single command respects the -o/--output flag."""
        # A non-specialized source URL
        url = 'https://news.ycombinator.com/item?id=40235991' # Example URL

        # Run the single command with output directory specified
        try:
            run_app(['single', url, '-o', self.output_dir])
        except SystemExit as e:
            # The app calls sys.exit(), we catch it to continue the test
            self.assertEqual(e.code, 0, f"Application exited with error code {e.code}")

        # Check if the output directory was created
        self.assertTrue(
            os.path.isdir(self.output_dir),
            f"Output directory '{self.output_dir}' was not created."
        )

        # Check if the output directory is not empty
        self.assertTrue(
            len(os.listdir(self.output_dir)) > 0,
            f"Output directory '{self.output_dir}' is empty."
        )

if __name__ == '__main__':
    unittest.main()