import sys
import os
import argparse
import hashlib
import csv

BUF_SIZE = 65536

class DoNotReplaceAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not getattr(namespace, self.dest):
            setattr(namespace, self.dest, values)

def GetFilesFromCsv(path):
    files = {}
    with open(path) as csvr:
        reader = csv.DictReader(csvr)
        for row in reader:
            row['items'] = row['items'].split(';')
            files[row['hash']] = {'count':row['count'],'duplicate_size':row['duplicate_size'],'items':row['items']}
    return files
def GetFiles(path,recurse=True):
    files = {}
    for item in os.scandir(path):
        if os.DirEntry.is_file(item):
            h = GetFileHash(item.path)
            if h in files:
                files[h]['items'] += [item.path]
            else:
                files[h] = {'size': os.stat(
                    item.path).st_size, 'items': [item.path]}
        elif recurse:
            sub = GetFiles(item.path,True)
            for s in sub.keys():
                if s in files:
                    files[s]['items'] += sub[s]['items']
                else:
                    files[s] = sub[s]
    return files

def GetFileHash(file):
    sha = hashlib.sha1()
    try:
        with open(file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha.update(data)
    except PermissionError as err:
        sha.update(str(err).encode('utf-8'))
    return sha.hexdigest()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find duplicate files in a given path, and optionally delete them.')
    group_source = parser.add_mutually_exclusive_group(required=True)
    group_source.add_argument('path', help='The path to search for duplicates.',
                        nargs='?', action=DoNotReplaceAction)
    group_source.add_argument(
        '-p', '--path', help='The path to search for duplicates.')
    group_source.add_argument(
        '-i', '--import-csv', help='Import file list from a Csv export (useful for subsequent delete).',dest='csvfile')
    parser.add_argument(
        '-o', '--output-file', help='The path to store the results.',default=None,dest='output')
    parser.add_argument('-d','--delete-duplicates', help='Delete all subseqent occurrences of the file after the first one.',default=None,dest='delete',action='store_true')
    group_recurse = parser.add_mutually_exclusive_group(required=False)
    group_recurse.add_argument(
        '-r', '--recursive', help='Search recursively through the path.', dest='recursive', action='store_true')
    group_recurse.add_argument(
        '-n', '--no-recursive', help='Search recursively through the path.', dest='recursive', action='store_false')
    parser.set_defaults(recursive=True)
    args = parser.parse_args()
    if args.path:
        search_path = args.path
        recursive_search = args.recursive
        stats = GetFiles(search_path,recursive_search)
        dups = {k: {'count': len(stats[k]['items']), 'items': stats[k]['items'], 'duplicate_size': (stats[k]['size']-1)*len(stats[k]['items'])} for k, v in stats.items() if len(stats[k]['items']) > 1}
    else:
        dups = GetFilesFromCsv(args.csvfile)
    if args.output:
        with open(args.output,'w') as o:
            o.write('hash,count,duplicate_size,items\n')
            for k, v in dups.items():
                o.write('{0},{1},{2},{3}\n'.format(
                    k, v['count'], v['duplicate_size'], ';'.join(v['items'])))
    else:
        print('hash','count','duplicate_size','items')
        for k,v in dups.items():
            print('{0},{1},{2},{3}'.format(k,v['count'],v['duplicate_size'],';'.join(v['items'])))
    if args.delete:
        for k,v in dups.items():
            if int(v['duplicate_size'])>100000:
                for f in v['items'][1:]:
                    print("Deleting duplicate file: {0}".format(f))
                    try:
                        os.remove(f)
                    except:
                        pass
