import pytest
from library_service import (
    add_book_to_catalog, borrow_book_by_patron, get_patron_status_report, return_book_by_patron, calculate_late_fee_for_book   
)

from clearDB import clear_database
import database
   
from database import get_patron_borrow_count
from datetime import datetime, timedelta
clear_database()

def test_total_late_fees_owed_exists():
    """Test that total late fees are correctly calculated for multiple overdue books"""
    # Add two books
    add_book_to_catalog("Late Fees?", "Test Author", "1234567898988", 3)
    add_book_to_catalog("Late Fees?2", "Test Author", "1234567898989", 3)
    patron_id = "123456"
    
    # Borrow both books
    borrow_book_by_patron(patron_id, 1)  # First book
    borrow_book_by_patron(patron_id, 2)  # Second book

    # Set different overdue dates for each book
    conn = database.get_db_connection()
    
    # First book: 10 days overdue (7 days at $0.50 + 3 days at $1.00 = $6.50)
    overdue_date1 = datetime.now() - timedelta(days=10)
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date1.strftime('%Y-%m-%d %H:%M:%S'), patron_id, 1))
    
    # Second book: 15 days overdue (7 days at $0.50 + 8 days at $1.00 = $11.50)
    overdue_date2 = datetime.now() - timedelta(days=15)
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date2.strftime('%Y-%m-%d %H:%M:%S'), patron_id, 2))
    
    conn.commit()
    conn.close()

    # Get patron status
    status = get_patron_status_report(patron_id)
    
    # Total fees should be sum of both books:
    # Book 1: $6.50 (10 days overdue)
    # Book 2: $11.50 (15 days overdue)
    # Total: $18.00, but capped at $15.00 per library policy
    assert status['total_fees_due'] == 6.5 + 11.5
    assert status['books_overdue'] == 2  # Both books should be counted as overdue
    clear_database()

def test_stored_currently_borrowed_books_with_due_dates_valid():
    """Test that currently borrowed books include due dates"""
    add_book_to_catalog("Currently Borrowed?", "Test Author", "1234567898988", 3)
    add_book_to_catalog("Currently Borrowed? 2", "Test Author", "1234567777788", 3)
    patron_id = "123456"
    borrow_book_by_patron(patron_id, 1)
    borrow_book_by_patron(patron_id, 2)

    # Get patron status
    status = get_patron_status_report(patron_id)
    
    # Check that each borrowed book has a due date
    from datetime import datetime, timedelta
    now = datetime.now()
    expected_due_date = now + timedelta(days=14)
    
    for book in status['currently_borrowed']:   
        assert 'due_date' in book
        assert book['due_date'] is not None
        due_date = book['due_date']  # due_date is already a datetime object
        # Allow 1 minute tolerance in the comparison
        assert abs((due_date - expected_due_date).total_seconds()) < 60
    clear_database()

def test_number_of_books_currently_borrowed():
    """Test that the number of currently borrowed books is correct"""
    # Add three books but only borrow two
    add_book_to_catalog("Number of Books?", "Test Author", "1234567898988", 3)
    add_book_to_catalog("Number of Books? 2", "Test Author", "1234567777788", 3)
    add_book_to_catalog("Number of Books? 3", "Test Author", "1234567767788", 3)

    patron_id = "123888"
    borrow_book_by_patron(patron_id, 1)
    borrow_book_by_patron(patron_id, 2)

    # Get patron status
    status = get_patron_status_report(patron_id)

    # Verify number of currently borrowed books
    assert len(status['currently_borrowed']) == 2
    
    # Verify these are the correct books
    book_ids = [book['book_id'] for book in status['currently_borrowed']]
    assert sorted(book_ids) == [1, 2]
    clear_database()

def test_shows_borrowing_history():
    """shows borrowing history/ history stored"""
    add_book_to_catalog("Borrowing History?", "Test Author", "1234567898988", 3)
    add_book_to_catalog("Borrowing History? 2 ", "Test Author", "1234567777788", 3)
    add_book_to_catalog("Borrowing History? 3 ", "Test Author", "1234567767788", 3)

    patron_id = "123888"
    borrow_book_by_patron(patron_id, 1)
    borrow_book_by_patron(patron_id, 2)
    return_book_by_patron(patron_id, 1)

    books_borrowed, total_late_fees, borrowing_history = get_patron_status_report(patron_id) #borrowing_history is a list of book dictonaries
    #borrowed history list should also contain variable on the status that it 'returned' or still 'borrowed'.
    for record in borrowing_history:
        assert 'title' in record and 'author' in record and 'isbn' in record and 'status' in record

    clear_database()