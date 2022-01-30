# ChatBot

##Setting up the database
1. Download SQL EXPRESS or some other local SQL server host (Only available on windows any MYSQL database will do)
2. Create a new database ours is called "AIChatBot"
3. Clone or download our REPO 
4. Navigate to the SQL\Scripts directory and run all the scripts in there on the new database (this creates all the tables and stored procedures used)
5. Navigate to the SQL\InsertTableData directory and open the solution
6. Edit the connectionString in the appsettings.json  file
7. Run the console app (this should take about 15mins to insert all the data)

##Downloading and importing SpaCy
Use the following commands in terminal
1. import spacy
2. python -m spacy download en

Hopefully can remove this after charlies headless {
##Download chromedriver 
Install chromedriver to resources folder
1. Open https://sites.google.com/chromium.org/driver/downloads
2. Download chromedriver with the appropriate version of chrome used on your machine
3. Move chromedriver into the resources folder
For MAC:
4. Make sure chromedriver is executable 'ls -l ChatBot/resrouces/chromedriver'
5. If not executable 'chmod +x ChatBot/resources/chromedriver'
6. OSX may need further entitlements
For Windows:}


##Download requirements
1. pip install -r requirements.txt
