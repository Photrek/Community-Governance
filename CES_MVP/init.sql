-- Create tables form csv files
CREATE TABLE user AS SELECT * FROM read_csv('./data/users.csv');
CREATE TABLE question AS SELECT * FROM read_csv('./data/questions.csv');

-- join table between user - question
CREATE TABLE answer AS SELECT * FROM read_csv('./data/answers.csv');

-- join table between user - wallet
CREATE TABLE wallet_link AS SELECT * FROM read_csv('./data/wallet-links.csv');