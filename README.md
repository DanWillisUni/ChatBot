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

##en_core_web
1. en_core_web_sm must be installed using:
   1. python -m spacy download en_core_web_sm


##Download requirements
1. pip install -r requirements.txt

Must have Firefox downloaded and installed on the computer

##To run
1. In CMD run: ngrok http 5000
2. Edit the callback URL for the facebook page to the https tunneled by ngrok
3. Start the FbMessenger.py
4. Send your first message in the chat
5. Start Engine.py


