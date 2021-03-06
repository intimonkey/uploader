#! /usr/bin/env python
import os
from os import path
from flask import Flask, request, redirect, url_for
from flask import render_template
from flask import Response
from werkzeug import secure_filename
from argparse import ArgumentParser
from pyserver.core import app

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', './files/')
# a list of partitions that we're reserving for our own use
# not using dl
app.config['RESERVED_PARTITIONS'] = ['list', 'dl']

def partition_path(partition_name):
    partition_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            partition_name)
    if not os.path.exists(partition_path):
        os.makedirs(partition_path)
    return partition_path


def file_path_for_partition(file_name, partition_name):
    dp = partition_path(partition_name)
    fp = os.path.join(
            dp,
            file_name)
    return fp

def is_uploaded_file(file_path):
    fp = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
    if os.path.isfile(fp):
        return fp
    return None

@app.route('/<path:root_partition>', methods=['POST'])
def upload_file(root_partition):
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            fp = file_path_for_partition(filename, root_partition)
            if os.path.exists(fp):
               return render_template("exists.html"), 409 
            file.save(fp)
            return list_contents(root_partition)

@app.route('/<path:root_partition>', methods=['GET'])
def download_file(root_partition):
    requested_file = is_uploaded_file(root_partition)
    if requested_file:
        # if the user is requesting a file that exists... give it to them
        def generate_file():
            with open(requested_file, 'r') as fp:
                yield fp.read(4096)
        return Response(generate_file(), mimetype='application/octet-stream')
    else:
        return render_template("submit.html")

@app.route('/list/<path:root_partition>', methods=['GET'])
def list_contents(root_partition):
    pp = partition_path(root_partition)
    file_names = os.listdir(pp)
    return render_template("ls.html", partition=root_partition, files=file_names)

if __name__ == "__main__":
    arg_parser = ArgumentParser(description="personal log server")
    arg_parser.add_argument("action", choices=('start', 'test'),
        help="action to be performed")
    args = arg_parser.parse_args()

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if args.action == "start":
        app.run(debug=True)
    elif args.action == "test":
        import sys
        import unittest
        import uuid
        from StringIO import StringIO
        uid = lambda: str(uuid.uuid4())
        # unit test uses args too.... so remove ours
        sys.argv.pop()
        class TestFixture(unittest.TestCase):
            def setUp(self):
                app.config['TESTING'] = True
                self.app = app.test_client()

            def test_app_exists(self):
                self.assertTrue(self.app)
        
            def test_file_upload(self):
                pid = uid()
                fn = 'file_%s.txt' % (uid())
                r = self.app.post('/%s' % (pid),
                    data={'file': (StringIO('my file contents'), fn)})
                self.assertEquals(200, r.status_code)
                self.assertTrue(fn in r.data)
                # does it come back when requested
                r = self.app.get('/%s/%s' % (pid, fn))
                self.assertTrue('my file contents' in r.data)
                
            def test_duplicate_file_upload(self):
                pid = uid()
                fn = 'file_%s.txt' % (uid())
                r = self.app.post('/%s' % (pid),
                    data={'file': (StringIO('my file contents'), fn)})
                self.assertEquals(200, r.status_code)
                r = self.app.post('/%s' % (pid),
                    data={'file': (StringIO('my file contents'), fn)})
                self.assertEquals(409, r.status_code)
        
            def test_non_existant_partition(self):
                """ this should always return a 200 even if there's nothing there """
                pid = uid()
                r = self.app.get("/list/%s" % (pid)) 
                self.assertEquals(200, r.status_code)
                self.assertTrue(pid in r.data)
        
        unittest.main()
        print("running tests")
