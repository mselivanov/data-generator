"""
Module contains code for implementing mock HTTP server
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
import requests
import re
import json

class MockHTTPServerRequestHandler(BaseHTTPRequestHandler):
    _response_mappings = {"GET":{}, "POST":{}, "PUT":{}}
    _request_mappings = {"GET":{}, "POST":{}, "PUT":{}}

    @classmethod
    def get_request(cls, verb, path):
        """
        Returns list of objects sent in request body
        """
        return cls._request_mappings[verb][path]

    @classmethod
    def find_response_mapping(cls, verb, path):
        keys = sorted(cls._response_mappings[verb].keys(), key=lambda k: -len(k))
        for key in keys:
            m = re.search(key, path)
            if m:
                return cls._response_mappings[verb][key]
        return None

    @classmethod
    def set_mock_response(cls, verb, mock_response):
        cls._response_mappings[verb].update(mock_response)

    @classmethod
    def register_request(cls, verb, path, body):
        if path not in cls._request_mappings[verb]:
            cls._request_mappings[verb][path] = {}
        if not cls._request_mappings[verb][path]:
            cls._request_mappings[verb][path] = []
        cls._request_mappings[verb][path].append(body)

    def save_request(self):
        content_len = int(self.headers.get('content-length', 0))
        MockHTTPServerRequestHandler.register_request(self.command, self.path, self.rfile.read(content_len).decode(encoding="utf-8"))

    def send_mock_response(self, mapping):
        status = mapping["status"]
        headers = mapping["headers"]
        body = mapping["body"]
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def execute_mock_workflow(self):
        self.save_request()
        mapping = MockHTTPServerRequestHandler.find_response_mapping(self.command, self.path)
        if not mapping:
            raise ValueError("Mapping for verb '{0}' and path {1} is not found"\
                             .format(self.command, self.path))
        self.send_mock_response(mapping)
        return

    def do_GET(self):
        self.execute_mock_workflow()

    def do_POST(self):
        self.execute_mock_workflow()

class MockHTTPServer(object):

    @staticmethod
    def get_free_port():
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        address, port = s.getsockname()
        s.close()
        return port

    @classmethod
    def start_server(cls):
        cls.mock_server = HTTPServer(("localhost", cls.mock_server_port), \
               MockHTTPServerRequestHandler)
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()
        print("Server started on port: {0}".format(cls.mock_server_port))

    @classmethod
    def setup(cls):
        cls.mock_server_port = MockHTTPServer.get_free_port()

