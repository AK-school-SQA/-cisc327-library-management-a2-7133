
from unittest.mock import Mock
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron
    ,calculate_late_fee_for_book
)

from clearDB import clear_database

import database
clear_database()

from datetime import timedelta, datetime

def test_valid_is_book_in_patron_borrow_record():
    """Test verifys that the book was borrowed by a patron"""
    add_book_to_catalog("Patron Has book", "Test Author", "1234567898788", 3)
    add_book_to_catalog("Patron Has book 2", "Test Author", "1234567898588", 3)

    patron_id = "123456"
    borrow_book_by_patron(patron_id, 1)
    borrow_book_by_patron(patron_id, 1)
    borrow_book_by_patron(patron_id, 2) #looking for this book in borrow record
    
    #patron borrow record should show that the patron has borrowed the book
    print(database.get_patron_borrowed_books(patron_id))

    for book in database.get_patron_borrowed_books(patron_id):
        if book.get("book_id") == 2:
            assert book.get("book_id") == 2
    clear_database()

def test_valid_book_borrowed_by_patron_is_returned():
    """Test returning a book that was borrowed by the patron"""

    add_book_to_catalog("Return Book?", "Test Author", "1234567898888", 3)
    patron_id = "133456"
    borrow_book_by_patron(patron_id, 1)

    book = database.get_book_by_id(1)
    initial_available_copies = book.get("available_copies")

    #return the book and check if the book was borrowed by the patron. NOTE that return_book_by_patron is not implemented yet
    # This is a placeholder, THIS TEST WILL PASS ONLY WHEN return_book_by_patron IS IMPLEMENTED
    sucess, message = return_book_by_patron("133456", 1) #assuming program checks that return book by patron is true and WILL return true with a message string containing substring "Successfully returned"
    assert sucess == True
    assert "Successfully returned" in message

    book = database.get_book_by_id(1)
    updated_available_copies = book.get("available_copies") # this number should be initial_available_copies + 1 after return book is valid

    assert (updated_available_copies == initial_available_copies + 1) and (updated_available_copies <= database.get_book_by_id(1).get("total_copies"))

    clear_database()

def test_records_return_date_is_valid():
    """Test that the return date is recorded when a book is returned"""
    add_book_to_catalog("Return Date Book?", "Test Author", "1234567898988", 3)
    patron_id = "143456"
    borrow_book_by_patron(patron_id, 1)

    # Simulate returning the book
    return_book_by_patron(patron_id, 1) #assuming program stores when returned book happened true and WILL return true with a message string containing substring "Successfully returned"

    # Check if the return date is recorded
    for record in database.get_patron_borrowed_books(patron_id):
        if record.get("book_id") == 1:
            assert record.get("return_date") is not None
            break

    clear_database()

def test_return_book_by_patron_accepts_parameters_valid():
    """Test that return_book_by_patron accepts patron ID and book ID as parameters"""
    add_book_to_catalog("Return Param Book?", "Test Author", "1234567898988", 3)
    patron_id = "143456"
    borrow_book_by_patron(patron_id, 1)

    success, message = return_book_by_patron(patron_id, 1) #assuming program checks that return book by patron is true and WILL return true with a message string containing substring "Successfully returned"
    assert success == True
    assert "Successfully returned" in message
    clear_database()

def test_valid_six_digit_card():
    """Test accepting a valid six digit card number"""
    add_book_to_catalog("valid card?", "Test Author", "1234567898588", 3)
    
    sucess, message = borrow_book_by_patron("123456", 1)
    assert sucess == True
    assert "Successfully borrowed" in message
    clear_database()

def test_invalid_six_digit_card_short_len():
    """Test rejecting an invalid six digit card number that is less than 6 digits"""
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)
    
    sucess, message = borrow_book_by_patron("12345", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_big_len():
    """Test rejecting an invalid six digit card number that is more than 6 digits"""
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)

    sucess, message = borrow_book_by_patron("1234567", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_not_numbers():
    """Test rejecting an invalid six digit card number that is not a number"""
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)

    sucess, message = borrow_book_by_patron("abcde@", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_not_int():
    """Test rejecting an invalid six digit card number that is not an integer"""
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)

    sucess, message = borrow_book_by_patron("0.1111", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

clear_database()

def test_records_return_date_assigned_value_correct_valid():
    """Test that the return date is recorded with a timestamp when a book is returned"""
    add_book_to_catalog("Return Date Book?", "Test Author", "1234567898988", 3)
    patron_id = "143456"
    borrow_book_by_patron(patron_id, 1)

    # Simulate returning the book
    return_book_by_patron(patron_id, 1)

    #get current time for comparison
    current_time = datetime.now()

    # Check if the return date is recorded
    for record in database.get_patron_borrowed_books(patron_id):
        if record.get("book_id") == 1:
            assert record.get("return_date") == current_time
            break

    clear_database()

def test_available_copies_increased_valid():
    """Test that available copies increase when a book is returned"""
    add_book_to_catalog("Available Copies Book?", "Test Author", "1234567898988", 3)
    patron_id = "153456"
    borrow_book_by_patron(patron_id, 1)

    # Return the book
    return_book_by_patron(patron_id, 1)

    book = database.get_book_by_id(1)
    assert book.get("available_copies") == 3

    clear_database()

def test_available_copies_returned_is_more_than_total_invalid():
    """Test that available copies never exceed total copies after multiple returns"""
    add_book_to_catalog("Copies Test Book", "Test Author", "1234567898988", 3)  
    patron_id = "153456"
    borrow_book_by_patron(patron_id, 1)
    return_book_by_patron(patron_id, 1)
    success, msg = return_book_by_patron(patron_id, 1) # Attempt to return again
    assert success == False
    assert "Available copies exceed total copies after return" in msg or "This book was not borrowed." in msg

    clear_database()

def test_returning_book_not_borrowed_by_patron_invalid():
    """Test returning a book that was not borrowed by the patron"""
    add_book_to_catalog("Not Borrowed Book?", "Test Author", "1234567898988", 3)
    patron_id = "163456"

    # Attempt to return a book that wasn't borrowed
    success, message = return_book_by_patron(patron_id, 1)
    assert success == False
    assert "This book was not borrowed." in message

    clear_database()

# WE WILL GO MORE INDEPTH WITH LATE FEE IN R5_test.py

