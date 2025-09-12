# Thesis Webscraper
  This is my code for the master's thesis. Specifically, this code was used to collect blog post texts from the website Autohome, one of the leading sites for automobile consumers in China.The premise of my thesis is write a web scraping program that collects consumer posted blog content from Chinese websites pertaining to foreign made EV models currently available in the Chinese market. Specifically, the title of the blog post was collected, the main body content as well as the comments. I then measure how many times certain words associated with EV adoption are mentioned in this text, using the findings to generate a principal component regression vis a visa company stock returns to provide an assessmenet and general market insight of the potential of the Chinese EV market for foreign companes. Specifically, after the principal component regressionw as completed, the text valuues for with the highest eigenvectors for each principal component were extracted. Based on these text values, it was then determined which factors affecting EV adoption were the most important for Chinese consumers. Below is a graph depicting the various categories of text variables that were used in the analysis. 



<img width="478" height="596" alt="Screenshot 2025-09-08 at 8 17 46 PM" src="https://github.com/user-attachments/assets/f726ed40-30c0-401e-88f4-764f857b3c01" />

It should be noted that this project was developed using Selenium 3.141.0. Update to Selenium 4+ requires migration of element selection methods.

Ethics & Compliance
Legal & Terms of Service
This code was developed for academic research (Master’s thesis) and is provided for educational purposes only.
Before running the scraper, check and comply with the Terms of Service (ToS) and robots.txt of the target website(s).
The authors do not encourage scraping in violation of site policies or applicable laws.
Politeness & Fair Use
The scraper introduces delays between requests to avoid overloading servers.
Please configure reasonable backoff intervals (e.g., 1–2 seconds per request).
Do not run high-concurrency scraping or large-scale crawls against Autohome or other sites.
Data Privacy
Scraped content may include user-generated data such as comments, usernames, and timestamps.
This project does not attempt to deanonymize users or collect personally identifiable information (PII).
Any analysis or publication of results should use aggregated and anonymized data only.
Transparency & Attribution
When sharing or publishing results derived from scraped data:
Cite the source site clearly.
Describe your data collection window and methods (e.g., frequency, filters).
Acknowledge the limitations and ethical considerations.
Responsible Use
Do not use this project for:
Commercial resale of scraped data
Mass harvesting of user profiles
Activities that violate privacy, local laws, or data protection regulations (e.g., GDPR)
Disclaimer: This scraper was built solely for academic research into EV adoption trends (Master’s thesis, 2023). The authors do not endorse or permit the use of this code for unlawful purposes. By using this repository, you agree to ensure your usage complies with relevant laws, data protection standards, and the Terms of Service of the websites you access.
