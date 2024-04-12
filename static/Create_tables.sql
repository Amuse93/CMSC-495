CREATE TABLE Product (
    ProductID varchar NOT NULL,
    Product_Name varchar(50) NOT NULL,
    Price float NOT NULL,
    Total_In_Stock NOT NULL,
    PRIMARY KEY (ProductID)
    );

CREATE TABLE Users (
    EmployeeID int NOT NULL,
    Username varchar(63),
    Password varchar(63),
    First_Name char(60),
    Last_Name char(60),
    DOB date,
    Phone_Number varchar(15),
    Position char(30),
    First_Time int CHECK (First_Time IN (0, 1)),
    Number_Of_Tries int,
    PRIMARY KEY (EmployeeID)
    );

-- Removed Product data as it has a many-to-many relationship.
CREATE TABLE Shelf (
    ShelfID varchar NOT NULL,
    PRIMARY KEY (ShelfID)
    );

-- Shelf_Product: Can store many products per shelf and multiple shelves can have the same product.
CREATE TABLE Shelf_Product(
    ShelfID varchar,
    ProductID varchar,
    Quantity int,
    FOREIGN KEY (ShelfID) REFERENCES Shelf(ShelfID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    PRIMARY KEY (ShelfID, ProductID)
    );
    
CREATE TABLE Sales (
    SaleID varchar NOT NULL,
    EmployeeID int NOT NULL,
    Total_Price float NOT NULL,
    Date date NOT NULL,
    PRIMARY KEY (SaleID),
    FOREIGN KEY (EmployeeID) REFERENCES Users(EmployeeID)
    );

CREATE TABLE Sales_Products (
    SaleID varchar NOT NULL,
    ProductID varchar NOT NULL,
    Product_Quantity int NOT NULL,
    PRIMARY KEY (SaleID, ProductID),
    FOREIGN KEY (SaleID) REFERENCES Sales(SaleID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
    );
    
-- Added the EmployeeID as an FK.
CREATE TABLE Waste_Reports (
    Report_Number varchar NOT NULL,
    ProductID varchar NOT NULL,
    Quantity int NOT NULL,
    ReasonCode int NOT NULL,
    Date date NOT NULL,
    Description varchar(255),
    EmployeeID int,
    PRIMARY KEY (Report_Number),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (EmployeeID) REFERENCES Users(EmployeeID)
    );

/*Default Admin account. Password is 'password'
Will be deleted after first account creation */

INSERT INTO Users
VALUES (
    1,
    'admin',
    '$5$rounds=535000$TMHik1MkhXyuoeyT$tgAheEu3MW9J3BofMXEVsoKa0VkEoa1V72YsrtnTQJ8',
    'default',
    'admin',
    '2024-03-28',
    '555-555-5555',
    'Manager',
    0,
    0
    );