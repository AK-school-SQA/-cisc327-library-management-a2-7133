import pytest
from unittest.mock import Mock
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    calculate_late_fee_for_book,
    return_book_by_patron
)

from clearDB import clear_database

from datetime import timedelta, datetime
import database
clear_database()

def test_that_book_is_overdue_valid():
    """Test verifies that a book is overdue"""
    add_book_to_catalog("14 Overdue Days", "Author", "4440007776666",3)
    patron_id = "134344"
    borrow_book_by_patron(patron_id, 1)

    # Manually set the borrow record to be 15 days ago to simulate overdue
    book = database.get_book_by_id(1)
    book["due_date"] = datetime.now() - timedelta(days=15)

    #time between due date and now should be greater than 14 days value
    book_held_time = datetime.now() - book["due_date"]
    assert book_held_time.days > 14
    clear_database()
    
def test_that_book_is_overdue_invalid():
    """Test verifies that a book is not overdue"""
    add_book_to_catalog("14 Overdue Days NOT", "Author", "4440007776666",3)
    patron_id = "134344"
    borrow_book_by_patron(patron_id, 1)

    # Manually set the borrow to 6 days ago
    book = database.get_book_by_id(1)
    book["due_date"] = datetime.now() - timedelta(days=6)

    book_held_time = datetime.now() - book["due_date"]
    assert book_held_time.days < 14
    clear_database()

def test_set_due_date_default_14_days_later():
    """Test that when first borrowing a book, the due date is set to 14 days later"""
    add_book_to_catalog("14 Days Later", "Author", "4440007776666",3)
    patron_id = "134344"
    borrow_book_by_patron(patron_id, 1)

    book = database.get_book_by_id(1)
    expected_due_date =  datetime.now() + timedelta(days=14)
    #get borrow record to check due date
    borrow_records = database.get_patron_borrowed_books(patron_id)
    assert borrow_records[0]["due_date"].day == expected_due_date.day
    clear_database()
  

def test_overdue_bill_cap():
    """Test that the late fee does not exceed the maximum cap of $15.00 and is in format json with correct date and status"""
    add_book_to_catalog("VERY Overdue Bill Cap", "Author", "4440007776666", 3)
    patron_id = "134344"
    book_id = 1
    
    # Borrow the book
    borrow_book_by_patron(patron_id, book_id)
    
    # Update the due date in the database
    overdue_date = datetime.now() - timedelta(days=25)
    conn = database.get_db_connection()
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date.strftime('%Y-%m-%d %H:%M:%S'), patron_id, book_id))
    conn.commit()
    conn.close()

    # Calculate late fee
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert result["fee_amount"] == 15.0  # Should be capped at $15
    assert result["days_overdue"] == 25
    assert "Late fee calculated" in result["status"]
    clear_database()

def test_overdue_by_7_days_calc_valid():
    """Test that the late fee is calculated correctly for books overdue by exactly 7 days format and status and is in format json with correct date and status"""
    add_book_to_catalog("Overdue by 7 Days", "Author", "4440007776666", 3)
    patron_id = "134344"
    book_id = 1
    
    # Borrow the book
    borrow_book_by_patron(patron_id, book_id)
    
    # Update the due date in the database
    overdue_date = datetime.now() - timedelta(days=7)
    conn = database.get_db_connection()
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date.strftime('%Y-%m-%d %H:%M:%S'), patron_id, book_id))
    conn.commit()
    conn.close()

    # Calculate late fee
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert result["fee_amount"] == 3.5  # 7 days * $0.50 per day
    assert result["days_overdue"] == 7
    assert "Late fee calculated" in result["status"]
    clear_database()

def test_due_past_7_days_under_cap_calc_valid():
    """Test that the late fee is calculated correctly for books overdue by more than 7 days with status in format and is in format json with correct date and status"""
    add_book_to_catalog("Overdue by 10 Days", "Author", "4440007776666", 3)
    patron_id = "134344"
    book_id = 1
    
    # Borrow the book
    borrow_book_by_patron(patron_id, book_id)
    
    # Update the due date in the database
    overdue_date = datetime.now() - timedelta(days=10)
    conn = database.get_db_connection()
    conn.execute('''
        UPDATE borrow_records 
        SET due_date = ? 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    ''', (overdue_date.strftime('%Y-%m-%d %H:%M:%S'), patron_id, book_id))
    conn.commit()
    conn.close()
    
    # Calculate late fee
    result = calculate_late_fee_for_book(patron_id, book_id)
    assert result["fee_amount"] == 6.5  # (7 days * $0.50) + (3 days * $1.00)
    assert result["days_overdue"] == 10
    assert "Late fee calculated" in result["status"]
    clear_database()

