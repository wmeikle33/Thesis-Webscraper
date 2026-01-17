## Quickstart

### Prerequisites
- Python 3.10+
- Chrome/Chromium (Selenium will use it)

### Install
```bash
git clone https://github.com/wmeikle33/Thesis-Webscraper.git
cd Thesis-Webscraper
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt

```

## Repository Structure

The project is organized into the following directories:

```bash
.
├── src/            # Source code for the application
├── docs/           # Project documentation and guides
├── test/           # Automated tests (unit, integration)
├── build/          # Compiled output files (usually excluded from git)
├── .github/        # GitHub specific configurations (workflows, templates)
├── LICENSE         # Project license file
└── README.md       # The main information file (this file)
```

# Thesis Webscraper
  This is my code for the master's thesis. Specifically, this code was used to collect blog post texts from the website Autohome, one of the leading sites for automobile consumers in China.The premise of my thesis is write a web scraping program that collects consumer posted blog content from Chinese websites pertaining to foreign made EV models currently available in the Chinese market. Specifically, the title of the blog post was collected, the main body content as well as the comments. I then measure how many times certain words associated with EV adoption are mentioned in this text, using the findings to generate a principal component regression vis a visa company stock returns to provide an assessmenet and general market insight of the potential of the Chinese EV market for foreign companes. Specifically, after the principal component regressionw as completed, the text valuues for with the highest eigenvectors for each principal component were extracted. Based on these text values, it was then determined which factors affecting EV adoption were the most important for Chinese consumers. Below is a graph depicting the various categories of text variables that were used in the analysis. 



<img width="478" height="596" alt="Screenshot 2025-09-08 at 8 17 46 PM" src="https://github.com/user-attachments/assets/f726ed40-30c0-401e-88f4-764f857b3c01" />

It should be noted that this project was developed using Selenium 3.141.0. Update to Selenium 4+ requires migration of element selection methods.

# Expansions

