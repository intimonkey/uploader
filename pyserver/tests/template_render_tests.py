import os
import json
import uuid
import unittest
from pyserver.core import *

TEST_HELLO = """Hello, {{name}}"""
TEST_HELLO_JSON = """{\"message\": "Hello, {{name}}"}"""
TEST_TEMPLATES = [
        dict(name="hello.html", content=TEST_HELLO),
        dict(name="hello.json", content=TEST_HELLO_JSON),
        ]


class TemplateRenderTestFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for template in TEST_TEMPLATES:
            with open(os.path.join("./templates", template['name']), 'w') as out_file:
                out_file.write(template['content'])

    @classmethod
    def tearDownClass(cls):
        for template in TEST_TEMPLATES:
            os.unlink(os.path.join("./templates", template['name']))

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_cache = app.config['_CACHE']
        self.app.debug = True
    
    def tearDown(self):
        app.config['_CACHE'] = self.app_cache

    def test_return_unrendered_template(self):
        r = self.app.get("/raw_template/hello.html")
        self.assertEquals(200, r.status_code)
        self.assertEquals(TEST_HELLO, r.data)

    def test_html_template_no_data(self):
        r = self.app.post("/render/hello.html")
        self.assertEquals(200, r.status_code)
        self.assertEquals("Hello, ", r.data)

    def test_html_template_with_data(self):
        r = self.app.post("/render/hello.html", data=dict(name="pants"))
        self.assertEquals(200, r.status_code)
        self.assertEquals("Hello, pants", r.data)

    def test_html_template_with_callback(self):
        request_data=dict(name="pants", callback="function_name")
        r = self.app.post("/render/hello.html", data=request_data)
        self.assertEquals(200, r.status_code)
        self.assertEquals("application/json", r.content_type)
        self.assertEquals("function_name(\"Hello, pants\")", r.data)

    def test_json_template_no_data(self):
        r = self.app.post("/render/hello.json")
        self.assertEquals(200, r.status_code)
        jr = json.loads(r.data)
        self.assertTrue(jr)
        self.assertEquals("application/json", r.content_type)
        self.assertEquals("Hello, ", jr['message'])

    def test_json_template_with_data(self):
        r = self.app.post("/render/hello.json", data=dict(name="pants"))
        self.assertEquals(200, r.status_code)
        jr = json.loads(r.data)
        self.assertTrue(jr)
        self.assertEquals("application/json", r.content_type)
        self.assertEquals("Hello, pants", jr['message'])

    def test_json_template_with_callback(self):
        request_data=dict(name="pants", callback="function_name")
        r = self.app.post("/render/hello.json", data=request_data)
        self.assertEquals(200, r.status_code)
        self.assertEquals("application/json", r.content_type)
        self.assertEquals("function_name({\"message\": \"Hello, pants\"})", r.data)
