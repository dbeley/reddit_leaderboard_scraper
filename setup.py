import setuptools
import reddit_leaderboard_scraper

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="reddit_leaderboard_scraper",
    version=reddit_leaderboard_scraper.__version__,
    author="dbeley",
    author_email="dbeley@protonmail.com",
    description="Extract subreddits from the new reddit leaderboard.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbeley/reddit_leaderboard_scraper",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "reddit_leaderboard_scraper=reddit_leaderboard_scraper.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["beautifulsoup4", "requests", "lxml", "selenium"],
)
