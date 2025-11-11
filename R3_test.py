import pytest
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    get_book_by_id
)

from clearDB import clear_database
clear_database()

import database

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

def test_invalid_book_borrowing_over_5_max_of_same_card():
    """Test borrowing a book over 5 books max limit from same card"""
    add_book_to_catalog("Over 6", "Test Author", "1234567898588", 7)

    # Simulate borrowing more than 5 books check
    for i in range(7):
          sucess, message = borrow_book_by_patron("123456", 1)
          if i >= 5:
              assert sucess == False
              assert "reached the maximum borrowing limit of 5 books" in message
              break
    clear_database()

def test_valid_borrow_book_decreases_available_copies():
    """Test borrowing a book decreases available copies"""
    add_book_to_catalog("Decrease Available Copies?", "Test Author", "1234567898588", 3)

    book = database.get_book_by_id(1)
    initial_available_copies = book.get("available_copies")

    sucess, message = borrow_book_by_patron("123476", 1)
    assert sucess == True
    assert "Successfully borrowed" in message

    book = database.get_book_by_id(1)
    updated_available_copies = book.get("available_copies")

    assert updated_available_copies == initial_available_copies - 1
    clear_database()
    
clear_database()