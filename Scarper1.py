import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import easygui


#def convert_relative_time_to_datetime(relative_time):
#    pattern = r'(\d+)\s+(hour|day|week|month|year)s? ago'
#    match = re.match(pattern, relative_time, re.IGNORECASE)
#    if match:
#        quantity, unit = match.groups()
#        quantity = int(quantity)
#        if unit == 'hour':
#            return datetime.now() - timedelta(hours=quantity)
#        elif unit == 'day':
#            return datetime.now() - timedelta(days=quantity)
#        elif unit == 'week':
#            return datetime.now() - timedelta(weeks=quantity)
#        elif unit == 'month':
#            return datetime.now() - timedelta(days=quantity * 30)
#        elif unit == 'year':
#            return datetime.now() - timedelta(days=quantity * 365)
#    return None



def recommend_jobs(df, location, job_type):
    # Filter jobs based on user preferences
    filtered_jobs = df[
        (df['Location'].str.contains(location, case=False)) &
        (df['Job Title'].str.contains(job_type, case=False))
        #(df['Experience Needed'].str.contains(experience, case=False))
    ]
    return filtered_jobs


def get_user_preferences():
    location = easygui.enterbox(msg='Enter your preferred location:', title='Location', default='', strip=True)
    job_type = easygui.enterbox(msg='Enter your preferred job type:', title='Job Type', default='', strip=True)
    #experience = easygui.enterbox(msg='Enter your preferred experience level:', title='Experience', default='', strip=True)
    return location, job_type

def get_job_info(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    jobs = []

    for job in soup.find_all('div', class_='css-pkv5jc'):
        job_title = job.find('h2', class_='css-m604qf').find('a').text.strip()
        company = job.find('div', class_='css-d7j1kk').find('a').text.strip()
        location = job.find('div', class_='css-d7j1kk').find('span', class_='css-5wys0k').text.strip()
        time_posted = job.find('div', class_='css-d7j1kk').find('div', class_='css-4c4ojb')#.text.strip()
        full_time = job.find('div', class_='css-y4udm8').find('span', string='Full Time')
        work_from_home = job.find('div', class_='css-y4udm8').find('span', string='Work From Home')
        experience = job.find('div', class_='css-y4udm8').find('span', href="/a/Experienced-Jobs-in-United-Arab-Emirates")

        # Convert relative 'Time Posted' to datetime
        #time_posted_text = time_posted.text.strip() if time_posted else 'Not Specified'
        #time_posted_datetime = convert_relative_time_to_datetime(time_posted_text)

        jobs_data = {
            'Job Title': job_title,
            'Company': company,
            'Location': location,
            'Time Posted': time_posted.text.strip() if time_posted else 'Not Specified',
            'Full Time': 'Yes' if full_time else 'No',
            'Work From Home': 'Yes' if work_from_home else 'No',
            'Experience Needed': experience.text.strip() if experience else 'Not Specified',
        }

        jobs.append(jobs_data)

    return jobs

def main():
    base_url = 'https://wuzzuf.net'
    #jobtype = input('What Job do you want to search for? \n')
    #pages_to_scrape = int(input('How many pages would you like to scrape? \n'))

    jobtype = easygui.enterbox(msg = 'What Job do you want to search for?', title = 'Job Name', default = 'Manager', strip = True)
    pages_to_scrape = easygui.integerbox("How many pages would you like to scrape?", "Page Count", lowerbound=1)

    all_jobs = []

    try:
        for page in range(pages_to_scrape):
            url = f"{base_url}/search/jobs/?q={jobtype}&a=hpb&start={page}"
            jobs = get_job_info(url)
            all_jobs.extend(jobs)

    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching the page:", e)
        return

    if not all_jobs:
        print("No job data found on the page.")
    else:
        # Convert the scraped job data to a DataFrame
        df = pd.DataFrame(all_jobs)
        #df2 = df.copy()

        location, job_type = get_user_preferences()
        recommended_jobs = recommend_jobs(df, location, job_type)

        output_file2 = f"{jobtype}_jobs_for_you.xlsx"
        recommended_jobs.to_excel(output_file2, index= False)
        print (f"Recommended jobs save to {output_file2}")

        # Save to Excel
        output_file = f"{jobtype}_jobs1.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Scraped job data saved to {output_file}")

main()
