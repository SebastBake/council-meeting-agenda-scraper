from aus_council_scrapers.base import BaseScraper, ScraperReturn, register_scraper
from bs4 import BeautifulSoup
import re
from datetime import datetime


@register_scraper
class ManninghamScraper(BaseScraper):
    def __init__(self):
        council_name = "manningham"
        state = "VIC"
        base_url = "https://www.manningham.vic.gov.au"
        super().__init__(council_name, state, base_url)

    def scraper(self) -> ScraperReturn | None:
        initial_webpage_url = "https://www.manningham.vic.gov.au/about-council/how-council-works/council-meetings"

        # Find next meeting url
        raw_html = self.fetcher.fetch_with_requests(initial_webpage_url)
        init_soup = BeautifulSoup(raw_html, "html.parser")
        meeting_a = init_soup.find("div", class_="js-next-date-start").find_all("a")[-1]
        meeting_url = self.base_url + meeting_a["href"]

        # Parse html of next meeting
        meeting_html = self.fetcher.fetch_with_requests(meeting_url)
        meeting_soup = BeautifulSoup(meeting_html, "html.parser")

        # Extract different variables
        name_from_title = meeting_soup.find("h1", class_="page-title").text
        raw_date = re.search(self.date_regex, name_from_title).group()
        name = name_from_title.replace(raw_date, "").strip()
        location = (
            meeting_soup.find("p", class_="address").text.strip().replace("\n", " ")
        )

        datetime_str = meeting_soup.find("a", class_="js-ics-export")["data-ics-start"]
        datetime_dt = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
        date = datetime_dt.strftime("%Y-%m-%d")
        time = datetime_dt.strftime("%H:%M")

        download_url = meeting_soup.find("a", class_="file-link")["href"]

        return ScraperReturn(
            name=name,
            date=date,
            time=time,
            webpage_url=self.base_url,
            download_url=download_url,
            location=location,
        )


if __name__ == "__main__":
    scraper = ManninghamScraper()
    scraper.scraper()
