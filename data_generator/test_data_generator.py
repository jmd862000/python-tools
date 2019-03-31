import unittest
import data_generator
import mock

class TestDataGenerator(unittest.TestCase):
    def setUp(self):
        self.test_data = data_generator.SourceData()
        self.test_data.input_source_file('test.csv', 'test', 'csv')

    def test_source_data(self):
        self.assertIsNotNone(self.test_data.get('test'))

    def test_data_generator(self):
        config = data_generator.ConfigurationSettings(
            'data_generator.conf').config
        test_generator = data_generator.DataGenerator(
            'random_entries', config, self.test_data)
        self.assertIsNotNone(test_generator)
        row = test_generator.generate_row()
        with mock.patch('data_generator.open', mock.mock_open()) as mock_open:
            handle = mock_open()
            test_generator.output_csv()
            self.assertEquals(handle.write.call_count, 501)
        self.assertIsNotNone(row)


if __name__ == '__main__':
    unittest.main()
