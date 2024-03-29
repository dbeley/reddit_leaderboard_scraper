"""
Extracts subreddits from the new reddit leaderboard pages.
"""
import json
import logging
import time
import argparse
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger()
TEMPS_DEBUT = time.time()
AUJ = datetime.datetime.now().strftime("%Y-%m-%d")

# Categories to NOT extract
BLACKLISTED_CATEGORIES = [
    # "all communities",
    # "sports",
    # "gaming",
    # "news",
    # "tv",
    # "aww",
    # "memes",
    # "pics & gifs",
    # "travel",
    # "tech",
    # "music",
    # "art & design",
    # "beauty",
    # "books & writing",
    # "crypto",
    # "discussion",
    # "fashion",
    # "finance & business",
    # "food",
    # "health & fitness",
    # "learning",
    # "mindblowing",
    # "outdoors",
    # "parenting",
    # "photography",
    # "relationships",
    # "science",
    # "video games",
    # "videos",
    # "vroom",
    # "wholesome",
]


def get_soup(browser):
    return BeautifulSoup(browser.page_source, "lxml")


def get_empty_dict(soup):
    # List categories contained in soup object
    list_dict_cat = [
        {
            "category": cat.text,
            "url": "https://www.reddit.com" + cat["href"],
            "subreddits": [],
        }
        for cat in soup.find_all("a", {"class": "_3p0xqZowgYYjYMOdinU151"})
        if cat.text not in BLACKLISTED_CATEGORIES
    ]
    return list_dict_cat


def main():
    args = parse_args()

    options = Options()
    options.headless = args.no_headless
    browser = webdriver.Firefox(options=options)
    url = "https://www.reddit.com/subreddits/leaderboard/"
    browser.get(url)

    Path("Exports").mkdir(parents=True, exist_ok=True)

    try:
        with open("Exports/subreddits_list.txt", "r") as f:
            subreddits = [x.strip() for x in f.readlines()]
    except Exception as e:
        logger.warning("File subreddits_list.txt not found : %s.", e)
        subreddits = []

    # Click on show more to display all categories
    try:
        browser.find_element_by_class_name("_1McO-Omm_mC2bkTnVgD6NV").click()
        logger.debug('Clicked on "Show More" button.')
    except Exception as e:
        logger.debug("button show more not found : %s.", e)

    soup = get_soup(browser)

    list_dict_cat = get_empty_dict(soup)

    # Results for each category (max 25)
    for cat in list_dict_cat:
        logger.info(
            "Retrieving top communities in category %s.", cat["category"]
        )
        browser.get(cat["url"])

        time.sleep(2)
        # Uncomment to have more than 25 subreddits
        # Scroll to bottom of page
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(2)

        soup = get_soup(browser)

        for index, li in enumerate(
            soup.find_all("li", {"class": "_267lcOmg8VvXcoj9O0Q1TB"}), 1
        ):
            logger.debug(
                "%s - %s : %s", cat["category"], index, li.find("a")["href"]
            )
            cat["subreddits"].append(li.find("a")["href"])
        logger.info("%s communities found.", len(cat["subreddits"]))

    # Creating json object for the day
    day_result = {"day": AUJ, "leaderboard": list_dict_cat}

    # Exporting json for the day
    with open(f"Exports/results_{AUJ}.json", "w") as f:
        json.dump(day_result, f, indent=4)

    # Complete subreddit list
    # Changing format to keep just the lowercase subreddit name
    subreddits = subreddits + [
        y.lower()[3:-1] for x in list_dict_cat for y in x["subreddits"]
    ]
    orig_length = len(subreddits)
    subreddits = list(set(subreddits))
    logger.info(
        f"Complete subreddit list : {orig_length - len(subreddits)} duplicates subreddits found. Deleting."
    )
    with open("Exports/subreddits_list.txt", "w") as f:
        for i in subreddits:
            f.write(f"{i}\n")

    logger.debug("Closing Selenium Browser.")
    browser.close()
    browser.quit()
    logger.info("Runtime : %.2f seconds." % (time.time() - TEMPS_DEBUT))


def parse_args():
    format = "%(levelname)s :: %(message)s"
    parser = argparse.ArgumentParser(
        description="Extracts subreddits from the new reddit leaderboard pages."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "positional_argument", nargs="?", type=str, help="Positional argument"
    )
    parser.add_argument(
        "--no_headless",
        help="Disable headless mode for the selenium browser.",
        dest="no_headless",
        action="store_false",
    )
    parser.set_defaults(no_headless=True)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format=format)
    return args


if __name__ == "__main__":
    main()
