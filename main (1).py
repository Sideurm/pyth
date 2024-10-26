import json
import datetime
from collections import defaultdict

class Book:
    def __init__(self, title, author, isbn, category, copies=1):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.copies = copies
        self.checked_out = 0
        self.due_dates = {}
        self.reservations = []
        self.ratings = []

    def checkout(self, user):
        if self.checked_out < self.copies:
            self.checked_out += 1
            self.due_dates[user] = datetime.date.today() + datetime.timedelta(days=14)
            return True
        return False

    def return_book(self, user):
        if user in self.due_dates:
            del self.due_dates[user]
            self.checked_out -= 1
            return True
        return False

    def reserve(self, user):
        if self.checked_out < self.copies:
            print(f"'{self.title}' is available for checkout.")
        else:
            self.reservations.append(user)
            print(f"{user.name} reserved '{self.title}'. Position in queue: {len(self.reservations)}.")

    def add_rating(self, rating):
        if 1 <= rating <= 5:
            self.ratings.append(rating)
            print(f"Added rating {rating} for '{self.title}'.")
        else:
            print("Rating must be between 1 and 5.")

    def average_rating(self):
        return sum(self.ratings) / len(self.ratings) if self.ratings else 0

    def __str__(self):
        status = f"Checked out: {self.checked_out}/{self.copies} available"
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Category: {self.category}) - {status}, Average Rating: {self.average_rating():.1f}"


class User:
    def __init__(self, name, role='user'):
        self.name = name
        self.role = role
        self.checked_out_books = []
        self.fines = 0
        self.history = []

    def checkout_book(self, book):
        if book.checkout(self):
            self.checked_out_books.append(book)
            self.history.append(f"Checked out '{book.title}'")
            print(f"{self.name} checked out '{book.title}'. Due date: {book.due_dates[self]}.")
        else:
            print(f"'{book.title}' is already checked out.")

    def return_book(self, book):
        if book.return_book(self):
            self.checked_out_books.remove(book)
            if book.due_dates[self] < datetime.date.today():
                days_late = (datetime.date.today() - book.due_dates[self]).days
                self.fines += days_late * 1
                print(f"{self.name} returned '{book.title}' late. Fine: ${self.fines}.")
            else:
                print(f"{self.name} returned '{book.title}' on time.")
            self.handle_reservations(book)
            self.history.append(f"Returned '{book.title}'")
        else:
            print(f"{self.name} does not have '{book.title}' checked out.")

    def handle_reservations(self, book):
        if book.reservations:
            next_user = book.reservations.pop(0)
            next_user.checkout_book(book)

    def pay_fine(self, amount):
        if amount <= self.fines:
            self.fines -= amount
            print(f"{self.name} paid ${amount} in fines. Remaining fine: ${self.fines}.")
        else:
            print(f"{self.name} cannot pay more than the total fines of ${self.fines}.")

    def view_history(self):
        print(f"Action history for {self.name}:")
        for action in self.history:
            print(action)

    def __str__(self):
        return f"{self.name} - Fines: ${self.fines}, Role: {self.role}"


class Library:
    def __init__(self, name):
        self.name = name
        self.books = []
        self.users = []
        self.history = []
        self.borrowing_statistics = defaultdict(int)

    def add_book(self, book):
        self.books.append(book)
        self.history.append(f"Added book: {book}")
        print(f"Book '{book.title}' added to library '{self.name}'.")

    def remove_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                self.books.remove(book)
                self.history.append(f"Removed book: {book}")
                print(f"Book '{book.title}' removed from library '{self.name}'.")
                return
        print(f"No book found with ISBN: {isbn}")

    def find_book(self, title=None, author=None, category=None):
        found_books = [
            book for book in self.books
            if (title is None or title.lower() in book.title.lower()) and
               (author is None or author.lower() in book.author.lower()) and
               (category is None or category.lower() in book.category.lower())
        ]
        if found_books:
            for book in found_books:
                print(book)
        else:
            print("No books found matching the criteria.")

    def add_user(self, user):
        self.users.append(user)
        self.history.append(f"Added user: {user.name}")
        print(f"User '{user.name}' added to library '{self.name}'.")

    def list_books(self):
        print("Library Books:")
        for book in self.books:
            print(book)

    def list_users(self):
        print("Library Users:")
        for user in self.users:
            print(user)

    def generate_report(self):
        print("Library Report:")
        print(f"Total Books: {len(self.books)}")
        print(f"Total Users: {len(self.users)}")
        for user in self.users:
            print(f"{user.name} has {len(user.checked_out_books)} books checked out and owes ${user.fines} in fines.")

    def generate_statistics(self):
        print("Borrowing Statistics:")
        for title, count in self.borrowing_statistics.items():
            print(f"{title}: {count} times borrowed")

    def save_data(self, filename):
        data = {
            "library_name": self.name,
            "books": [{"title": book.title, "author": book.author, "isbn": book.isbn, "category": book.category, "copies": book.copies, "ratings": book.ratings} for book in self.books],
            "users": [{"name": user.name, "role": user.role, "fines": user.fines, "history": user.history} for user in self.users],
            "history": self.history,
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print("Data saved to", filename)

    def load_data(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.name = data.get("library_name", self.name)
                for book_data in data["books"]:
                    book = Book(book_data["title"], book_data["author"], book_data["isbn"], book_data["category"], book_data["copies"])
                    book.ratings = book_data["ratings"]
                    self.add_book(book)
                for user_data in data["users"]:
                    user = User(user_data["name"], user_data["role"])
                    user.fines = user_data["fines"]
                    user.history = user_data.get("history", [])
                    self.add_user(user)
                self.history = data["history"]
            print("Data loaded from", filename)
        except FileNotFoundError:
            print("Data file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON data.")


def main():
    library = Library("Main Library")

    # Loading data
    try:
        library.load_data('library_data.json')
    except FileNotFoundError:
        print("Data file not found. Starting with an empty library.")

    # User interface
    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Add User")
        print("4. Checkout Book")
        print("5. Return Book")
        print("6. List Books")
        print("7. List Users")
        print("8. Find Book")
        print("9. Generate Report")
        print("10. Generate Borrowing Statistics")
        print("11. Save Data")
        print("12. Exit")

        choice = input("Choose an option: ")

        try:
            if choice == '1':
                title = input("Enter book title: ")
                author = input("Enter book author: ")
                isbn = input("Enter book ISBN: ")
                category = input("Enter book category: ")
                copies = int(input("Enter number of copies: "))
                library.add_book(Book(title, author, isbn, category, copies))
            elif choice == '2':
                isbn = input("Enter book ISBN to remove: ")
                library.remove_book(isbn)
            elif choice == '3':
                name = input("Enter user name: ")
                role = input("Enter user role (admin/user): ")
                library.add_user(User(name, role))
            elif choice == '4':
                user_name = input("Enter user name: ")
                # Find user by name
                user = next((u for u in library.users if u.name == user_name), None)
                if user is None:
                    print(f"No user found with name '{user_name}'.")
                    continue
                book_title = input("Enter book title to checkout: ")
                # Find book by title
                book = next((b for b in library.books if b.title == book_title), None)
                if book is None:
                    print(f"No book found with title '{book_title}'.")
                    continue
                user.checkout_book(book)
            elif choice == '5':
                user_name = input("Enter user name: ")
                user = next((u for u in library.users if u.name == user_name), None)
                if user is None:
                    print(f"No user found with name '{user_name}'.")
                    continue
                book_title = input("Enter book title to return: ")
                book = next((b for b in library.books if b.title == book_title), None)
                if book is None:
                    print(f"No book found with title '{book_title}'.")
                    continue
                user.return_book(book)
            elif choice == '6':
                library.list_books()
            elif choice == '7':
                library.list_users()
            elif choice == '8':
                title = input("Enter book title (optional): ")
                author = input("Enter author (optional): ")
                category = input("Enter category (optional): ")
                library.find_book(title, author, category)
            elif choice == '9':
                library.generate_report()
            elif choice == '10':
                library.generate_statistics()
            elif choice == '11':
                library.save_data('library_data.json')
            elif choice == '12':
                print("Exiting the Library Management System.")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
