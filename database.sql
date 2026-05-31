DROP DATABASE IF EXISTS shoes;
CREATE DATABASE shoes;
USE shoes;

CREATE TABLE roles (
    role_id INT PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    full_name VARCHAR(150),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE statuses (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name VARCHAR(50) NOT NULL
);

CREATE TABLE pickup_points (
    pickup_point_id INT PRIMARY KEY AUTO_INCREMENT,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(100) NOT NULL
);

CREATE TABLE manufacturers (
    manufacturer_id INT PRIMARY KEY AUTO_INCREMENT,
    manufacturer_name VARCHAR(100) NOT NULL
);

CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE units (
    unit_id INT PRIMARY KEY AUTO_INCREMENT,
    unit_name VARCHAR(20) NOT NULL
);

CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    article VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    unit_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    supplier_id INT NOT NULL,
    manufacturer_id INT NOT NULL,
    category_id INT NOT NULL,
    sale INT DEFAULT 0,
    stock INT DEFAULT 0,
    description TEXT,
    image_path VARCHAR(500),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    status_id INT NOT NULL,
    pickup_point_id INT NOT NULL,
    order_date DATE,
    delivery_date DATE,
    items TEXT,
    user_id INT NOT NULL,
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(pickup_point_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);