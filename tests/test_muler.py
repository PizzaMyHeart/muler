import os


import pytest
from muler.app import search, create_app
import sqlite3



@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'DATABASE': 'test.db'})

    os.close('test.db')



