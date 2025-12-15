class NotificationTemplates:
    WAITLIST_ADDED = "You have been added to the waitlist for book: '{title}'."
    
    BOOK_AVAILABLE = "Good news! The book '{title}' is now available for pickup."
 
    FINE= "The book was marked as lost. Fine: {price:.2f} UAH."
    
    RETUTN = "The book has been successfully returned."

    BORROW = "You have successfully borrowed the book. Please return it by {formatted_date}."

    WAITLIST_END = "The book you were waiting for is now available.Please visit the library to collect it."

    SOON = "The loan period for this book ends in 3 days. Please return the book."

    OVERDUE ="You missed the deadline for returning the book. Please return the book and pay the fine."