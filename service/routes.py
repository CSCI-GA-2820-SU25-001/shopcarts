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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
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

    # Todo: uncomment when get_shopcarts is implemented
    # location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)
    location_url = "unknown"
    return jsonify(shopcart.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcarts(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to Delete a shopcart with id [%s]", shopcart_id)

    # Delete the Shopcart if it exists
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        app.logger.info("Shopcart with ID: %d found.", shopcart.id)
        shopcart.delete()

    app.logger.info("Shopcart with ID: %d delete complete.", shopcart_id)
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
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to Update a shopcart with id [%s]", shopcart_id)
    check_content_type("application/json")

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{shopcart_id}' was not found.")

    # Update the Shopcart with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    shopcart.deserialize(data)

    # Save the updates to the database
    shopcart.update()

    app.logger.info("Shopcart with ID: %d updated.", shopcart.id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK