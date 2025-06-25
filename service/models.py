"""
Models for Shopcart

All of the models are stored in this module
"""

import logging
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

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
    item_list = db.Column(JSONB)

    def __repr__(self):
        return f"<Shopcart {self.customer_id} item_list={self.item_list}>"

    def create(self):
        """
        Creates a Shopcart to the database
        """
        logger.info("Creating shopcart for %d", self.customer_id)
        self.id = None  # pylint: disable=invalid-name
        self.item_list = []
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
        logger.info(
            "Creating product %d for %d 's shopcart", data.product_id, self.customer_id
        )
        try:
            self.deserialize(
                db.session.query(self).filter_by(customer_id=customer_id).first()
            )
            self.item_list.append(data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(
                "Error creating record for customer %d : %s", self.customer_id, data
            )
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Shopcart to the database
        """
        logger.info("Saving shopcart for %d", self.customer_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Shopcart from the data store"""
        logger.info("Deleting shopcart for %s", self.customer_id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Shopcart into a dictionary"""
        return {"customer_id": self.customer_id, "item_list": self.item_list}

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
        return cls.query.session.filter_by(customer_id=by_id).first()
