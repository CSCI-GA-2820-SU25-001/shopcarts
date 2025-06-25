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
Shopcart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcart
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart
from service.common import status  # HTTP Status Codes


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify({"message": "Shopcart API root url"}),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Create a Shopcart
    This endpoint will create a Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to Create a Shopcart...")
    check_content_type("application/json")

    shopcart = Shopcart()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)

    # Save the new Shopcart to the database
    shopcart.create()
    app.logger.info("Shopcart with new id [%s] saved!", shopcart.id)

    # Return the location of the new Shopcart

    location_url = url_for("create_shopcarts", shopcart_id=shopcart.id, _external=True)
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# CREATE A NEW ITEM IN SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items", methods=["POST"])
def create_shopcarts_item(customer_id):
    """
    Create a Shopcart item
    This endpoint will create a Shopcart item based the data in the body that is posted
    """
    app.logger.info("Request to Create a Shopcart item...")
    check_content_type("application/json")

    shopcart = Shopcart()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)

    # Save the new Shopcart to the database
    shopcart.create_subordinate(customer_id, data)
    app.logger.info("Shopcart item with new id saved!")

    # Return the location of the new Shopcart

    location_url = url_for(
        "create_shopcarts_item", customer_id=customer_id, _external=True
    )
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def get_all_shopcarts():
    """
    Retrieve all Shopcart

    This endpoint will return all entries in the database
    """
    app.logger.info("Request to Retrieve all shopcarts")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.all()
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            "No user has any active shopcarts",
        )

    app.logger.info("Returning shopcarts: %s", shopcart)
    return jsonify([x.serialize() for x in shopcart]), status.HTTP_200_OK


######################################################################
# LIST ALL SHOPCART ITEMS
######################################################################
@app.route("/shopcarts/<int:customer_id>/items", methods=["GET"])
def get_all_shopcarts_items(customer_id):
    """
    Retrieve all Shopcart items

    This endpoint will return all entries in the database
    """
    app.logger.info("Request to Retrieve all shopcart items for customer")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(customer_id)
    if not shopcart or len(shopcart.item_list) == 0:
        abort(
            status.HTTP_404_NOT_FOUND,
            "User has no shop cart available",
        )

    app.logger.info("Returning shopcart items: %s", shopcart)
    return jsonify(shopcart.item_list), status.HTTP_200_OK


######################################################################
# READ A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["GET"])
def get_shopcarts(customer_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request to Retrieve a shopcart with customer id [%s]", customer_id)
    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(customer_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart for customer '{customer_id}' was not found.",
        )

    app.logger.info("Returning shopcart: %s", shopcart.customer_id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# READ AN INDIVIDUAL ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["GET"])
def get_shopcarts_item(customer_id, product_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request to Retrieve a shopcart with customer id [%s]", customer_id)

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(customer_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart for customer '{customer_id}' was not found.",
        )
    item_list = shopcart.item_list
    for item in item_list:
        if item["product_id"] == product_id:
            app.logger.info("Returning shopcart: %s", shopcart.customer_id)
            return jsonify(item), status.HTTP_200_OK

    abort(
        status.HTTP_404_NOT_FOUND,
        f"Product '{product_id}' was not found in cart.",
    )


######################################################################
# DELETE AN ITEM FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["DELETE"])
def delete_shopcarts_item(customer_id, product_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info(
        "Request to Delete a shopcart item [%d] for customer [%d]",
        product_id,
        customer_id,
    )

    # Delete the Shopcart if it exists
    shopcart = Shopcart.find(customer_id)
    if shopcart:
        app.logger.info("Shopcart for customer: %d found.", customer_id)
        shopcart.delete_subordinate(customer_id, product_id)
    else:
        app.logger.info("Shopcart for customer: %d found.", customer_id)
    app.logger.info("Shopcart with ID: %d delete complete.", customer_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["DELETE"])
def delete_shopcarts(customer_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to Delete a shopcart with id [%d]", customer_id)

    # Delete the Shopcart if it exists
    shopcart = Shopcart.find(customer_id)
    if shopcart:
        app.logger.info("Shopcart for customer: %d found.", shopcart.id)
        shopcart.delete()
    else:
        app.logger.info("Shopcart for customer: %d not found.", customer_id)

    app.logger.info("Shopcart with customer ID: %d delete complete.", customer_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["PUT"])
def update_shopcarts(customer_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to Update a shopcart for customer [%d]", customer_id)
    check_content_type("application/json")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(customer_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart for customer '{customer_id}' was not found.",
        )

    # Update the Shopcart with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)

    # Save the updates to the database
    shopcart.update(customer_id, data)

    app.logger.info("Shopcart for customer %d updated.", customer_id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE INDIVIDUAL ITEM IN SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["PUT"])
def update_shopcarts_item(customer_id, product_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info(
        "Request to Update a shopcart item [%d] for customer [%d]",
        product_id,
        customer_id,
    )
    check_content_type("application/json")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(customer_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart for customer '{customer_id}' was not found.",
        )

    # Update the Shopcart with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)

    # Save the updates to the database
    shopcart.update_subordinate(customer_id, data)

    app.logger.info("Shopcart for customer %d updated.", customer_id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK
