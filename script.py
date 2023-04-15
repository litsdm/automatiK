from fastapi.testclient import TestClient
from modules.script_callbacks import on_app_started

import shared

def set_client(block, app):
    shared.client = TestClient(app)

on_app_started(set_client)