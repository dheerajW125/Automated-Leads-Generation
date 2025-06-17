import datetime as dt
import logging
import random
import string
from typing import Optional
from requests.exceptions import HTTPError, RequestException
from time import sleep
# import requests
from curl_cffi import requests
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator, ValidationError, Field

logger = logging.getLogger(__name__)

false = False


class Organization(BaseModel):
    name: str
    domain: Optional[str]
    website_url: Optional[HttpUrl]
    logo_url: Optional[HttpUrl]
    id: str


class OrganizationUrl(BaseModel):
    website_url : Optional[HttpUrl]

class Person(BaseModel):
    id: str
    first_name: str
    last_name: str
    linkedin_url: Optional[HttpUrl]
    title: Optional[str]
    email_status: str
    photo_url: Optional[HttpUrl]
    email: Optional[EmailStr]
    company: Optional[str]
    organization_id: Optional[str]
    # organization_website_url: Optional[HttpUrl] = Field(None, alias='organization.website_url')
    # organization: Optional[OrganizationUrl] 

    @field_validator("email")
    def validate_email(cls, email):
        if email == "email_not_unlocked@domain.com":
            return None
        return email


class Person_email(BaseModel):
    id: str
    first_name: str
    last_name: str
    linkedin_url: Optional[HttpUrl]
    title: Optional[str] 
    email_status: str
    photo_url: Optional[HttpUrl]
    email: Optional[EmailStr]
    # organization: Optional[OrganizationUrl]
    # company: Optional[str]

    @field_validator("email")
    def validate_email(cls, email):
        if email == "email_not_unlocked@domain.com":
            return None
        return email


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


class ApolloClient:
    BASE_URL = "https://app.apollo.io"
    ENDPOINT_AUTH_CHECK = "/api/v1/auth/check"
    ENDPOINT_AUTH_LOGIN = "/api/v1/auth/login"
    ENDPOINT_ORG_SEARCH = "/api/v1/organizations/search"
    ENDPOINT_PEOPLE_SEARCH = "/api/v1/mixed_people/search"
    ENDPOINT_EMAIL_ACCESS = "/api/v1/mixed_people/add_to_my_prospects"

    def __init__(self) -> None:
        self.reqSession = requests.Session(impersonate="chrome123")
        self.reqSession.headers.update(
            {
                "accept": "*/*",
                "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                "content-type": "application/json",
                "referer": "https://app.apollo.io/",
                "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            }
        )
        self.csrf_token = None
        self.ui_finder_random_seed = generate_random_string(11)

    @property
    def _cache_key(self):
        return int(dt.datetime.now().timestamp() * 1000)

    def check_auth(self):
        params = {
            "timezone_offset": -330,
            "current_finder_view_id": "",
            "cacheKey": self._cache_key,
        }
        url = self.BASE_URL + self.ENDPOINT_AUTH_CHECK
        resp = self.request("GET", url, params=params)
        return resp.get("is_logged_in") is True

    def login(self, email, password):
        data = {
            "email": email,
            "password": password,
            "timezone_offset": -330,
            "cacheKey": self._cache_key,
        }

        url = self.BASE_URL + self.ENDPOINT_AUTH_LOGIN
        resp = self.request("POST", url, json=data)
        return resp

    def search_organization(self, organization_name):
        data = {
            "q_organization_fuzzy_name": organization_name,
            "display_mode": "fuzzy_select_mode",
            "cacheKey": self._cache_key,
        }
        url = self.BASE_URL + self.ENDPOINT_ORG_SEARCH
        resp = self.request("POST", url, json=data)

        if resp["organizations"]:
            return Organization(**resp["organizations"][0])

    def extract_people(self, resp):
        people = []

        for contact in resp["contacts"]:
            org_id = contact["organization_id"]
            for org in contact["employment_history"]:
                if org["organization_id"] == org_id:
                    contact["company"] = org["organization_name"]
                    break
            try:
                people.append(Person(**contact))
            except ValidationError as e:
                print(e)
                pass
        
        for person in resp["people"]:
            org_id = person["organization_id"]
            for org in person["employment_history"]:
                if org["organization_id"] == org_id:
                    person["company"] = org["organization_name"]
                    break
            try:
                people.append(Person(**person))
            except ValidationError:
                pass

        return people

    
    def specific_people_search(self, organization_id):
        data = {
            "cacheKey": self._cache_key,
            "contact_email_status_v2": ["verified"],
            "context": "people-index-page",
            "display_mode": "explorer_mode",
            "finder_table_layout_id": "63bcaac126d5eb00e4c28a38",
            "finder_view_id": "5b6dfc5a73f47568b2e5f11c",
            "num_fetch_result": 2,
            "open_factor_names": [],
            'sort_by_field': '[none]',
            'sort_ascending': False,
            "organization_ids": organization_id,
            "page": 1,
            "per_page": 1,
            "person_titles": ["CEO", "CIO", "CTO", "President", "CFO", "COO", "VP", "Founder","Project Manager","Marketing & Sales","Product Manager","Data Engineer","Co-Founder"],
            "show_suggestions": false,
            "ui_finder_random_seed": self.ui_finder_random_seed,
        }

        url = self.BASE_URL + self.ENDPOINT_PEOPLE_SEARCH
        resp = self.request("POST", url, json=data)

        return resp
    
    def general_people_search(self, organization_id):
        data = {
            "cacheKey": self._cache_key,
            "contact_email_status_v2": ["verified"],
            "context": "people-index-page",
            "display_mode": "explorer_mode",
            "finder_table_layout_id": "63bcaac126d5eb00e4c28a38",
            "finder_view_id": "5b6dfc5a73f47568b2e5f11c",
            "num_fetch_result": 3,
            "open_factor_names": ['prospected_by_current_team'],
            'sort_by_field': '[none]',
            'sort_ascending': False,
            "organization_ids": organization_id,
            "page": 1,
            "per_page": 2,
            # "person_titles": ["CEO", "CIO", "CTO", "President", "CFO", "COO", "VP", "Founder"],
            "show_suggestions": false,
            "ui_finder_random_seed": self.ui_finder_random_seed,
        }

        url = self.BASE_URL + self.ENDPOINT_PEOPLE_SEARCH
        resp = self.request("POST", url, json=data)

        return resp
    
    def search_companies_by_filters(self, technology_uids: list, organization_keyword_tags: list = None):
        headers = {
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        }
        
        all_data = []
        for page in range(60,70):  # Iterate through pages
            try:
                tag_params = ""
                sleep(random.randint(25, 35))  # Sleep for a random duration before each request
                if organization_keyword_tags:
                    tag_params = (
                        "currently_using_any_of_technology_uids[]=&"  
                        "q_organization_keyword_tags[]=web%20scraping&"  
                        "q_organization_keyword_tags[]=data%20extraction&"  
                        "q_organization_keyword_tags[]=web%20crawling&"  
                        "q_organization_keyword_tags[]=data%20mining&"  
                        "q_organization_keyword_tags[]=data%20harvesting&"  
                        "q_organization_keyword_tags[]=screen%20scraping&"  
                        "q_organization_keyword_tags[]=content%20extraction&"  
                        "q_organization_keyword_tags[]=data%20aggregation&"  
                        "q_organization_keyword_tags[]=automated%20data%20collection&"  
                        "q_organization_keyword_tags[]=web%20data%20integration&"  
                        "q_organization_keyword_tags[]=web%20data%20extraction&"  
                        "q_organization_keyword_tags[]=price%20scraping&"  
                        "q_organization_keyword_tags[]=market%20intelligence&"  
                        "q_organization_keyword_tags[]=competitor%20monitoring&"  
                        "q_organization_keyword_tags[]=lead%20generation&"  
                        "q_organization_keyword_tags[]=data%20collection&"  
                        "q_organization_keyword_tags[]=news%20aggregation&"     
                        "q_not_organization_keyword_tags[]=VPN&"  
                        "q_not_organization_keyword_tags[]=bot%20detection%20evasion&"  
                        "q_not_organization_keyword_tags[]=captcha%20bypass&"  
                        "q_not_organization_keyword_tags[]=Bright%20Data&"
                        "q_not_organization_keyword_tags[]=Oxylabs&"
                        "q_not_organization_keyword_tags[]=NetNut&"
                        "q_not_organization_keyword_tags[]=Smartproxy&"
                        "q_not_organization_keyword_tags[]=SOAX&"
                        "q_not_organization_keyword_tags[]=GeoSurf&"
                        "q_not_organization_keyword_tags[]=IPRoyal&"
                        "q_not_organization_keyword_tags[]=Shifter%20%28formerly%20Microleaves%29&"
                        "q_not_organization_keyword_tags[]=Infatica&"
                        "q_not_organization_keyword_tags[]=ProxyEmpire&"
                        "q_not_organization_keyword_tags[]=911Proxy&"
                        "organization_industry_tag_ids[]=5567cd4773696439b10b0000&"
                        "organization_num_employees_ranges[]=201%2C500&"
                        "organization_num_employees_ranges[]=1%2C10&"
                        "organization_num_employees_ranges[]=11%2C20&"
                        "organization_num_employees_ranges[]=21%2C50&"
                        "organization_num_employees_ranges[]=51%2C100&"
                        "organization_num_employees_ranges[]=101%2C200&"
                        f"page={page}"
                        "&per_page=50"
                    )
                else:
                    tag_params = f"page={page}"
                
                url = f"{self.BASE_URL}/api/v1/mixed_companies/search?{tag_params}"
                print(f"Fetching: {url}")
                
                response = self.reqSession.post(url, headers=headers)
                print(response.status_code, response.text)
                response.raise_for_status()
                
                all_data.append(response.json())
                
            except HTTPError as http_err:
                print(f"HTTP error occurred on page {page}: {http_err}")
                logging.error(f"HTTP error occurred on page {page}: {http_err}")
                break  # Skip this page and continue with the next
            except RequestException as req_err:
                print(f"Request error occurred: {req_err}")
                logging.error(f"Request error occurred: {req_err}")
                break # Skip and continue processing
            except Exception as err:
                print(f"Unexpected error: {err}")
                logging.error(f"Unexpected error: {err}")
                break  # Continue the process even if an unknown error occurs
        
        return all_data
    def bulk_enrich_organizations(self, domains: list):
        url = f"{self.BASE_URL}/api/v1/organizations/bulk_enrich"
        
        headers = {
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
             # Replace with your actual API key
        }
        
        # Format domains as required by the API
        payload = {"domains": domains}
    
        response = self.reqSession.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Ensure HTTP errors are raised
        return response.json()
    def fetch_organization_details(self, org_ids: list):
        """Fetch additional details for organization IDs using the load_snippets endpoint"""
        if not org_ids:
            return {"organizations": []}
        print("Fetching organization details for IDs:", org_ids)
        url = f"{self.BASE_URL}/api/v1/organizations/load_snippets"

        headers = {
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
              # Add your API key here
        }

        try:
            response = self.reqSession.post(
                url,
                headers=headers,
                json={'ids': org_ids},
                timeout=30
            )

            print(f"Details API status code: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching organization details: {response.text}")
                return {"organizations": []}

        except Exception as e:
            print(f"Exception when fetching organization details: {str(e)}")
            return {"organizations": []}

    # def search_people(self, organization_id, job_titles):
    def search_people(self, organization_id: list):

        specific_res = self.specific_people_search(organization_id=organization_id)
        peoples = self.extract_people(specific_res)
        if peoples:
            return peoples
        else:
            # general_res = self.general_people_search(organization_id=organization_id)
            # peoples = self.extract_people(general_res) 
            return []

        # data = {
        #     "cacheKey": self._cache_key,
        #     "contact_email_status_v2": ["verified"],
        #     "context": "people-index-page",
        #     "display_mode": "explorer_mode",
        #     "finder_table_layout_id": "63bcaac126d5eb00e4c28a38",
        #     "finder_view_id": "5b6dfc5a73f47568b2e5f11c",
        #     "num_fetch_result": 18,
        #     "open_factor_names": [],
        #     'sort_by_field': '[none]',
        #     'sort_ascending': False,
        #     "organization_ids": organization_ids,
        #     "page": page,
        #     "per_page": 25,
        #     "person_titles": ["CEO", "CIO", "CTO", "President", "CFO", "COO", "VP", "Founder"],
        #     "show_suggestions": false,
        #     "ui_finder_random_seed": self.ui_finder_random_seed,
        # }

        # url = self.BASE_URL + self.ENDPOINT_PEOPLE_SEARCH
        # resp = self.request("POST", url, json=data)

        # people = []

        # for contact in resp["contacts"]:
        #     org_id = contact["organization_id"]
        #     for org in contact["employment_history"]:
        #         if org["organization_id"] == org_id:
        #             contact["company"] = org["organization_name"]
        #             break
        #     try:
        #         people.append(Person(**contact))
        #     except ValidationError as e:
        #         print(e)
        #         pass
        
        # for person in resp["people"]:
        #     org_id = person["organization_id"]
        #     for org in person["employment_history"]:
        #         if org["organization_id"] == org_id:
        #             person["company"] = org["organization_name"]
        #             break
        #     try:
        #         people.append(Person(**person))
        #     except ValidationError:
        #         pass

        # return people

    # def access_email(self, person_id):
    #     data = {
    #         "entity_ids": [person_id],
    #         "analytics_context": "Searcher: Individual Add Button",
    #         "skip_fetching_people": True,
    #         "cta_name": "Access email",
    #         "cacheKey": self._cache_key,
    #     }

    #     url = self.BASE_URL + self.ENDPOINT_EMAIL_ACCESS

    #     resp = self.request("POST", url, json=data)
    #     if resp["contacts"]:
    #         return Person_email(**resp["contacts"][0])
    def access_email(self, person_id):
        data = {
            "entity_ids": [person_id],
            "analytics_context": "Searcher: Individual Add Button",
            "skip_fetching_people": True,
            "cta_name": "Access email",
            "cacheKey": self._cache_key,
        }

        url = self.BASE_URL + self.ENDPOINT_EMAIL_ACCESS

        try:
            resp = self.request("POST", url, json=data)

            # Basic validation
            if not isinstance(resp, dict):
                raise ValueError(f"Invalid response type: {type(resp)}")

            if "contacts" not in resp:
                raise ValueError(f"No 'contacts' in response: {resp}")

            if resp["contacts"]:
                return Person_email(**resp["contacts"][0])
            return None
        except Exception as e:
            print(f"Failed to access email for ID {person_id}: {e}")
            return None


    # def request(self, method, url, params=None, data=None, json=None):
    #     if self.csrf_token:
    #         self.reqSession.headers.update({"X-Csrf-Token": self.csrf_token})
    #     response = self.reqSession.request(
    #         method, url, params=params, data=data, json=json, impersonate="chrome123"
    #     )
    #     response.raise_for_status()
    #     if response.cookies.get("X-CSRF-TOKEN"):
    #         self.csrf_token = response.cookies.get("X-CSRF-TOKEN")
    #     return response.json()
    def request(self, method, url, params=None, data=None, json=None):
        if self.csrf_token:
            self.reqSession.headers.update({"X-Csrf-Token": self.csrf_token})

        response = self.reqSession.request(
            method, url, params=params, data=data, json=json, impersonate="chrome123"
        )

        try:
            response.raise_for_status()

            # Debug: check if response is JSON
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("application/json"):
                print(f"[DEBUG] Unexpected content-type: {content_type}")
                print(f"[DEBUG] Response (trimmed): {response.text[:300]}")
                raise ValueError("Expected JSON response, got something else")

            # Update token if available
            if response.cookies.get("X-CSRF-TOKEN"):
                self.csrf_token = response.cookies.get("X-CSRF-TOKEN")

            return response.json()

        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            print(f"[ERROR] URL: {url}")
            print(f"[ERROR] Payload: {json}")
            print(f"[ERROR] Status code: {response.status_code}")
            print(f"[ERROR] Response text (trimmed): {response.text[:300]}")
            raise

