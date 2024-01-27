import unittest
from main import random_value_in_range, generate_random_scan, update_list, create_prompt, get_bot_response

class TestYourModule(unittest.TestCase):

    def test_random_value_in_range(self):
        # Test cases for different formats of range strings
        self.assertTrue(53 <= random_value_in_range('53 - 106') <= 106)
        self.assertTrue(0 <= random_value_in_range('<40') < 40)
        self.assertTrue(10 <= random_value_in_range('>10') < 30)  # Assuming upper limit is 3 times lower limit

    def test_generate_random_scan(self):
        scan = generate_random_scan()
        # Test if all expected keys are present
        self.assertIn('Creatinine', scan)
        self.assertIn('Glucose', scan)
        self.assertIn('HDL Cholesterol', scan)
        self.assertIn('Albumin', scan)
        self.assertIn('ALT', scan)
        self.assertIn('AST', scan)

    def test_update_list(self):
        prompt_list = ['Initial']
        update_list('New Message', prompt_list)
        self.assertIn('New Message', prompt_list)

    def test_create_prompt(self):
        prompt_list = ['Initial']
        prompt = create_prompt('User Message', prompt_list)
        self.assertIn('User Message', prompt)

    def test_get_bot_response(self):
        prompt_list = ['Initial']
        response = get_bot_response('Hello', prompt_list)
        self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()
