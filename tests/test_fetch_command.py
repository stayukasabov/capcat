
import unittest
import os
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capcat import run_app

class TestFetchCommand(unittest.TestCase):
    def setUp(self):
        self.output_dir = 'test_output_fetch'
        # Ensure the output directory doesn't exist before each test
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def tearDown(self):
        # Clean up the output directory after each test
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_fetch_single_article(self):
        """Tests if the fetch command can fetch a single article."""
        try:
            run_app(['fetch', 'bbc', '--count', '1', '-o', self.output_dir])
        except SystemExit as e:
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
