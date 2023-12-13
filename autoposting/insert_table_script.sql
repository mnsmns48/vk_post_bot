INSERT INTO posts (id, signer_id, signer_name, phone_number)
SELECT id, user_id, full_name, phone_number from people 