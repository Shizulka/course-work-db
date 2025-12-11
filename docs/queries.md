BEGIN; 

WITH closed_loan AS (

    UPDATE checkout
    SET 
        end_time = NOW(),     
        status = 'Overdue'::status_type 
    WHERE 
        book_copy_id = 2           
        AND end_time IS NULL        
    RETURNING patron_id, book_copy_id  
)


INSERT INTO notification (patron_id, contents)
SELECT 
    patron_id, 
    'Шановний читач! Ви повідомили про втрату книги (Копія #' || book_copy_id || '). Вам нараховано штраф 200 грн'

COMMIT;

шираф книги
