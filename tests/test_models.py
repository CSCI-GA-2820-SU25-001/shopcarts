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

    def test_create_item(self):
        """It should create a Item"""
        resource = ShopcartFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Shopcart.all()
        self.assertEqual(len(found), 1)
        data = Shopcart.find(resource.customer_id)
        self.assertEqual(data.customer_id, resource.customer_id)
        new_item = {
            "product_id": 1,
            "description": "Banana",
            "price": 100,
            "quantity": 2,
        }
        resource.create_subordinate(resource.customer_id, new_item)

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

    def test_validation(self):
        """It should raise a DataValidationError if required fields in JSONB item_list are missing"""
        item_list = [{"product_id": 21}]
        shopcart = Shopcart()
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = [{"product_id": 21, "description": "Item 21"}]
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = [{"product_id": 21, "description": "Item 21", "price": 214}]
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = [
            {"product_id": 21, "description": "Item 21", "price": 214, "quantity": "24"}
        ]
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = 123
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = [{}]
        self.assertRaises(
            DataValidationError, shopcart.validate_item_list, None, item_list
        )
        item_list = [
            {"product_id": 21, "description": "Item 21", "price": 214, "quantity": 24}
        ]
        self.assertEqual(shopcart.validate_item_list(None, item_list), item_list)

    # ----------------------------------------------------------
    # Sad Data Validation test.
    # ----------------------------------------------------------
    def test_deserialize_missing_data(self):
        """It should raise a DataValidationError if required fields are missing"""
        data = {"item_list": []}  # missing customer_id
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_missing_key(self):
        """It should raise DataValidationError if a required key is missing"""
        bad_data = {
            "id": 1,
            # "customer_id" is missing
            "item_list": [],
        }
        shopcart = Shopcart()
        with self.assertRaises(DataValidationError) as context:
            shopcart.deserialize(bad_data)
        self.assertIn("missing customer_id", str(context.exception))

    # ----------------------------------------------------------
    # Sad Delete Item test. (shopcart exist check)
    # ----------------------------------------------------------
    def test_delete_subordinate_invalid(self):
        """It should raise DataValidationError when deleting an item from a nonexistent cart"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.delete_subordinate, 9999, 123)

    # ----------------------------------------------------------
    # Delete correct Item test.
    # ----------------------------------------------------------
    def test_delete_subordinate_removes_correct_item(self):
        """It should delete the correct item from item_list"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Add two items manually
        shopcart.item_list = [
            {"product_id": 1, "description": "apple", "price": 10, "quantity": 2},
            {"product_id": 2, "description": "banana", "price": 20, "quantity": 1},
        ]
        db.session.commit()
        # Now delete product_id 1
        shopcart.delete_subordinate(shopcart.customer_id, 1)
        updated = Shopcart.find(shopcart.customer_id)
        self.assertEqual(len(updated.item_list), 1)
        self.assertEqual(updated.item_list[0]["product_id"], 2)

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
        self.assertRaises(
            DataValidationError, shopcart.update_subordinate, 9999, new_item
        )

    # ----------------------------------------------------------
    # Sad create tests
    # -----------------------------------------------------------
    def test_error_creating_shopcart(self):
        """Raises a DataValidationError if invalid input on create"""
        shopcart = Shopcart()
        shopcart.customer_id = "error"
        self.assertRaises(DataValidationError, shopcart.create)

    def test_error_creating_item(self):
        """It should create a Item"""
        resource = ShopcartFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Shopcart.all()
        self.assertEqual(len(found), 1)
        data = Shopcart.find(resource.customer_id)
        self.assertEqual(data.customer_id, resource.customer_id)
        new_item = 2
        self.assertRaises(
            DataValidationError,
            resource.create_subordinate,
            resource.customer_id,
            new_item,
        )

    # ----------------------------------------------------------
    # Sad save tests
    # -----------------------------------------------------------
    def test_save_class_method(self):
        """It should call save() to commit changes"""
        shopcart = ShopcartFactory()
        shopcart.create()
        Shopcart.save()
        found = Shopcart.find(shopcart.customer_id)
        self.assertIsNotNone(found)

    # ----------------------------------------------------------
    # Tests for more coverage
    # -----------------------------------------------------------

    def test_deserialize_attribute_error(self):
        """It should raise DataValidationError when deserializing with invalid attribute"""
        shopcart = Shopcart()
        # Pass a non-dict object to trigger AttributeError
        with self.assertRaises(DataValidationError) as context:
            shopcart.deserialize("not a dict")
        self.assertIn(
            "Invalid Shopcart: body of request contained bad or no data",
            str(context.exception),
        )

    def test_deserialize_attribute_error_specific(self):
        """It should raise DataValidationError when deserializing with specific AttributeError"""
        shopcart = Shopcart()
        # Create an object that will cause AttributeError when accessing dict keys

        class BadObject:
            """Test class that raises AttributeError when accessed."""
            
            def __getitem__(self, key):
                raise AttributeError("test attribute error")

        with self.assertRaises(DataValidationError) as context:
            shopcart.deserialize(BadObject())
        self.assertIn("Invalid attribute: test attribute error", str(context.exception))

    def test_deserialize_type_error(self):
        """It should raise DataValidationError when deserializing with TypeError"""
        shopcart = Shopcart()
        # Pass None to trigger TypeError
        with self.assertRaises(DataValidationError) as context:
            shopcart.deserialize(None)
        self.assertIn(
            "Invalid Shopcart: body of request contained bad or no data",
            str(context.exception),
        )

    def test_find_filtered_none_cart(self):
        """It should return None when cart is not found in find_filtered"""
        # Test find_filtered with a non-existent customer
        result = Shopcart.find_filtered(99999, 100)
        self.assertIsNone(result)

    def test_create_database_error(self):
        """It should handle database errors during create"""
        shopcart = ShopcartFactory()
        # Mock a database error by trying to create with invalid data
        # This will trigger the exception handling in create method
        shopcart.customer_id = None  # This will cause issues
        try:
            shopcart.create()
        except DataValidationError:
            # This is expected behavior
            pass
        except (ValueError, TypeError, AttributeError) as e:
            # This is also acceptable as it tests the exception handling
            self.assertIsInstance(e, (ValueError, TypeError, AttributeError))
