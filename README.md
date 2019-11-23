# Amazon Review Downloader

# Disclaimer
Use at your own risk. I don't support scraping of any website or webservice without consent

Instructions:

extractProductIDsFromCategories.py -> Uses the Category URL's provided in the 'url_categories.txt' file to visit that URL and download all the product IDs to a tunable parameter and saves them in 'Categories' directory with each file contain product ids or one category

downloadAmazonReviews.py -> Uses the category files in the 'Categories' directory to send a request for 1) product name and then for a (tunable) number of times for the review of the product and stores them in csv format file in 'Reviews' Category in a similar manner



