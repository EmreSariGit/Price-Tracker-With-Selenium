CREATE TABLE Users(
    username VARCHAR(255) NOT NULL,
    mail VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY(username)
);
ALTER TABLE
    Users ADD UNIQUE users_mail_unique(mail);

CREATE TABLE Products (
    id INTEGER NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    product_image_link VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_price VARCHAR(255) NOT NULL,
    product_link VARCHAR(255) NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (username) REFERENCES Users(username)
);
