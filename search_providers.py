import random
import time
import requests
from bs4 import BeautifulSoup

class SearchProvider:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def search(self, query, max_results=10, max_retries=3):
        pass

class GoogleSearch(SearchProvider):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        
    def search(self, query, max_results=10, max_retries=3):
        if not query or len(query.strip()) < 3:
            print(f"Query too short or invalid: {query}")
            return []
            
        results = []
        retry_delay = 2
        print(f"Searching for: {query}")

        for attempt in range(max_retries):
            try:
                params = {
                    'q': query,
                    'num': max_results,
                    'hl': 'en'
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                # Add random delay between requests
                time.sleep(random.uniform(2, 5))
                
                # Rotate user agent
                headers['User-Agent'] = random.choice(self.user_agents)
                
                # First get the homepage to set cookies
                try:
                    home_response = self.session.get('https://www.google.com/', headers=headers, timeout=10)
                    home_response.raise_for_status()
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    print(f"[DEBUG] Failed to get homepage: {str(e)}")
                
                # Now perform the search
                response = self.session.get(
                    'https://www.google.com/search',
                    headers=headers,
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                print(f"[DEBUG] Response status: {response.status_code}")
                print("[DEBUG] Response URL:", response.url)
                print("[DEBUG] Response headers:", dict(response.headers))
                
                # Save response content for debugging
                with open('google_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("[DEBUG] Saved response content to google_response.html")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                if not soup.find_all('div', {'class': ['g', 'g-inner']}):
                    print("[DEBUG] No search result elements found in response")
                # Try different possible result containers
                search_results = []
                for div in soup.find_all(['div', 'article']):
                    classes = div.get('class', [])
                    if any(c in ['g', 'g-inner', 'MjjYud', 'Gx5Zad', 'fP1Qef', 'xpd', 'EIaa9b'] for c in classes):
                        search_results.append(div)

                for i, result in enumerate(search_results[:max_results], 1):
                    title_elem = result.find(['h3', 'h4'])
                    link_elem = result.find('a')
                    snippet_elem = result.find('div', {'class': ['VwiC3b', 'lyLwlc']})

                    if title_elem and link_elem:
                        results.append({
                            'position': i,
                            'keyword': query,
                            'title': title_elem.text.strip(),
                            'url': link_elem.get('href', '').split('?q=')[-1].split('&')[0] if '?q=' in link_elem.get('href', '') else link_elem.get('href', ''),
                            'description': snippet_elem.text.strip() if snippet_elem else ''
                        })

                if results:
                    break

            except Exception as e:
                print(f"Search attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue

        return results

class DuckDuckGoSearch(SearchProvider):
    def search(self, query, max_results=10, max_retries=3):
        results = []
        retry_delay = 3

        for attempt in range(max_retries):
            try:
                params = {'q': query, 'kl': 'us-en'}
                response = requests.get(
                    'https://html.duckduckgo.com/html/',
                    headers=self.get_headers(),
                    params=params,
                    timeout=15
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                search_results = soup.find_all('div', {'class': 'result'})

                for i, result in enumerate(search_results[:max_results], 1):
                    title_elem = result.find('a', {'class': 'result__a'})
                    snippet_elem = result.find('a', {'class': 'result__snippet'})

                    if title_elem:
                        results.append({
                            'position': i,
                            'keyword': query,
                            'title': title_elem.text.strip(),
                            'url': title_elem['href'],
                            'description': snippet_elem.text.strip() if snippet_elem else ''
                        })

                if results:
                    break

            except Exception as e:
                print(f"Search attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                continue

        return results