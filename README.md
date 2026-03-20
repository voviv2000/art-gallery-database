# art-gallery-database
Web app and Database for an art gallery using data from the National Gallery of Art's [Open Data](https://github.com/NationalGalleryOfArt/opendata/tree/main) Repository. The web app is relatively intuitive, but for more information on how webpage navigation works or what each page presents, look to the report in the repository. 

## Webapp Link
Hosted via Heroku.
**URL**: https://vivian-art-gallery-tamu-9131538c5461.herokuapp.com/


## Local Installation
My webapp is already hosted, so you can follow the URL above; however, if you want to go ahead and make your own app, follow these steps. 

1. **Clone Repository**:
''' git clone https://github.com/vvo5683/art-gallery-database.git
    cd art-gallery-database'''

2. **Install Dependencies**
'''pip install -r requirements.txt'''

3. **Configure Environment Variables**
Do this by creating your own .env file in the root directory with these variables filled:
* DB_NAME
* DB_USER
* DB_PASS
* DB_HOST
* DB_PORT

4. **Run Applicaiton**
''' streamlist run app.py'''
