-- Create wordpress database and user
CREATE DATABASE wordpress;
CREATE USER 'wordpress'@'%' IDENTIFIED BY 'wordpress-password';
GRANT ALL ON wordpress.* TO 'wordpress'@'%';

-- Create redmine database and user
CREATE DATABASE redmine;
CREATE USER 'redmine'@'%' IDENTIFIED BY 'redmine-password';
GRANT ALL ON redmine.* TO 'redmine'@'%';