"""
Models for Shopcart

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import validates

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Shopcart(db.Model):
    """
    Class that represents a Shopcart
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    item_list = db.Column(MutableList.as_mutable(JSONB), default=list)

    @validates("item_list")
    def validate_item_list(self, key, value):
        """
        Validates sub-fields of item_list JSONB Array
        """
        logger.info("Item List key %s:", key)
        if not isinstance(value, list):
            raise DataValidationError(
                Exception("Column 'item_list' must be of type: List []")
            )

        for item in value:
            if "product_id" not in item or not isinstance(item["product_id"], int):
                raise DataValidationError(
                    Exception("Field 'product_id' of type: Integer expected")
                )
            if "description" not in item or not isinstance(item["description"], str):
                raise DataValidationError(
                    Exception("Field 'description' of type: String expected")
                )
            if "price" not in item or not isinstance(item["price"], int):
                raise DataValidationError(
                    Exception("Field 'price' of type: Integer expected")
                )
            if "quantity" not in item or not isinstance(item["quantity"], int):
                raise DataValidationError(
                    Exception("Field 'quantity' of type: Integer expected")
                )

        return value

    def __repr__(self):
        return f"<Shopcart {self.customer_id} item_list={self.item_list}>"

    def create(self):
        """
        Creates a Shopcart to the database
        """
        if not self.customer_id:
            self.customer_id = 33
        logger.info("Creating shopcart for %d", self.customer_id)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def create_subordinate(self, customer_id, data):
        """
        Creates an item to the Shopcart item_list
        """
        try:
            logger.info(
                "Creating product %d for %d 's shopcart",
                data["product_id"],
                customer_id,
            )
            cart = self.find(customer_id)
            cart.item_list.append(data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error creating record for customer %d : %s", customer_id, data
            )
            raise DataValidationError(e) from e

    def update(self, customer_id, data):
        """
        Updates a Shopcart of a customer in the database
        """
        logger.info("Updating shopcart for %d", customer_id)
        try:
            cart = self.find(customer_id)
            cart.item_list = data
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def update_subordinate(self, customer_id, data):
        """
        Updates a Shopcart item of a customer in the database
        """
        logger.info("Updating shopcart item %d for %d", data["product_id"], customer_id)
        try:
            cart = self.find(customer_id)
            newlist = []
            for item in cart.item_list:
                if item["product_id"] == data["product_id"]:
                    newlist.append(data)
                else:
                    newlist.append(item)
            cart.item_list = newlist
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Shopcart from the data store"""
        logger.info("Deleting shopcart for customer %s", self.customer_id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def delete_subordinate(self, customer_id, product_id):
        """Removes a Shopcart from the data store"""
        logger.info("Deleting shopcart for customer %s", customer_id)
        try:
            cart = self.find(customer_id)
            newlist = []
            for item in cart.item_list:
                if item["product_id"] == product_id:
                    continue
                newlist.append(item)
            cart.item_list = newlist
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Shopcart into a dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "item_list": self.item_list,
        }

    def deserialize(self, data):
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.item_list = data["item_list"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Shopcarts in the database"""
        logger.info("Processing all Shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Shopcart by customer ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.filter_by(customer_id=by_id).first()

    @classmethod
    def save(cls):
        """Saves the model state"""
        db.session.commit()
