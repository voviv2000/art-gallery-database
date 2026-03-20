import pandas as pd
import numpy as np
import csv
import uuid
import random

from faker import Faker
from dateutil.relativedelta import relativedelta


# create dataframes from csvs
objects_df = pd.read_csv('../data/objects.csv')
constituents_df = pd.read_csv('../data/constituents.csv')
links_df = pd.read_csv('../data/objects_constituents.csv')
text_df = pd.read_csv('../data/objects_text_entries.csv')



'''HELPER FUNCTIONS'''
def generate_fake_location(locale='en_US'):
    """Generates a single fake address, city, state, and datetime."""
    fake = Faker(locale)
    
    return {
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "timestamp": fake.date_time_this_year()
    }


def generate_fake_date_range(min_months=1, max_months=6):
    """
    Generates a start and end date separated by a random number of months.
    Returns: (start_date, end_date) as datetime objects.
    """
    fake = Faker()
    
    # 1. Generate a random start date (e.g., within the last 2 years)
    start_date = fake.date_time_between(start_date='-2y', end_date='now')
    
    # 2. Pick a random number of months for the duration
    duration_months = random.randint(min_months, max_months)
    
    # 3. Calculate end date by adding the months
    end_date = start_date + relativedelta(months=duration_months)
    
    return start_date, end_date


def generate_id():
    """Generates a random UUID4 and returns it as an integer."""
    # uuid.uuid4() creates the object, .int converts it to a massive integer
    return random.randint(100_000_000, 2_147_483_647)


def generate_numeric_id():
    """Generates a unique ID based on the current timestamp in nanoseconds."""
    return random.randint(10_000_000, 99_999_999)


def generate_art_theme():
    """Generates a random string representing an art exhibition theme."""
    
    # Artistic movements or styles
    themes = [
        "Florals", "Black Culture", "Women in Art", "Landscapes", 
        "Portraits", "Urban Life", "Maritime History", "Abstract Forms",
        "The Human Condition", "Mythology", "Indigenous Art", "Architecture",
        "17th Century French", "Impressionism", "Modernism", "Baroque", 
        "Surrealism", "Renaissance", "Contemporary", "Post-Modern", 
        "Fauvism", "Expressionism", "Minimalism", "Romanticism"
    ]
    
    return f"{random.choice(themes)}"


def get_availability():
    """Returns a random string: either 'available' or 'unavailable'."""
    options = ["available", "unavailable"]
    return random.choice(options)


def clean_and_create_csvs():

    print('Cleaning Dataframes...\n')
    # clean dataframes into desired entities
    # Artist
    artist_df = constituents_df[constituents_df['artistofngaobject'] == 1].copy()
    artist_df = constituents_df[['constituentid', 'preferreddisplayname']]
    artist_df = pd.concat([artist_df, objects_df[['displaydate', 'visualbrowsertimespan', 'subclassification']]], axis=1)
    artist_df.columns = ['artistID', 'artistName', 'birthplace', 'period', 'artType']
    artist_df = artist_df.dropna(subset=['artistID', 'artistName']) # keep row if both exist

    # generate numeric id's
    for idx, row in artist_df.iterrows():
        artist_df.at[idx, 'artistID'] = generate_numeric_id()
    artist_df['artistID'] = artist_df['artistID'].round().convert_dtypes() # convert to ints
    artist_df = artist_df.drop_duplicates(subset=['artistID'])




    # Customers 
    #  use the link table to find people who gave art to the NGA
    donor_ids = links_df[links_df['roletype'] == 'donor']['constituentid'].unique()
    customer_df = constituents_df[constituents_df['constituentid'].isin(donor_ids)].copy()
    customer_df = customer_df[['constituentid', 'forwarddisplayname']].dropna()
    customer_df.columns = ['customerID', 'customerName']
    customer_df['address'] = None
    customer_df['donationAmount'] = None
    customer_df['donationDate'] = None

    # generate address and donations
    for idx, row in customer_df.iterrows():
        address_dict = generate_fake_location()
        customer_df.at[idx, 'address'] = address_dict['address']
        customer_df['donationAmount'] = np.random.uniform(500, 50000, size=len(customer_df)).round(2)
        customer_df.at[idx, 'donationDate'] = pd.to_datetime(address_dict['timestamp'])
        customer_df.at[idx, 'customerID'] = generate_id()





    # Artwork - still need price
    artwork_df = objects_df[objects_df['isvirtual'] == 0].copy()
    artwork_df = artwork_df[['objectid', 'title', 'displaydate', 'subclassification', 'medium']]
    artwork_df.columns = ['artworkID', 'title', 'creationYear', 'artType', 'medium']
    artwork_df = artwork_df.dropna()


    artwork_df['price'] = np.random.uniform(1000, 1000000, size=len(artwork_df)).round(2)

    # map artistID from the link table
    artist_map = links_df[links_df['roletype'] == 'artist'].groupby('objectid')['constituentid'].first()
    artwork_df['artistID'] = artwork_df['artworkID'].map(artist_map)

    valid_artist_ids = artist_df['artistID'].tolist()
    artwork_df['artistID'] = np.random.choice(valid_artist_ids, size=len(artwork_df))

    valid_customer_ids = customer_df['customerID'].tolist()
    artwork_df['customerID'] = np.random.choice(valid_customer_ids, size=len(artwork_df))

    # artwork_df['customerID'] = None
    # for idx, row in artwork_df.iterrows():
    #     artwork_df.at[idx, 'customerID'] = np.random.choice(customer_df['customerID'].values, size=len(artwork_df))

    artwork_df = artwork_df.dropna(subset=['artistID'])

    artwork_df['customerID'] = pd.to_numeric(artwork_df['customerID'], errors='coerce').astype('Int64')
    artwork_df['artistID'] = pd.to_numeric(artwork_df['artistID'], errors='coerce').astype('Int64')

    artwork_df['title'] = artwork_df['title'].str.replace(',', '')
    artwork_df['medium'] = artwork_df['medium'].str.replace(',', '')





    # Categories - create unique category list based on NGA classifications
    category_df = objects_df[['classification', 'visualbrowsertimespan', 'subclassification']].drop_duplicates()

    # generate an id
    category_df['classificationid'] = None
    for idx, row in category_df.iterrows():
        category_df.at[idx, 'classificationid'] = generate_id()

    # move id column to front
    category_df.insert(0, 'classificationid', category_df.pop('classificationid'))
    category_df = category_df.dropna()

    # rename columns
    category_df.columns = ['categoryID', 'categoryName', 'period', 'artType']
    category_df = category_df.dropna(subset=['categoryID'])




    # Exhibitions - filter text entries for exhibition history
    ex_data = text_df[text_df['texttype'] == 'exhibition_history'].copy()

    # simplify and treat each unique year/text combo as an event
    exhibition_df = ex_data[['text', 'year']].drop_duplicates().head(500) 
    exhibition_df['exhibitionID'] = range(1, len(exhibition_df) + 1)
    exhibition_df.columns = ['exhibitionName', 'theme', 'exhibitionID']
    exhibition_df['startDate'] = None
    exhibition_df['endDate'] = None

    # generate random start and end dates for exhibition
    for idx, row in exhibition_df.iterrows():
        start, end = generate_fake_date_range()
        exhibition_df.at[idx, 'startDate'] = start
        exhibition_df.at[idx, 'endDate'] = end
        exhibition_df.at[idx, 'theme'] = generate_art_theme()


    # move id column to front
    exhibition_df.insert(0, 'exhibitionID', exhibition_df.pop('exhibitionID'))
    exhibition_df = exhibition_df.dropna()


    # Relationship Tables 

    # Displays (Artwork <-> Exhibition)
    displays_df = artwork_df[['artworkID', 'artworkID']].copy() # temp copy to get structure
    displays_df.columns = ['artworkID', 'temp'] 
    displays_df['exhibitionID'] = np.random.choice(exhibition_df['exhibitionID'], size=len(displays_df))
    displays_df = displays_df[['artworkID', 'exhibitionID']].drop_duplicates()



    # Belongs (Artwork <-> Category)
    belongs_df = artwork_df[['artworkID']].copy()
    belongs_df['categoryID'] = np.random.choice(category_df['categoryID'], size=len(belongs_df))
    belongs_df = belongs_df.dropna()



    # Attends (Customer <-> Exhibition)
    attends_df = pd.DataFrame()
    attends_df = pd.concat([attends_df, customer_df[['customerID']]], axis=1)
    attends_df['exhibitionID'] = np.random.choice(exhibition_df['exhibitionID'], size=len(attends_df))
    attends_df = attends_df.dropna(subset=['customerID', 'exhibitionID'])


    '''
        UNCOMMENT WHEN YOU WANT RUN AND DOWNLOAD CSV
    '''
    print('Converting Dataframes to CSVs...\n')
    artist_df.to_csv('../data/artists.csv', index=False)
    artwork_df.to_csv('../data/artwork.csv', index=False, quoting=1, float_format='%.0f')
    customer_df.to_csv('../data/customers.csv', index=False, float_format='%.0f')
    exhibition_df.to_csv('../data/exhibitions.csv', index=False)
    category_df.to_csv('../data/categories.csv', index=False)
    displays_df.to_csv('../data/displays.csv', index=False, float_format='%.0f')
    belongs_df.to_csv('../data/belongs.csv', index=False, float_format='%.0f')
    attends_df.to_csv('../data/attends.csv', index=False, float_format='%.0f')

    print('Done!\n')


'''
Main Method
'''
if __name__ == "__main__":
    clean_and_create_csvs()