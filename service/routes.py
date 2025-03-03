"""
Wishlist

Describe what your service does here
"""

from flask import jsonify, request, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Wishlist, WishlistItem

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

######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create an Wishlist based on the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")

    # Validate content is json
    check_content_type("application/json")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()  # match test case

    return make_response(
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": f"/wishlists/{wishlist.id}"},
    )


######################################################################
# READ A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def read_wishlists(wishlist_id):
    """
    Reads an Existing Wishlist
    This endpoint will read a Wishlist based on the given id
    """
    app.logger.info("Request to read Wishlist: %d", wishlist_id)

    # Validate content is json
    check_content_type("application/json")

    # Check if wishlist exists
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# LIST ALL WISHLISTs
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
    app.logger.info("Request for Wishlist list")
    wishlists = Wishlist.all()
    # Return as an array of dictionaries
    results = [wishlist.serialize() for wishlist in wishlists]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# DELETE A NEW WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", wishlist_id)

    # Retrieve the account to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    else:
        return make_response("", status.HTTP_404_NOT_FOUND)

    return make_response("", status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
#                W I S H L I S T   I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# CREATE A NEW WISHLIST ITEM
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["POST"])
def create_wishlist_item(wishlist_id):
    """
    Creates a Wishlist Item and associates it with a specific Wishlist
    This endpoint will create a Wishlist Item based on the data in the request body
    and associate it with the specified Wishlist.
    """
    app.logger.info("Request to create a Wishlist Item")

    # Validate content is JSON
    check_content_type("application/json")

    # Find the specified Wishlist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with ID {wishlist_id} not found")

    # Create the Wishlist Item
    wishlist_item = WishlistItem()
    wishlist_item.deserialize(request.get_json())
    wishlist_item.wishlist_id = (
        wishlist.id
    )  # Associate the item with the specified wishlist

    # Append items to the wishlist
    wishlist.items.append(wishlist_item)
    wishlist.update()

    # Create a message to return
    message = wishlist_item.serialize()

    return make_response(
        jsonify(message),
        status.HTTP_201_CREATED,
        {"Location": f"/wishlists/{wishlist.id}/items/{wishlist_item.id}"},
    )


######################################################################
# LIST ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items", methods=["GET"])
def list_wishlist_items(wishlist_id):
    """Returns all of the Items for a Wishlist"""
    app.logger.info(
        "Request for all WishlistItems for Wishlist with id: %s", wishlist_id
    )

    # See if the account exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get the items for the wishlist
    results = [item.serialize() for item in wishlist.items]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# DELETE ITEMS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
def delete_addresses(wishlist_id, item_id):
    """
    Delete an Item

    This endpoint will delete an Item based the id specified in the path
    """

    app.logger.info(
        "Request to delete Item %s for Wishlist id: %s", item_id, wishlist_id
    )

    # See if the address exists and delete it if it does
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    else:
        return make_response("", status.HTTP_404_NOT_FOUND)

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
