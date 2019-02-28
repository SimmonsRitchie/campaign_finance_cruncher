## CAMPAIGN FINANCE CRUNCHER

A python script written to analyze campaign finance data during Pennsylvania 2018 election. It produces an excel spreadsheet that summarizes the data.

### About

The data is stored as text files and can be downloaded here: https://www.dos.pa.gov/VotingElections/CandidatesCommittees/CampaignFinance/Resources/Pages/FullCampaignFinanceExport.aspx

This script uses Pandas to clean, sort and group the data, with a particular focus on Pennsylvania's gubernatorial election. The script can easily be adapted to focus on other candidates.

It ultimately produces an excel spreadsheet that includes the following sheets:

    total_donations': ranks PACs by the total amount of donations they've recieved. Please note that this includes advocacy and party PACs (eg. REPUBLICAN STATE COMMITTEE OF PENNSYLVANIA) in addition to PACs for individual candidates.
    wolf_v_wagner : summarizes key data in Wagner and Wolf race
    wolf_top_donors: ranks top donors to Wolf
    wagner_top_donors: ranks top donors to Wagner
    wolf_all_donations: lists each individual donation to Wolf
    wagner_all_donations: lists each individual donation to Wagner
    info_on_each_filer': provides additional info on all the filers referenced in the 'total_donations' sheet.

### Author

Daniel Simmons-Ritchie, reporter the Patriot-News/PennLive.com

Last updated: Oct 26, 2018

About: 
