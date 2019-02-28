## CAMPAIGN FINANCE CRUNCHER

This program was used to scrape and analyze campaign finance data during Pennsylvania 2018 election.

The program downloads data from Pa.'s Dept of State website then uses pandas to analyze the date, with a particular focus on the gubernatorial race between Democrat Tom Wolf and Republican Scott Wagner.
 
It then produces an excel spreadsheet that summarizes the data.

### About

The raw campaign finance data is stored as text files and can be downloaded here: https://www.dos.pa.gov/VotingElections/CandidatesCommittees/CampaignFinance/Resources/Pages/FullCampaignFinanceExport.aspx

The script can easily be adapted to focus on other candidates.

In its current form it produces an excel file with the following sheets:

    total_donations': ranks PACs by the total amount of donations they've recieved. Please note that this includes advocacy and party PACs (eg. REPUBLICAN STATE COMMITTEE OF PENNSYLVANIA) in addition to PACs for individual candidates.
    wolf_v_wagner : summarizes key data in Wagner and Wolf race
    wolf_top_donors: ranks top donors to Wolf
    wagner_top_donors: ranks top donors to Wagner
    wolf_all_donations: lists each individual donation to Wolf
    wagner_all_donations: lists each individual donation to Wagner
    info_on_each_filer': provides additional info on all the filers referenced in the 'total_donations' sheet.

### Author

Daniel Simmons-Ritchie, reporter the Patriot-News/PennLive.com


