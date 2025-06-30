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
TestShopcart API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Shopcart
from .factories import ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create shopcarts
    ############################################################
    def _create_shopcarts(self, count: int = 1) -> list:
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE SHOPCART
    # ----------------------------------------------------------

    def test_create_shopcart(self):
        """It should Create a new Shopcart"""
        test_shopcart = ShopcartFactory()
        logging.debug("Test Shopcart: %s", test_shopcart.serialize())
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = response.get_json()

        self.assertEqual(new_shopcart["customer_id"], test_shopcart.customer_id)
        self.assertEqual(new_shopcart["item_list"], test_shopcart.item_list)

        # Check that the location header was correct
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_id"], test_shopcart.customer_id)
        self.assertEqual(new_shopcart["item_list"], test_shopcart.item_list)

    def test_create_shopcart_subordinate(self):
        """It should Create a new Shopcart Item"""
        test_shopcart = ShopcartFactory()
        logging.debug("Test Shopcart: %s", test_shopcart.serialize())
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        customer_id = test_shopcart.customer_id
        new_item = {
            "product_id": 1,
            "description": "Banana",
            "price": 100,
            "quantity": 2,
        }

        response = self.client.post(
            f"{BASE_URL}/{customer_id}/items",
            json=new_item,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the location header was correct
        response = self.client.get(f"{BASE_URL}/{customer_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_shopcart = response.get_json()
        self.assertEqual(new_shopcart["customer_id"], customer_id)
        self.assertEqual(
            new_shopcart["item_list"][0]["product_id"], new_item["product_id"]
        )

    # ----------------------------------------------------------
    # TEST READ SHOPCART
    # ----------------------------------------------------------
    def test_get_shopcart(self):
        """It should Get a single Shopcart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["customer_id"], test_shopcart.customer_id)

    def test_get_shopcart_not_found(self):
        """It should not Get a Shopcart thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST READ INDIVIDUAL ITEM IN SHOPCART
    # ----------------------------------------------------------
    def test_get_shopcart_item(self):
        """It should Get a single Shopcart item"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.customer_id}", json=new_list
        )
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}/items/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["price"], new_list[0]["price"])
        self.assertEqual(data["quantity"], new_list[0]["quantity"])
        self.assertEqual(data["description"], new_list[0]["description"])
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}/items/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["price"], new_list[1]["price"])
        self.assertEqual(data["quantity"], new_list[1]["quantity"])
        self.assertEqual(data["description"], new_list[1]["description"])

    def test_get_shopcart_item_not_found(self):
        """It should not Get a Shopcart item thats not found"""
        test_shopcart = self._create_shopcarts(1)[0]
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.customer_id}", json=new_list
        )
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST LIST ALL SHOPCARTS
    # ----------------------------------------------------------
    def test_get_all_shopcart(self):
        """It should Get all Shopcarts"""
        set_carts = self._create_shopcarts(2)
        set_carts = [i.serialize() for i in set_carts]
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data, set_carts)

    def test_get_all_shopcart_not_found(self):
        """It should not Get a Shopcart thats not found"""
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("No user has any active shopcarts", data["message"])

    # ----------------------------------------------------------
    # TEST LIST ALL SHOPCART ITEMS
    # ----------------------------------------------------------
    def test_get_all_shopcart_items(self):
        """It should Get all Shopcart item lists"""
        test_cart = self._create_shopcarts(1)[0]
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(f"{BASE_URL}/{test_cart.customer_id}", json=new_list)
        response = self.client.get(f"{BASE_URL}/{test_cart.customer_id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data, new_list)

    def test_get_all_shopcart_items_not_found(self):
        """It should not Get a Shopcart items_list thats not found"""
        test_cart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_cart.customer_id}/items")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("User has no shop cart available", data["message"])

    def test_get_all_shopcart_items_query_max_price(self):
        """It should Get all items in item list with lower price than query string"""
        test_cart = self._create_shopcarts(1)[0]
        test_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
            {"product_id": 3, "description": "Item 3", "price": 320, "quantity": 6},
            {"product_id": 4, "description": "Item 4", "price": 347, "quantity": 3},
        ]
        response = self.client.put(f"{BASE_URL}/{test_cart.customer_id}", json=new_list)
        response = self.client.get(
            f"{BASE_URL}/{test_cart.customer_id}/items?max-price=300"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered_shopcart = response.get_json()
        self.assertEqual(filtered_shopcart, test_list)

    def test_get_all_shopcart_items_query_max_price_not_found(self):
        """It should not get any items if none meet the max price criteria"""
        test_cart = self._create_shopcarts(1)[0]
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(f"{BASE_URL}/{test_cart.customer_id}", json=new_list)
        response = self.client.get(
            f"{BASE_URL}/{test_cart.customer_id}/items?max-price=100"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------------------------------------
    # TEST DELETE SHOPCART
    # ----------------------------------------------------------
    def test_delete_shopcart(self):
        """It should Delete a Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.customer_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_shopcart(self):
        """It should Delete a Shopcart even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # -----------------------------------------------------------
    # TEST DELETE SHOPCART ITEM
    # ----------------------------------------------------------
    def test_delete_shopcart_subordinate(self):
        """It should Delete a Shopcart Item"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_shopcart.item_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        db.session.commit()
        loc = f"{BASE_URL}/{test_shopcart.customer_id}/items/1"
        logging.debug(loc)
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.customer_id}/items/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_shopcart.customer_id}/items/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_shopcart_subordinate(self):
        """It should Delete a Shopcart Item even if it doesn't exist"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.customer_id}/items/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST UPDATE SHOPCART
    # ----------------------------------------------------------
    def test_update_shopcart(self):
        """It should Update an existing Shopcart"""
        # create a shopcart to update
        test_shopcart = ShopcartFactory()
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = response.get_json()
        logging.debug(new_shopcart)
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(
            f"{BASE_URL}/{new_shopcart['customer_id']}", json=new_list
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_shopcart = response.get_json()
        self.assertEqual(updated_shopcart["item_list"], new_list)

    # ----------------------------------------------------------
    # TEST UPDATE SHOPCART INDIVIDUAL ITEM
    # ----------------------------------------------------------
    def test_update_shopcart_subordinate(self):
        """It should Update an existing Shopcart item"""
        # create a shopcart to update
        test_shopcart = ShopcartFactory()
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = response.get_json()
        logging.debug(new_shopcart)
        new_list = [
            {"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2},
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        response = self.client.put(
            f"{BASE_URL}/{new_shopcart['customer_id']}", json=new_list
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_shopcart = response.get_json()
        self.assertEqual(updated_shopcart["item_list"], new_list)

        # update the shopcart item
        logging.debug(new_shopcart)
        new_list_item = {
            "product_id": 1,
            "description": "Bad item",
            "price": 20,
            "quantity": 5,
        }
        response = self.client.put(
            f"{BASE_URL}/{updated_shopcart['customer_id']}/items/{new_list_item['product_id']}",
            json=new_list_item,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_shopcart_2 = response.get_json()
        logging.debug(updated_shopcart_2["item_list"])
        expected = [
            {
                "product_id": 1,
                "description": "Bad item",
                "price": 20,
                "quantity": 5,
            },
            {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5},
        ]
        self.assertEqual(updated_shopcart_2["item_list"], expected)

    # ----------------------------------------------------------
    # TEST SAD PATH
    # ----------------------------------------------------------

    def test_invalid_method(self):
        """Invalid method raises error"""
        response = self.client.delete(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_media(self):
        """Invalid data raises error"""
        response = self.client.post(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_invalid_path(self):
        """Invalid path raises error"""
        response = self.client.post(
            f"{BASE_URL}", data="", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
