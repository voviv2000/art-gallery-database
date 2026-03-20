-- 1. Artists Table
CREATE TABLE Artist (
    artistID INT PRIMARY KEY,
    artistName VARCHAR(512) NOT NULL,
    birthplace VARCHAR(512),
    timePeriod VARCHAR(256),
    artType VARCHAR(256)
);

-- 2. Customers Table
CREATE TABLE Customer (
    customerID INT PRIMARY KEY,
    customerName VARCHAR(2048) NOT NULL,
    address TEXT,
    donationAmount DECIMAL(15, 2) DEFAULT 0.00,
    donationDate TIMESTAMP
);

-- 3. Exhibitions Table
CREATE TABLE Exhibition (
    exhibitionID INT PRIMARY KEY,
    exhibitionName VARCHAR(2048) NOT NULL,
    theme TEXT, -- Changed to TEXT for long museum descriptions
    startDate DATE,
    endDate DATE
);

-- 4. Category Table
CREATE TABLE Category (
    categoryID BIGINT PRIMARY KEY, -- Changed to BIGINT for NGA IDs
    categoryName VARCHAR(256) NOT NULL,
    timePeriod VARCHAR(256),
    artType VARCHAR(256)
);

-- 5. Artwork Table 
CREATE TABLE Artwork (
    artworkID INT PRIMARY KEY,
    title VARCHAR(2048) NOT NULL,
    creationYear VARCHAR(256),
    artType VARCHAR(256),
    medium TEXT,
    price DECIMAL(15, 2),
    artistID INT,
    -- canPurchase VARCHAR(32),
    customerID INT,
    FOREIGN KEY (artistID) REFERENCES Artist(artistID),
    FOREIGN KEY (customerID) REFERENCES Customer(customerID) -- Fixed singular name
);

-- 6. Linking Table: Displays
CREATE TABLE Displays (
    artworkID INT,
    exhibitionID INT,
    PRIMARY KEY (artworkID, exhibitionID),
    FOREIGN KEY (artworkID) REFERENCES Artwork(artworkID),
    FOREIGN KEY (exhibitionID) REFERENCES Exhibition(exhibitionID)
);

-- 7. Linking Table: Belongs
CREATE TABLE Belongs (
    artworkID INT,
    categoryID BIGINT, -- Must match Category(categoryID) type
    PRIMARY KEY (artworkID, categoryID),
    FOREIGN KEY (artworkID) REFERENCES Artwork(artworkID),
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID)
);

-- 8. Linking Table: Attends
CREATE TABLE Attends (
    customerID INT,
    exhibitionID INT,
    PRIMARY KEY (customerID, exhibitionID),
    FOREIGN KEY (customerID) REFERENCES Customer(customerID),
    FOREIGN KEY (exhibitionID) REFERENCES Exhibition(exhibitionID)
);

--- 9. Images table
CREATE TABLE IF NOT EXISTS published_images (
    uuid character varying(64) PRIMARY KEY,
    iiifurl character varying(512),
    iiifthumburl character varying(512),
    viewtype character varying(32),
    sequence character varying(32),
    width integer,
    height integer,
    maxpixels integer,
    openaccess integer NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone,
    depictstmsobjectid integer, -- This links to artworkID
    assistivetext text
);