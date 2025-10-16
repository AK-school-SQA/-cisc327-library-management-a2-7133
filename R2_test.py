import pytest
from library_service import (
    add_book_to_catalog, borrow_book_by_patron, return_book_by_patron, get_patron_borrowed_books,
    get_patron_borrow_count, get_book_by_id, get_book_by_isbn, get_all_books, get_patron_status_report

)
import datetime
from datetime import timedelta, datetime

from clearDB import clear_database
clear_database()

import database

def test_valid_book_id_positive():
    """Test adding a book with a positive book ID is generated"""
    add_book_to_catalog("Positive Book ID?", "Test Author", "1234567898888", 3)
    
    books = database.get_all_books()

    book_id = books[0].get("id")
    assert book_id > 0
    clear_database()

def test_available_copies_are_less_than_equal_to_total_copies_valid():
    """Test adding a book with available copies less than or equal to total copies"""
    add_book_to_catalog("Available Copies?", "Test Author", "1234567898888", 3)
    
    books = database.get_all_books()

    available_copies = books[0].get("available_copies")
    total_copies = books[0].get("total_copies")
    assert available_copies <= total_copies
    clear_database()


def test_valid_borrow_button_for_available_books():
    """Test borrowing a book when there are available copies"""
    
    add_book_to_catalog("Borrow Button?", "Test Author", "1234567898888", 3)
    
    books = database.get_all_books()

    available_copies = books[0].get("available_copies")
    assert available_copies > 0  
    clear_database()

def test_invalid_borrow_button_for_unavailable_books():
    """Test borrowing a book when there are no available copies"""
    
    add_book_to_catalog("Borrow Button?", "Test Author", "1234567898888", 1)
    
    books = database.get_all_books()
    book_id = books[0].get("id")

    #borrow the only available copy
    database.insert_borrow_record("123456", book_id, datetime.now() - timedelta(days=5), datetime.now() + timedelta(days=9))
    database.update_book_availability(book_id, -1)

    books = database.get_all_books()
    available_copies = books[0].get("available_copies")
    assert available_copies <= 0
    clear_database()

    def system_displays_books_in_table_format_valid():
        """Test that the system displays books in a table format of dictionaries with keys id, title, author, and ISBN"""
        add_book_to_catalog("Table Format Book", "Test Author", "1234567898888", 3)
        
        books = database.get_all_books()
        
        assert isinstance(books, list)
        assert all(isinstance(book, dict) for book in books) # iterate through list and check each item is a dict
        assert all("id" in book and "title" in book and "author" in book and "ISBN" in book for book in books) # check each book has id, title, author, and ISBN
        clear_database()

clear_database()