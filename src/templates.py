class NotificationTemplates:

    WAITLIST_ADDED = "You have been added to the waitlist for book: '{title}'."

    BOOK_AVAILABLE = "Good news! The book '{title}' is now available for pickup."

    FINE= "The book was marked as lost. Fine: {price:.2f} UAH."

    RETUTN = "The book has been successfully returned."

    BORROW = "You have successfully borrowed the book. Please return it by {formatted_date}."

    WAITLIST_END = "The book '{title}' you were waiting for is now available. Please visit the library to borrow it."

    SOON = "The loan period for '{title}' ends in 3 days. Please return the book."

    OVERDUE ="You missed the deadline for returning '{title}'. Please return the book and pay the fine."
    WAITLIST_END = "The book you were waiting for is now available.Please visit the library to collect it."

    RENEWED = "Success! The loan period for '{title}' has been extended. New due date: {date}."
    SOON = "The loan period for this book ends in 3 days. Please return the book."

    WISHLIST_CREATED = "Your request to add the book '{title}' has been successfully submitted."
    OVERDUE ="You missed the deadline for returning the book. Please return the book and pay the fine."

    WISHLIST_FULFILLED = "Good news! The book '{title}' is now available in the library. You can come and borrow it."
    WELCOME = (
        "Welcome to the Library!\n\n"
        "Your account has been successfully created. "
        "You can now borrow books, join waitlists, and send wishlist requests."
    )