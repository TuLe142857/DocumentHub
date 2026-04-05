CREATE DATABASE IF NOT EXISTS db_test;
CREATE USER 'user_test'@'%' IDENTIFIED BY 'password_test';
GRANT ALL PRIVILEGES ON db_test.* TO 'user_test'@'%';