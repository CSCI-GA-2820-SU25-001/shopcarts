######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Shopcart, DataValidationError, db
from .factories import ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Shopcart   M O D E L   T E S T   C A S E S
######################################################################

# pylint: disable=too-many-public-methods
class TestShopcart(TestCase):
    """Test Cases for Shopcart Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create(self):
        """It should create a Shopcart"""
        resource = ShopcartFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Shopcart.all()
        self.assertEqual(len(found), 1)
        data = Shopcart.find(resource.customer_id)
        self.assertEqual(data.customer_id, resource.customer_id)

    def test_delete(self):
        """It should delete created shopcart"""
        resource = ShopcartFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Shopcart.all()
        self.assertEqual(len(found), 1)
        resource.delete()
        found = Shopcart.all()
        self.assertEqual(len(found), 0)

    def test_update(self):
        """It should update created shopcart"""
        resource = ShopcartFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        data = Shopcart.find(resource.customer_id)
        original_id = resource.customer_id
        data.customer_id = 44
        db.session.commit()
        found = Shopcart.find(original_id)
        self.assertIsNone(found)
        found = Shopcart.find(44)
        self.assertEqual(len(found.all()), 1)
    
    # ----------------------------------------------------------
    # Sad Data Validation test.
    # ----------------------------------------------------------
    def test_deserialize_missing_data(self):
        """It should raise a DataValidationError if required fields are missing"""
        data = {"item_list": []}  # missing customer_id
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    # ----------------------------------------------------------
    # Sad Delete Item test.
    # ----------------------------------------------------------
    def test_delete_subordinate_invalid(self):
        """It should raise DataValidationError when deleting an item from a nonexistent cart"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.delete_subordinate, 9999, 123)

    # ----------------------------------------------------------
    # Sad Delete shopcart test
    # -----------------------------------------------------------
    def test_delete_invalid_shopcart(self):
        """It should raise DataValidationError when deleting a shopcart with no ID"""
        shopcart = Shopcart(id=9999)
        self.assertRaises(DataValidationError, shopcart.delete)

    # ----------------------------------------------------------
    # Sad Update shopcart test
    # -----------------------------------------------------------
    def test_update_invalid_shopcart(self):
        """It should raise DataValidationError when updating a nonexistent shopcart"""
        shopcart = Shopcart()
        updated_data = [
            {"product_id": 1, "description": "Item", "price": 50, "quantity": 1}
        ]
        self.assertRaises(DataValidationError, shopcart.update, 9999, updated_data)

    # ----------------------------------------------------------
    # Sad Update item test (shopcart does not exist)
    # -----------------------------------------------------------
    def test_update_subordinate_invalid_shopcart(self):
        """It should raise DataValidationError when updating an item in nonexistent cart"""
        shopcart = Shopcart()
        new_item = {"product_id": 99, "description": "X", "price": 50, "quantity": 2}
        self.assertRaises(DataValidationError, shopcart.update_subordinate, 9999, new_item)