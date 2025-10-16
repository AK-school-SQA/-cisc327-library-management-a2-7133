import pytest
from library_service import (
    add_book_to_catalog
)

from clearDB import clear_database
clear_database()

def test_add_book_valid_input_all_fields():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567897", 5)
    
    assert success == False
    assert "13 digits" in message
    clear_database()

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)

    assert success == False
    assert "13 digits" in message
    clear_database()

def test_add_book_invalid_duplicate_isbn():
    """Test adding a book with an isbn value that also exists in the catalog"""
    add_book_to_catalog("Test Book 2", "Test Author", "1234567890129", 5)
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890129", 5)

    assert success == False
    assert "ISBN already exists" in message
    clear_database()

def test_add_book_invalid_isbn_uses_special_characters():
    """Test adding a book with ISBN containing special characters"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "!@#$%^&*()~|;", 5)
    
    assert success == False
    assert "ISBN must be digits" in message
    clear_database()


def test_add_book_invalid_isbn_uses_letters():
    """Test adding a book with ISBN containing letters"""
    success, message = add_book_to_catalog("Test Book 4", "Test Author", "ababababababt", 5)
    
    assert success == False
    assert "ISBN must be digits" in message
    clear_database()

def test_add_book_invalid_copies_zero():
    """Test adding a book with 0 copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "must be a positive integer greater than 0" in message
    clear_database()

def test_add_book_invalid_copies_string():
    """Test adding a book with string copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", "five")
    
    assert success == False
    assert "must be a positive integer greater than 0" in message
    clear_database()

def test_add_book_invalid_copies_none():
    """Test adding a book with no copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", None)
    
    assert success == False
    assert "must be a positive integer greater than 0" in message
    clear_database()

def test_add_book_invalid_copies_float():
    """Test adding a book with float copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 3.5)
    
    assert success == False
    assert "must be a positive integer greater than 0" in message
    clear_database()

def test_add_book_invalid_copies_negative():
    """Test adding a book with negative copies"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -3)
    
    assert success == False
    assert "must be a positive integer greater than 0" in message

    clear_database()

def test_add_book_invalid_empty_title():
    """Test adding a book with empty title"""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "Title is required" in message
    clear_database()

def test_add_book_invalid_empty_author():
    """Test adding a book with empty author"""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "Author is required" in message

    clear_database()


def test_add_book_invalid_title_too_long():
    """Test adding a book with title too long"""
    success, message = add_book_to_catalog("T" * 201, "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "greater than 1 and less than 200 characters" in message
    clear_database()

def test_add_book_invalid_author_too_long():
    """Test adding a book with author name too long"""
    success, message = add_book_to_catalog("Test Book", "A" * 101, "1234567890123", 5)
    
    assert success == False
    assert "greater than 1 and less than 100 characters" in message

clear_database()



