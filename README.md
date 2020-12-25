![Header](visuals/ladot.png)

# LADOT COVID19 Enforcement
## About the Project
### Goal
Using Los Angeles parking citation data, social media data, and city council records the aim of this project is to analyze the city's transition plan to resume street sweeper services on 10/15/2020. 

### Background


### Deliverables
- [Tablaeu Map](https://public.tableau.com/profile/promeos#!/vizhome/LADOTCOVID19StreetSweeperCitations/enforcement-10152020?publish=yes)
- [MVP Notebook](https://github.com/Promeos/LADOT-COVID19-enforcement/blob/main/MVP.ipynb)
- [Final Notebook](https://github.com/Promeos/LADOT-COVID19-enforcement/blob/main/summary.ipynb)
- [Slide Presentation](https://www.canva.com/design/DAERUYKNmnQ/0g_1Ed6ynJUkhXlPImCR9w/view?utm_content=DAERUYKNmnQ&utm_campaign=designshare&utm_medium=link&utm_source=sharebutton)
- Video presentation

### Project Management
- [Trello Board](https://trello.com/b/A1KCGKQN/ladot-covid19-enforcement)

### Acknowledgments
This dataset is maintained using Socrata's API and Kaggle's API. Socrata has assisted countless organizations with hosting their open data and has been an integral part of the process of bringing more data to the public.<br><br>

Download Los Angeles City Council documents [here](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?fa=ccfi.viewrecord&cfnumber=20-1365).

## Data Dictionary
| Feature Name           | Description                                                                        |
|------------------------|------------------------------------------------------------------------------------|
| issue_date             | The date the citation was issued. yyyy-mm-dd date format                           |
| issue_time             | The time the citation was issued. HH-MM-ss time format, 24hrs.                     |
| rp_state_plate         | The state license plate. Abbreviated format ex.CA, TX                              |
| plate_expiry_date      | The date the license plates expire.yyyy-mm-dd date format                          |
| make                   | Indicates the car manufacturer ex. NISS is Nissan.                                 |
| body_style             | Indicates the body style of the car. PA is a Passenger vehicle with four doors.    |
| color                  | The color of the vehicle.                                                          |
| location               | The street number and street name the citation was issued.                         |
| route                  | Indicates the section of the city where the citation was issued.                   |
| agency                 | The agency that issued the citation. See city-documents/LADOT/agency-names.pdf     |
| violtion_code          | The Alpha-numeric code used to indicate the type of violation.                     |
| violation_description  | Short description of the parking citation.                                         |
| fine_amount            | The amount of the citation.                                                        |
| latitude               | The latitude of the citation location.                                             |
| longitude              | The longitude of the citaiton location.                                            |
| day_of_week            | The day of the week the citation was issued.                                       |
| issue_year             | The year the citation was issued.                                                  |
| issue_hour             | The hour the citation was issued.                                                  |
| issue_minute           | The minute the citation was issued.                                                |


## Initial Thoughts & Hypotheses
### Thoughts


### Hypotheses

## Project Steps
### Acquire
Download the dataset [here](https://www.kaggle.com/cityofLA/los-angeles-parking-citations/discussion). The data is stored in a file named `parking-citations.csv`. The file contains approximately 7 years worth of parking citations issued in Los Angeles, California.

[Placeholder: Web Scraping]

### Prepare
**Missing Values**
- Dropped rows missing latitude and longitude data. 99999.0 indicates null.
- Dropped rows missing license plate expiration date.
- Dropped columns: vin, marked_time, color_description, body_style_description, agency_description, meter_id, ticker_number
- Dropped rows with missing values.

**Data Type Casting, Metric Conversion, and Formatting**
- Converted all numeric date columns to datetime.
- Converted issue_time from a float to TimeStamp.
- Converted agency from a float to an integer.
- Converted latitude amd longitude values from US Feet coordinates \[NAD1983StatePlaneCaliforniaVFIPS0405_Feet projection] to standard coordinates.
  - Used folium and pyproj library to convert the coordinates.
- Removed capitalization and spacing from column names.
  
**Feature Engineering**
- Created a new column called `day_of_week`.
- Created a new column called `issue_year`.
- Created a new column called `issue_hour`.
- Created a new column called `issue_minute`.

[Placeholder: Prep Web Scraped Data]

### Explore


### Conclusions


### Future Investigations
#### What are your next steps?
- A
- B
- C

## How to Reproduce
All files are reproducible and available for download and use.
- [x] Read this README.md
- [ ] Clone this repository
- [ ] Acquire the dataset from [Kaggle](https://www.kaggle.com/cityofLA/los-angeles-parking-citations?select=LADOT-Xerox+Crib+Sheet+Agency+Codes+12-31-2015+%281%29.pdf).
- [ ] Run Summary.ipynb

### Tools & Requirements
