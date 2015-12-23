# custom
from robots.general import requestsHandler
from robots.general import customFunctions
																				
url = "https://www.whatismybrowser.com/developers/what-http-headers-is-my-browser-sending"
bsObj = customFunctions.url2bs(url)

print(bsObj.find("table",{"class":"table-striped"}).get_text)
