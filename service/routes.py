"""
Wishlist

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Wishlist

# Import Flask application
from . import app


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

# Place your REST API code here ...


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlist", methods=["POST"])
def create_wishlists():
    """
    Creates an Wishlist
    This endpoint will create an Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()  # match test case

    return make_response(
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": f"/wishlist/{wishlist.id}"},
    )
