class NotificationTemplates:

    WAITLIST_ADDED = "You have been added to the waitlist for book: '{title}'."

    BOOK_AVAILABLE = "Good news! The book '{title}' is now available for pickup."

    FINE= "The book '{title}' was marked as lost. Fine: {price:.2f} UAH."

    RETURN = "'{title}' has been successfully returned."

    BORROW = "You have successfully borrowed '{title}'. Please return it by {formatted_date}."

    WAITLIST_END = "The book '{title}' you were waiting for is now available. Please visit the library to borrow it."

    SOON = "The loan period for '{title}' ends in 3 days. Please return the book."

    OVERDUE ="You missed the deadline for returning '{title}'. Please return the book and pay the fine."

    RENEWED = "Success! The loan period for '{title}' has been extended. New due date: {date}."

    WISHLIST_CREATED = "Your request to add the book '{title}' has been successfully submitted."

    WISHLIST_FULFILLED = "Good news! The book '{title}' is now available in the library. You can come and borrow it."

    WELCOME = (
        "Welcome to the Library!\n\n"
        "Your account has been successfully created. "
        "You can now borrow books, join waitlists, and send wishlist requests."
    )

    GOODBYE = ("Your account has been deleted."
               "We appreciate all the time you spent with us."
               "You can restore your account within 6 months.")

    GOODBYE_AFTER = ("Your account has been permanently deleted." 
                     "Thank you for spending time with us." 
                     "This time, goodbye forever.")

    RETURN = ("Welcome back, we are glad to see you again :)")