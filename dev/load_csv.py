"""
Load mock csv data into Postgres database.
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from db import get_connection

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

CSV_DIR = ROOT_DIR / "dev" / "csv_data"

def main():
    pass

def drop_all(current):
    pass

def copy_table(current, table_name):
    pass


# Statements

# Drop in reverse FK dependency order to avoid constraint violations.
DROP_STATEMENTS = [
    "DROP TABLE IF EXISTS order_items",
    "DROP TABLE IF EXISTS stocks",
    "DROP TABLE IF EXISTS orders",
    "DROP TABLE IF EXISTS products",
    "DROP TABLE IF EXISTS staffs",
    "DROP TABLE IF EXISTS brands",
    "DROP TABLE IF EXISTS categories",
    "DROP TABLE IF EXISTS customers",
    "DROP TABLE IF EXISTS stores",
]

# Each tuple is (table_name, ddl). The list order drives both CREATE and COPY.
CREATE_STATEMENTS = [
    ("brands", """
        CREATE TABLE brands (
            brand_id   INTEGER      NOT NULL,
            brand_name VARCHAR(255) NOT NULL,
            CONSTRAINT pk_brands PRIMARY KEY (brand_id)
        )
    """),

    ("categories", """
        CREATE TABLE categories (
            category_id   INTEGER      NOT NULL,
            category_name VARCHAR(255) NOT NULL,
            CONSTRAINT pk_categories PRIMARY KEY (category_id)
        )
    """),

    ("customers", """
        CREATE TABLE customers (
            customer_id INTEGER      NOT NULL,
            first_name  VARCHAR(255) NOT NULL,
            last_name   VARCHAR(255) NOT NULL,
            phone       VARCHAR(25),
            email       VARCHAR(255) NOT NULL,
            street      VARCHAR(255),
            city        VARCHAR(50),
            state       CHAR(2),
            zip_code    VARCHAR(10),
            CONSTRAINT pk_customers PRIMARY KEY (customer_id)
        )
    """),

    ("stores", """
        CREATE TABLE stores (
            store_id   INTEGER      NOT NULL,
            store_name VARCHAR(255) NOT NULL,
            phone      VARCHAR(25),
            email      VARCHAR(255),
            street     VARCHAR(255),
            city       VARCHAR(50),
            state      CHAR(2),
            zip_code   VARCHAR(10),
            CONSTRAINT pk_stores PRIMARY KEY (store_id)
        )
    """),

    # manager_id FK is DEFERRABLE INITIALLY DEFERRED so Postgres only validates
    # it at commit time — allowing COPY to load all staff rows in one pass.
    ("staffs", """
        CREATE TABLE staffs (
            staff_id   INTEGER      NOT NULL,
            first_name VARCHAR(50)  NOT NULL,
            last_name  VARCHAR(50)  NOT NULL,
            email      VARCHAR(255) NOT NULL UNIQUE,
            phone      VARCHAR(25),
            active     SMALLINT     NOT NULL,
            store_id   INTEGER      NOT NULL,
            manager_id INTEGER,
            CONSTRAINT pk_staffs         PRIMARY KEY (staff_id),
            CONSTRAINT fk_staffs_store   FOREIGN KEY (store_id)
                REFERENCES stores(store_id),
            CONSTRAINT fk_staffs_manager FOREIGN KEY (manager_id)
                REFERENCES staffs(staff_id)
                DEFERRABLE INITIALLY DEFERRED
        )
    """),

    ("products", """
        CREATE TABLE products (
            product_id   INTEGER       NOT NULL,
            product_name VARCHAR(255)  NOT NULL,
            brand_id     INTEGER       NOT NULL,
            category_id  INTEGER       NOT NULL,
            model_year   SMALLINT      NOT NULL,
            list_price   NUMERIC(10,2) NOT NULL,
            CONSTRAINT pk_products          PRIMARY KEY (product_id),
            CONSTRAINT fk_products_brand    FOREIGN KEY (brand_id)
                REFERENCES brands(brand_id),
            CONSTRAINT fk_products_category FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """),

    ("orders", """
        CREATE TABLE orders (
            order_id      INTEGER  NOT NULL,
            customer_id   INTEGER  NOT NULL,
            order_status  SMALLINT NOT NULL,
            order_date    DATE     NOT NULL,
            required_date DATE     NOT NULL,
            shipped_date  DATE,
            store_id      INTEGER  NOT NULL,
            staff_id      INTEGER  NOT NULL,
            CONSTRAINT pk_orders          PRIMARY KEY (order_id),
            CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id),
            CONSTRAINT fk_orders_store    FOREIGN KEY (store_id)
                REFERENCES stores(store_id),
            CONSTRAINT fk_orders_staff    FOREIGN KEY (staff_id)
                REFERENCES staffs(staff_id)
        )
    """),

    ("stocks", """
        CREATE TABLE stocks (
            store_id   INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity   INTEGER NOT NULL,
            CONSTRAINT pk_stocks         PRIMARY KEY (store_id, product_id),
            CONSTRAINT fk_stocks_store   FOREIGN KEY (store_id)
                REFERENCES stores(store_id),
            CONSTRAINT fk_stocks_product FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
    """),

    ("order_items", """
        CREATE TABLE order_items (
            order_id   INTEGER       NOT NULL,
            item_id    INTEGER       NOT NULL,
            product_id INTEGER       NOT NULL,
            quantity   INTEGER       NOT NULL,
            list_price NUMERIC(10,2) NOT NULL,
            discount   NUMERIC(4,2)  NOT NULL DEFAULT 0,
            CONSTRAINT pk_order_items         PRIMARY KEY (order_id, item_id),
            CONSTRAINT fk_order_items_order   FOREIGN KEY (order_id)
                REFERENCES orders(order_id),
            CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
    """),
]