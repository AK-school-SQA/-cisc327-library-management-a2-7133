"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_all_books, get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability, get_patron_borrowed_books,
    update_borrow_record_return_date,
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200 and len(title.strip()) > 1:
        return False, "Title must be greater than 1 and less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100 and len(author.strip()) > 1:
        return False, "Author must be greater than 1 and less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isbn.isdigit():
        return False, "ISBN must be digits"
    
    if not isinstance(total_copies, int) or total_copies <= 0 or total_copies > 2147483647:
        return False, "Total copies must be a positive integer greater than 0 and less than equal to 2,147,483,647"
    
    try:
        total_copies = int(total_copies)
    except ValueError:
        return False, "Total copies must be a valid integer."

    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'






def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    Implements R4: Book Return Processing
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to return
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Verify book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Verify if the book was borrowed by the patron and not yet returned
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Get all active borrows of this specific book
    active_borrows = [b for b in borrowed_books if b['book_id'] == book_id and not b.get('return_date')]
    #print(f"Active borrows found: {len(active_borrows)}")
    #print(f"Active borrows details: {active_borrows}")

    if not active_borrows:
        return False, "This book was not borrowed."

    #sort list by the borrow date in descending order
    active_borrows.sort(key=lambda x: x['borrow_date'], reverse=True)

    # Get the most recent borrow record
    most_recent_borrow = active_borrows[0]
    due_date = most_recent_borrow['due_date']

    # Calculate late fees 
    late_fee_info = calculate_late_fee_for_book(patron_id, book_id)
    
    # update patron list to mark that one book as returned
    update_borrow_record_return_date(patron_id, book_id, due_date, datetime.now())

    # Increase book availability
    availability_success = update_book_availability(book_id, +1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    #availabile books is not more
    if book['available_copies'] + 1 > book['total_copies']:
        return False, "Database error: Available copies exceed total copies after return."
    

    #check patron list again to see if there are still active borrows of this book
    #remaining_borrows = [b for b in get_patron_borrowed_books(patron_id) if b['book_id'] == book_id and not b.get('return_date')]
    #print(f"Remaining active borrows after return: {len(remaining_borrows)}")
    #if len(remaining_borrows) > 0:
    #    print(f"Remaining active borrows details: {remaining_borrows}")

    # Calculate late fees
    

    # Prepare return message with fee information
    message = f"Successfully returned book '{book['title']}'. "
    
    if late_fee_info['days_overdue'] > 0:
        message += f"\n\nBook is {late_fee_info['days_overdue']} days overdue. "
        message += f"\nLate fee charged: ${late_fee_info['fee_amount']:.2f}"
    else:
        message += "No late fees charged."

    return True, message











def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5: Late Fee Calculation
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
    
    Returns:
        dict: Contains fee amount and days overdue info
        { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculated' or 'No late fee. Book is not overdue.' or 'No active borrow record found for this book.'
        }
    
    Fee structure:
    - Books are due 14 days after borrowing
    - $0.50/day for first 7 days overdue
    - $1.00/day for each additional day after 7 days
    - Maximum $15.00 per book
    """
    # Get borrowed record details
    borrowed_books = get_patron_borrowed_books(patron_id)
    active_borrows = [b for b in borrowed_books if b['book_id'] == book_id and not b.get('return_date')]
    #print(f"Active borrows found: {len(active_borrows)}")
    #print(f"Active borrows details: {active_borrows}")

    if not active_borrows:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No active borrow record found for this book.'}

    #sort list by the borrow date in descending order
    active_borrows.sort(key=lambda x: x['borrow_date'], reverse=True)

    # Get the most recent borrow record
    most_recent_borrow = active_borrows[0]
    due_date = most_recent_borrow['due_date']
    
    current_date = datetime.now()
  
    
    # Calculate days overdue
    if current_date <= due_date:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No late fee. Book is not overdue.'}

    days_overdue = (current_date - due_date).days
    fee_amount = 0.0
    
    # Calculate fee based on overdue days
    if days_overdue <= 7:
        # First 7 days: $0.50 per day
        fee_amount = days_overdue * 0.50
    else:
        # First 7 days at $0.50/day
        fee_amount = 7 * 0.50
        # Additional days at $1.00/day
        fee_amount += (days_overdue - 7) * 1.00
    
    # Cap fee at maximum $15.00
    if (fee_amount > 15.00):
        fee_amount = 15.00
    
    return {
        'fee_amount': round(fee_amount, 2),
        'days_overdue': days_overdue,
        'status': 'Late fee calculated, '
    }










def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6: Book Search
    
    Args:
        search_term ('q'): The term to search for
        search_type ('type'): Type of search ('title' or 'author' or 'isbn)
        
    Returns:
        list: List of matching books with their details and availability,
             including books that exist but might not be available for borrowing.
             Books are sorted with exact matches first, then alphabetically by title.
             
    Search types supported:
    - Title: Case-insensitive substring match
    - Author: Case-insensitive substring match
    - ISBN: Exact prefix match from start of ISBN
    """
    if not search_term or not search_term.strip():
        return []
        
    # Get all books from catalog
    all_books = get_all_books() # List to hold search results
    
    # Clean up search term for each new search when selected
    search_term = search_term.strip()
    results = []
    
    for book in all_books:
        if search_type == 'title':
            # Case-insensitive substring match for title
            if search_term.lower() in book['title'].lower() and len(search_term) <= 200:
                results.append(book)
        elif search_type == 'author':
            # Case-insensitive substring match for author
            if search_term.lower() in book['author'].lower() and len(search_term) <= 100:
                results.append(book)
        elif search_type == 'isbn':
            # Exact match from start for ISBN
            if book['isbn'] == search_term and len(search_term) == 13 and search_term.isdigit():
                results.append(book)
            
    # First sort alphabetically by title
    results.sort(key=lambda x: x['title'].lower())
    
    # Then move exact matches to the front
    if search_type in ['title', 'author']:
        # For title/author searches, check for exact match in the respective field
        matches = []
        field_name = 'title' if search_type == 'title' else 'author'
        
        for book in results:
            if book[field_name].lower() in search_term.lower():
                matches.append(book)


    elif search_type == 'isbn':
        # For ISBN searches, check for exact ISBN match
        matches = []
        for book in results:
            if book['isbn'] == search_term:
                matches.append(book)
    
    return matches




def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7: Patron Status Report
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: 
            currently_borrowed: list of currently borrowed books
            total_fees_due: sum of all late fees
            books_overdue: count of overdue books
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'error': "Invalid patron ID. Must be exactly 6 digits.",
            'currently_borrowed': [],
            'total_fees_due': 0.00,
            'books_overdue': 0
        }
    
    # Get all borrowed books
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Filter for currently borrowed (not returned) books
    current_borrows = [b for b in borrowed_books if not b.get('return_date')]
    
    # Calculate total fees and count overdue books
    total_fees = 0.00
    overdue_count = 0
    
    for book in current_borrows:
        # Calculate late fee for each book
        fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
        if fee_info['days_overdue'] > 0:
            overdue_count += 1
            total_fees += fee_info['fee_amount']
    
    return {
        'currently_borrowed': current_borrows,
        'total_fees_due': total_fees,
        'books_overdue': overdue_count
    }
