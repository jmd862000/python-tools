import pandas
import configparser
import random
import csv
import collections

class ConfigurationSettings(object):
    def __init__(self, filename):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

class SourceData(dict):
    def __init__(self, *arg, **kw):
        super(SourceData, self).__init__(*arg, **kw)

    def input_source_file(self, filename, source_name, type):
        self[source_name] = {}
        if type == 'csv':
            data_frame = pandas.read_csv(filename, dtype="str")
            data_frame.columns = ["{0}::{1}".format(source_name, col) for col in data_frame.columns]
            for col in data_frame.columns:
                self[source_name][col] = data_frame[col].dropna().tolist()
        elif type == 'txt':
            with open(filename, 'rb') as source_file:
                self[source_name]['data'] = source_file.readlines()


class DataGenerator(object):
    def __init__(self, record_name, config_parser, source_data=None):
        self.config_parser = config_parser
        self.record_name = record_name
        self.columns = clean_comma_split(self.config_parser.get(record_name, 'columns'))
        self.record_count = self.config_parser.getint(record_name, 'number_of_records')
        self.filename = self.config_parser.get(record_name, 'filename')
        self.record_type = self.config_parser.get(record_name, 'type')
        self.source_data = source_data or SourceData()
        self.output_columns = self.generate_output_columns()

    def generate_output_columns(self):
        result = collections.OrderedDict()
        for column in self.columns:
            result[column] = self.get_output_column_name(column)
        return result

    def generate_row(self):
        row = {}
        for column in self.columns:
            field_selection_type = self.config_parser.get(column, 'selection_type')
            if self.config_parser.has_option(column, 'source'):
                field_sources = self.config_parser.get(column, 'source')
            else:
                field_sources = ''
            field_eval = self.config_parser.get(column, 'source_eval')
            source_data = []
            if field_selection_type == 'random':
                for source in clean_comma_split(field_sources):
                    source_data.append(self.get_random_source_value(source))
            elif field_selection_type == 'static':
                source_data.append(field_sources)
            elif field_selection_type == 'correlated':
                correlated_columns = clean_comma_split(self.config_parser.get(column, 'correlated_source_columns'))
                correlated_output_columns = clean_comma_split(self.config_parser.get(column, 'correlated_output_columns'))
                correlated_results = self.get_correlated_source_values(field_sources, correlated_columns)
                source_data.append(correlated_results[field_sources])
                for index, col in enumerate(correlated_columns):
                    source_value = correlated_results[col]
                    col_eval = self.config_parser.get(col, 'source_eval').replace('<0>', "\"{}\"".format(source_value))
                    row[self.output_columns[correlated_output_columns[index]]] = eval(col_eval)
            elif field_selection_type == 'correlated_output':
                continue
            for i, v in enumerate(source_data):
                field_eval = field_eval.replace('<{}>'.format(i), "\"{}\"".format(v))
            row[self.output_columns[column]] = eval(field_eval)
        return row

    def get_random_source_value(self, source_column):
        return random.choice(self.source_data[self.get_data_source_from_column(source_column)][source_column])

    def get_data_source_from_column(self, source_column):
        data_source, _ = source_column.split('::')
        if data_source not in self.source_data:
            self.update_source_data(data_source)
        return data_source

    def get_correlated_source_values(self, source_column, correlated_columns):
        result = {}
        data_source = self.get_data_source_from_column(source_column)
        selection_index = random.randint(0, len(self.source_data[data_source][source_column])-1)
        for column in correlated_columns:
            result[column] = self.source_data[data_source][column][selection_index]
        result[source_column] = self.source_data[data_source][source_column][selection_index]
        return result

    def output_csv(self):
        with open(self.filename, 'wb') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.output_columns.values())
            csv_writer.writeheader()
            for i in xrange(self.record_count):
                csv_writer.writerow(self.generate_row())

    def update_source_data(self, source):
        filename = self.config_parser.get(source, 'filename')
        source_type = self.config_parser.get(source, 'type')
        self.source_data.input_source_file(filename, source, source_type)

    def get_output_column_name(self, column):
        if self.config_parser.has_option('column', 'output_name'):
            return self.config_parser.get('column', 'output_name')
        else:
            return column.split("::")[1]


def clean_comma_split( string_to_split, delim=','):
    return [col.strip() for col in string_to_split.split(delim)]


if __name__ == '__main__':
    config = ConfigurationSettings('data_generator.conf').config
    records = clean_comma_split(config.get('default', 'records'))
    source_init = SourceData()
    for record in records:
        record_generator = DataGenerator(record, config, source_init)
        record_generator.output_csv()
