class NotificationTemplates:
    
    WAITLIST_ADDED = "You have been added to the waitlist for book: '{title}'."
    
    BOOK_AVAILABLE = "Good news! The book '{title}' is now available for pickup."
 
    FINE= "The book was marked as lost. Fine: {price:.2f} UAH."
    
    RETUTN = "The book has been successfully returned."

    BORROW = "You have successfully borrowed the book. Please return it by {formatted_date}."

    WAITLIST_END = "The book '{title}' you were waiting for is now available. Please visit the library to borrow it."

    SOON = "The loan period for '{title}' ends in 3 days. Please return the book."

    OVERDUE ="You missed the deadline for returning '{title}'. Please return the book and pay the fine."

    RENEWED = "Success! The loan period for '{title}' has been extended. New due date: {date}."

    WISHLIST_CREATED = "Your request to add the book '{title}' has been successfully submitted."

    WISHLIST_FULFILLED = "Good news! The book '{title}' is now available in the library. You can come and borrow it."