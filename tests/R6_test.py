import pytest
from unittest.mock import Mock
from services.library_service import (
    add_book_to_catalog,
    search_books_in_catalog
)

from clearDB import clear_database

import database

clear_database()

def test_valid_search_isbn():
    """Test to find book with exact match isbn"""
    add_book_to_catalog("isbn-search?", "Test Author", "1231234568889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1231237778889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1244437778889", 3)
    
    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns a list containing the one isbn that match the search that will be displayed
    books = search_books_in_catalog("1231234568889", "isbn")
    assert books[0].get("isbn") == "1231234568889"
    clear_database()

def test_valid_search_isbn_no_results():
    """Test to find book with no results"""
    add_book_to_catalog("isbn-search?", "Test Author", "1231234568889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1231237778889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1244437778889", 3)
    
    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no isbns match the search which will be displayed
    books = search_books_in_catalog("9999999999999", "isbn")
    assert books == []
    clear_database()

def test_invalid_isbn_size_small():
    """Test to find book with invalid isbn size small"""
    add_book_to_catalog("isbn-search?", "Test Author", "1231234568889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1231237778889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no isbns match the search which will be displayed
    books = search_books_in_catalog("12345678", "isbn")
    assert books == []
    clear_database()

def test_invalid_isbn_size_large():
    """Test to find book with invalid isbn size large"""
    add_book_to_catalog("isbn-search?", "Test Author", "1231234568889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1231237778889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no isbns match the search which will be displayed
    books = search_books_in_catalog("1231234568889123", "isbn")
    assert books == []
    clear_database()

def test_invalid_isbn_only_integers():
    """Test to find book with invalid isbn only integers"""
    add_book_to_catalog("isbn-search?", "Test Author", "1231234568889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1231237778889", 3)
    add_book_to_catalog("isbn-search?", "Test Author", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no isbns match the search which will be displayed
    books = search_books_in_catalog("abcdabc@@bcde", "isbn")
    assert books == []
    clear_database()


def test_valid_search_title_partial():
    """Test to find book with partial match title"""
    # Add books with case variations in title
    add_book_to_catalog("titLe-searchrr? 1", "Test Author", "1231234568889", 1)
    add_book_to_catalog("title-svvearch? 2", "Test Author", "1231237778889", 2)
    add_book_to_catalog("tITle-searchc? 3", "Test Author", "1244437778889", 3)

    # Search for partial title match (case-insensitive)
    books = search_books_in_catalog("vv", "title")
    # All titles starting with 'tit' (case-insensitive) should be included

    for i in books:
        assert "vv" in i['title'].lower()
    clear_database()


def test_valid_search_author_partial():
    """Test to find book with partial match author"""
    # Add books with case variations in author
    add_book_to_catalog("Some Book 1", "AutwefOr-search?", "1231234568889", 1)
    add_book_to_catalog("Some Book 2", "Authworff-search?", "1231237778889", 2)
    add_book_to_catalog("Some Book 3", "aUthfor-search?", "1244437778889", 3)

    # Search for partial author match (case-insensitive)
    books = search_books_in_catalog("w", "author")

    for i in books:
        assert "w" in i['author'].lower()
    clear_database()

def test_valid_search_no_results_author():
    """Test to find book with no results"""
    add_book_to_catalog("Some Book 1", "AuthOr-search?", "1231234568889", 3)
    add_book_to_catalog("Some Book 2", "Author-search?", "1231237778889", 3)
    add_book_to_catalog("Some Book 3", "aUthor-search?", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no books match the search which will be displayed
    books = search_books_in_catalog("Somename", "author")
    assert books == [] #put this in proper dictionary format
    clear_database

def test_valid_search_no_results_title():
    """Test to find book with no results"""
    add_book_to_catalog("Some Book 1", "AuthOr-search?", "1231234568889", 3)
    add_book_to_catalog("Some Book 2", "Author-search?", "1231237778889", 3)
    add_book_to_catalog("Some Book 3", "aUthor-search?", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no books match the search which will be displayed
    books = search_books_in_catalog("Somename", "title")
    assert books == [] #put this in proper dictionary format
    clear_database
    
def test_invalid_search_empty_string_title():
    """Test to find book with empty string title"""
    add_book_to_catalog("Some Book 1", "AuthOr-search?", "1231234568889", 3)
    add_book_to_catalog("Some Book 2", "Author-search?", "1231237778889", 3)
    add_book_to_catalog("Some Book 3", "aUthor-search?", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no books match the search which will be displayed
    books = search_books_in_catalog("", "title")
    assert books == [] #put this in proper dictionary format

    clear_database()

def test_invalid_search_empty_string_author():
    """Test to find book with empty string author"""
    add_book_to_catalog("Some Book 1", "AuthOr-search?", "1231234568889", 3)
    add_book_to_catalog("Some Book 2", "Author-search?", "1231237778889", 3)
    add_book_to_catalog("Some Book 3", "aUthor-search?", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no books match the search which will be displayed
    books = search_books_in_catalog("", "author")
    assert books == [] #put this in proper dictionary format

def test_invalid_search_empty_isbn():
    """Test to find book with empty string isbn"""
    add_book_to_catalog("Some Book 1", "AuthOr-search?", "1231234568889", 3)
    add_book_to_catalog("Some Book 2", "Author-search?", "1231237778889", 3)
    add_book_to_catalog("Some Book 3", "aUthor-search?", "1244437778889", 3)

    #placeholder for search function
    #assume function changes its search in the book catalog based on the type of search and returns an empty list since no books match the search which will be displayed
    books = search_books_in_catalog("", "isbn")
    assert books == [] #put this in proper dictionary format
    clear_database()