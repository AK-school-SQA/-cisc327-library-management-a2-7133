import pytest
from unittest.mock import Mock
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    get_book_by_id
)

from clearDB import clear_database
clear_database()

import database

def test_valid_six_digit_card(mocker):
    """Test accepting a valid six digit card number"""
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'valid card?', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 3, 'available_copies': 3}
    )
    mocker.patch(
        'services.library_service.get_patron_borrow_count',
        return_value=0
    )
    mocker.patch(
        'services.library_service.insert_borrow_record',
        return_value=True
    )
    mocker.patch(
        'services.library_service.update_book_availability',
        return_value=True
    )
    
    add_book_to_catalog("valid card?", "Test Author", "1234567898588", 3)
    
    sucess, message = borrow_book_by_patron("123456", 1)
    assert sucess == True
    assert "Successfully borrowed" in message
    clear_database()

def test_invalid_six_digit_card_short_len(mocker):
    """Test rejecting an invalid six digit card number that is less than 6 digits - validation test."""
    # STUB: Mock get_book_by_isbn to return None (book doesn't exist)
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    # STUB: Mock insert_book to return True
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)
    
    sucess, message = borrow_book_by_patron("12345", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_big_len(mocker):
    """Test rejecting an invalid six digit card number that is more than 6 digits"""
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)
    sucess, message = borrow_book_by_patron("1234567", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_not_numbers(mocker):
    """Test rejecting an invalid six digit card number that is not a number"""

    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)

    sucess, message = borrow_book_by_patron("abcde@", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_six_digit_card_not_int(mocker):
    """Test rejecting an invalid six digit card number that is not an integer"""
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    
    add_book_to_catalog("6 Digit Card?", "Test Author", "1234567898588", 3)

    sucess, message = borrow_book_by_patron("0.1111", 1)
    assert sucess == False
    assert "Must be exactly 6 digits" in message
    clear_database()

def test_invalid_book_borrowing_over_5_max_of_same_card(mocker):
    """Test borrowing a book over 5 books max limit from same card"""
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    mocker.patch(
        'services.library_service.get_book_by_id',
        return_value={'id': 1, 'title': 'Over 6', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 7, 'available_copies': 7}
    )
    mocker.patch(
        'services.library_service.get_patron_borrow_count',
        side_effect=[0, 1, 2, 3, 4, 5, 5]  # Should returns increasing values each call
    )

    mocker.patch(
        'services.library_service.insert_borrow_record',
        return_value=True
    )
    mocker.patch(
        'services.library_service.update_book_availability',
        return_value=True
    )
    
    add_book_to_catalog("Over 6", "Test Author", "1234567898588", 7)

    # Simulate borrowing more than 5 books check
    for i in range(7):
          sucess, message = borrow_book_by_patron("123456", 1)
          if i >= 5:
              assert sucess == False
              assert "reached the maximum borrowing limit of 5 books" in message
              break
    clear_database()

def test_valid_borrow_book_decreases_available_copies(mocker):
    """Test borrowing a book decreases available copies"""
    mocker.patch(
        'services.library_service.get_book_by_isbn',
        return_value=None
    )
    mocker.patch(
        'services.library_service.insert_book',
        return_value=True
    )
    mocker.patch(  #returns 3 copies initially and then borrow 2
        'services.library_service.get_book_by_id',
        side_effect=[
            {'id': 1, 'title': 'Decrease Available Copies?', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 3, 'available_copies': 3},
            {'id': 1, 'title': 'Decrease Available Copies?', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 3, 'available_copies': 2}
        ]
    )
    mocker.patch( #no borrow yet
        'services.library_service.get_patron_borrow_count',
        return_value=0
    )
    mocker.patch(
        'services.library_service.insert_borrow_record',
        return_value=True
    )
    mocker.patch(
        'services.library_service.update_book_availability',
        return_value=True
    )
    mocker.patch(
        'database.get_book_by_id',
        side_effect=[
            {'id': 1, 'title': 'Decrease Available Copies?', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 3, 'available_copies': 3},
            {'id': 1, 'title': 'Decrease Available Copies?', 'author': 'Test Author', 'isbn': '1234567898588', 'total_copies': 3, 'available_copies': 2}
        ]
    )
    
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