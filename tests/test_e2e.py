
from flask import url_for 
from playwright.sync_api import Page, expect

def test_e2e_add_book_to_catalog_and_check_catalog(app, live_server, page: Page):
    """Test adding a book to the catalog and verifying it appears in the catalog"""
    page.goto("http://127.0.0.1:5000/catalog") # start at catalog page

    #go to add book page
    page.get_by_role("link", name="➕ Add Book").click()
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("Horror Story")
    expect(page.get_by_role("textbox", name="Title *")).to_have_value("Horror Story");

    #fill in author, isbn, total copies
    page.get_by_role("textbox", name="Author *").click()
    page.get_by_role("textbox", name="Author *").fill("Jayden Smith")
    expect(page.get_by_role("textbox", name="Author *")).to_have_value("Jayden Smith");

    page.get_by_role("textbox", name="ISBN *").click()
    page.get_by_role("textbox", name="ISBN *").fill("1111111111111")
    expect(page.get_by_role("textbox", name="ISBN *")).to_have_value("1111111111111");

    page.get_by_role("spinbutton", name="Total Copies *").click()
    page.get_by_role("spinbutton", name="Total Copies *").fill("7")
    expect(page.get_by_role("spinbutton", name="Total Copies *")).to_have_value("7");

    page.get_by_role("button", name="Add Book to Catalog").click()
    expect(page.get_by_text("Book \"Horror Story\" has been")).to_be_visible()

    #back to catalog page
    page.goto("http://127.0.0.1:5000/catalog")

    #verify book appears in catalog
    page.get_by_role("cell", name="Horror Story").click()
    expect(page.get_by_role("cell", name="Horror Story")).to_be_visible()
    expect(page.get_by_role("cell", name="Jayden Smith")).to_be_visible()
    expect(page.get_by_role("cell", name="1111111111111")).to_be_visible()
    expect(page.get_by_role("row", name="5 Horror Story Jayden Smith").locator("span")).to_be_visible()

def test_e2e_borrow_book_and_verify_borrowed_books(app, live_server, page: Page):
    """Test borrowing a book and verifying it's confirmation message appears"""
    # First, add a book to the catalog
    page.goto("http://127.0.0.1:5000/catalog")

    #add book to catalog (to be borrowed later)
    page.get_by_role("link", name="➕ Add New Book").click()
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("Fairy Tales")
    page.get_by_role("textbox", name="Author *").click()
    page.get_by_role("textbox", name="Author *").fill("Mika Lore")
    page.get_by_role("textbox", name="ISBN *").click()
    page.get_by_role("textbox", name="ISBN *").fill("1212121212121")
    page.get_by_role("spinbutton", name="Total Copies *").click()
    page.get_by_role("spinbutton", name="Total Copies *").fill("3")
    page.get_by_role("button", name="Add Book to Catalog").click()

    #borrow the book just added with patron ID
    page.get_by_role("row", name="1 Test Creator 1111111111111").get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_role("row", name="2 Fairy Tales Mika Lore").get_by_placeholder("Patron ID (6 digits)").click()
    page.get_by_role("row", name="2 Fairy Tales Mika Lore").get_by_placeholder("Patron ID (6 digits)").fill("888888")
    expect(page.get_by_role("cell", name="888888 Borrow").get_by_placeholder("Patron ID (6 digits)")).to_have_value("888888");
   
   #click borrow button
    page.get_by_role("cell", name="888888 Borrow").get_by_role("button").click()

    #verify borrow confirmation message appears
    expect(page.get_by_text("Successfully borrowed \"Fairy")).to_be_visible()

    #verify available copies decreased by 1
    expect(page.locator("tbody")).to_contain_text("2/3 Available")