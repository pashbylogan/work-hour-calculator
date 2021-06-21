# Work Hour Calculator

Small project to calculate the number of hours I've worked throughout a given period.
This uses the Google Calendar API to search for events with a name (specified in config.yaml),
and then shows those events, the date and hour details, and the total number of hours. 

**Usage:**

        1. Create a python virtual environment and pip install the requirements. 
        2. Set parameters specific to you in config.yaml:
            - timezone (UTC)
            - string to search for in your calendar event titles
            - Date ranges of interest (mine are pay periods)
        3. Run with "python3 main.py"
