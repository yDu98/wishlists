"""
Test cases for Wishlist Model

"""
import os
import logging
import unittest
from datetime import datetime
from service import app
from service.models import Wishlist, WishlistItem, DataValidationError, db
from tests.factories import WishlistFactory, WishlistItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(unittest.TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Wishlist.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()
        # db.drop_all() #Drops all tables if needed for updating schema

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_define_a_wishlist(self):
        """It should Define a Wishlist and assert that it is correct"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            customer_id=fake_wishlist.customer_id,
            wishlist_name=fake_wishlist.wishlist_name,
            created_date=fake_wishlist.created_date,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)
        self.assertEqual(wishlist.wishlist_name, fake_wishlist.wishlist_name)
        self.assertEqual(wishlist.created_date, fake_wishlist.created_date)

    def test_create_a_wishlist(self):
        """It should Create a Wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Second addition
        wishlist = WishlistFactory()
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 2)

    def test_read_wishlist(self):
        """It should Read a Wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(found_wishlist.wishlist_name, wishlist.wishlist_name)
        self.assertEqual(found_wishlist.created_date, wishlist.created_date)

    def test_update_wishlist(self):
        """It should Update a Wishlist"""

        # Define names
        old_name = "change name"
        new_name = "different name"
        self.assertNotEqual(old_name, new_name)

        wishlist = WishlistFactory(wishlist_name=old_name)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(wishlist.wishlist_name, old_name)

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        wishlist.wishlist_name = new_name
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.wishlist_name, new_name)

    def test_delete_an_wishlist(self):
        """It should Delete a Wishlist from the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        last_id = wishlist.id
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        wishlist = wishlists[0]
        self.assertEqual(wishlist.id, last_id)
        # Second Wishlist
        wishlist_2 = WishlistFactory()
        wishlist_2.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist_2.id)
        self.assertNotEqual(wishlist_2.id, last_id)
        last_id_2 = wishlist_2.id
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 2)
        # Delete first wishlist
        wishlist.delete()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        wishlists_found = Wishlist.find(last_id)
        self.assertIsNone(wishlists_found)
        # Verify second wishlist exists
        wishlists_found = Wishlist.find(last_id_2)
        self.assertIsNotNone(wishlists_found)
        # Delete second wishlist
        wishlist_2.delete()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 0)
        wishlists_found = Wishlist.find(last_id_2)
        self.assertIsNone(wishlists_found)

    def test_list_all_wishlists(self):
        """It should List all Wishlists in the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        for wishlist in WishlistFactory.create_batch(5):
            wishlist.create()
        # Assert that there are now 5 wishlists in the database
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 5)

    def test_serialize_an_wishlist(self):
        """It should Serialize an wishlist"""
        wishlist = WishlistFactory()
        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist["id"], wishlist.id)
        self.assertEqual(serial_wishlist["customer_id"], wishlist.customer_id)
        self.assertEqual(serial_wishlist["wishlist_name"], wishlist.wishlist_name)
        self.assertEqual(serial_wishlist["created_date"], str(wishlist.created_date))

    def test_deserialize_an_wishlist(self):
        """It should Deserialize an wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(new_wishlist.wishlist_name, wishlist.wishlist_name)
        self.assertEqual(new_wishlist.created_date, wishlist.created_date)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_repr_wishlist(self):
        """It should represent wishlist as a string"""
        wishlist = WishlistFactory()
        wishlist.create()
        given_id = wishlist.id
        repr_string = repr(wishlist)
        expected_repr = f"<wishlist_id=[{given_id}]>"
        self.assertEqual(repr_string, expected_repr)

    def test_wishlist_id_is_increment(self):
        """It should represent wishlist_id as incrementing"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        wishlist = WishlistFactory()
        wishlist.create()
        expected = wishlist.id + 1

        for wishlist in WishlistFactory.create_batch(5):
            wishlist.create()
            self.assertEqual(wishlist.id, expected)
            expected += 1


class TestWishlistItem(unittest.TestCase):
    """Test cases for WishlistItem Model"""

    def test_wishlist_item_no_arg_initializer(self):
        """It should create an instance using the no arg initializer"""
        item = WishlistItem()
        self.assertIsNotNone(item)

    # Note: This is kind of a silly test.  I had problems trying to implement a __init__ function that would have set all these values in a single line.
    def test_wishlist_after_populating_properties(self):
        """It should create an instance using the constructor with arguments"""
        now = datetime.now()
        values = {
            "id": 1,
            "wishlist_id": 2,
            "product_id": 3,
            "product_name": "The Big Lebowski",
            "product_price": 9.99,
            "created_date": now,
        }
        item = WishlistItem()
        item.id = values["id"]
        item.wishlist_id = values["wishlist_id"]
        item.product_id = values["product_id"]
        item.product_name = values["product_name"]
        item.product_price = values["product_price"]
        item.created_date = values["created_date"]

        # self.assertEqual(item.id, values.id)
        self.assertEqual(item.wishlist_id, values["wishlist_id"])
        self.assertEqual(item.product_id, values["product_id"])
        self.assertEqual(item.product_name, values["product_name"])
        self.assertEqual(item.product_price, values["product_price"])
        self.assertEqual(item.created_date, values["created_date"])

    def test_repr_method(self):
        item = WishlistItemFactory()
        expected = f"WishlistItem(id={item.id}, wishlist_id={item.wishlist_id}, product_id={item.product_id}, product_name='{item.product_name}', product_price={item.product_price}, created_date='{item.created_date}')"
        self.assertEqual(repr(item), expected)

    def test_serialize(self):
        item = WishlistItemFactory()
        serialized = item.serialize()
        self.assertEqual(item.wishlist_id, serialized["wishlist_id"])
        self.assertEqual(item.product_id, serialized["product_id"])
        self.assertEqual(item.product_name, serialized["product_name"])
        self.assertEqual(item.product_price, serialized["product_price"])
        self.assertEqual(item.created_date, serialized["created_date"])
