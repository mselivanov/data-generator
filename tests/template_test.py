"""
Module unit-tests template package.
"""
import unittest
from string import ascii_letters
from string import hexdigits

import datagenerator.template.functions as func

class TemplateFunctionsTests(unittest.TestCase):
    """
    Class tests datagenerator.template.functions module
    """
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_random_int_start_and_end_equal(self):
        x = func.random_int(1, 1)
        self.assertEqual(1, x)
        
    def test_random_int_range(self):
        for _ in range(20):    
            x = func.random_int(1, 5)
            self.assertTrue(1<=x<=5, "Random int not in expected range")
    
    def test_alpha_contains_only_letters(self):
        for _ in range(20):
            letters_sequence = func.alpha(10)
            self.assertFalse([_ for _ in letters_sequence if _ not in ascii_letters], "Sequence {0} contains not only ascii letters".format(letters_sequence))
            
    def test_alpha_length(self):
        for idx in range(20):
            letters_sequence = func.alpha(idx)
            self.assertTrue(len(letters_sequence) == idx, "Sequence {0} must have length {1}".format(letters_sequence, idx))

    def test_random_sentence(self):
        for idx in range(10, 30):
            sentence = func.random_sentence(idx)
            word_count = len(sentence.split())
            self.assertTrue(idx == word_count, "Sentence '{0}' has {1} words. Must have {2} words.".format(sentence, word_count, idx))
    
    def test_array_generation(self):
        def array_function(x, y, z):
            return x + y - z
        params = [(1, 2, 3), (10, 21, 21), (90, 20, 23)]
        answers = [array_function(*param) for param in params]
        element_number = 5
        for param in params:
            arr = func.array(element_number, array_function, *param)
            answers = [array_function(*param) for _ in range(element_number)]
            self.assertEqual(answers, arr, "Generated array {0} must be equal to {1}".format(arr, answers))
    
    def test_random_uuid_string(self):
        uuid_length = 36 # 16 bytes in hex and 4 delimiters
        allowed_symbols = hexdigits + "-"
        for _ in range(20):
            random_uuid = func.random_uuid_string()
            self.assertEqual(len(random_uuid), uuid_length)
            self.assertFalse([_ for _ in random_uuid if _ not in allowed_symbols])

if __name__ == "__main__":
    unittest.main()