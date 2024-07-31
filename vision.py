from openai import OpenAI
import subprocess
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

model = OpenAI()
model.timeout = 200

def image_base64(image):
    with open(image, "rb") as f:
        return base64.b64encode(f.read()).decode()


def url2screenshot(url):
    print(f"Crawling {url}")
    if os.path.exists("screenshot.png"):
        os.remove("screenshot.png")
    
    result = subprocess.run(
        ["node", "screenshot.js", url],
        capture_output=True,
        text=True
    )

    exitcode = result.returncode
    output = result.stdout

    if not os.path.exists("screenshot.png"):
        print("Error")
        return "Failed to scrape the website"
    
    b64_image = image_base64("screenshot.png")
    return b64_image

def visionExtract(b64_image, prompt):
    response = model.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a web crawler, your job is to extract information based on a screenshot of a website & user's instruction"
            },
            {
                "role":"user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        }
                    },
                    {
                        "type":"text",
                        "text": prompt
                    }
                ]
            }
        ],
        max_tokens=3000
    )
    message = response.choices[0].message
    message_text = message.content

    if "ANSWER_NOT_FOUND" in message_text:
        print("ERROR: Answer not found")
        return "I was unable to find the answer on that website. Please pick anothe one"
    else:
        print(f"GPT: {message_text}")
        return message_text

def save_response_as_json(response, file_path):
    try:
        json_start = response.find('<json_output>') + len('<json_output>')
        json_end = response.find('</json_output>')
        json_str = response[json_start:json_end].strip()
        
        json_data = json.loads(json_str)
        
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Response saved to {file_path}")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"Error saving response as JSON: {e}")

def visionCrawl(url, prompt):
    b64_image = url2screenshot(url)
    print("Image Captured")

    if b64_image == "Failed to scrape the website":
        return "I was unable to crawl that site. Please pick a different one"
    else:
        return visionExtract(b64_image, prompt)

response = visionCrawl("http://www.cvs.com", 
                       """
                        You are an end-to-end tester tasked with generating precise navigation steps for a given webpage screenshot. Your goal is to create a detailed JSON output that includes event names and correct element information for each step of navigation.

                        Carefully examine the screenshot and identify all interactive elements such as buttons, links, input fields, dropdowns, and other clickable and focusable items. Pay attention to their visual appearance, labels, and relative positions on the page.

                        Generate a series of navigation steps that would allow a user to interact with all major elements on the page. For each step, determine:
                        1. The event name (e.g., "click", "input", "select")
                        2. The element type (e.g., "button", "link", "text field")
                        3. The element identifier (e.g., id, class, or descriptive text, label)
                        4. The action to be performed (e.g., "click", "enter text", "choose option")

                        Create a JSON output with the following structure:
                        {
                        "steps": [
                            {
                            "step_number": 1,
                            "event_name": "event_name_here",
                            "element": {
                                "type": "element_type_here",
                                "identifier": "element_identifier_here"
                            },
                            "action": "action_description_here"
                            },
                            // Additional steps...
                        ]
                        }

                        Here are three examples of how a step in your JSON output might look:

                        1. For clicking a Book a vaccination link:
                        {
                        "step_number": 1,
                        "event_name": "click",
                        "element": {
                            "type": "link",
                            "identifier": "Book a vaccination"
                        },
                        "action": "Click on the 'Book a vaccination' link"
                        }

                        2. For entering text in a search field:
                        {
                        "step_number": 2,
                        "event_name": "input",
                        "element": {
                            "type": "text field",
                            "identifier": "search-input"
                        },
                        "action": "Enter search query in the search box"
                        }

                        Be as precise and thorough as possible in your analysis. Include all significant interactive elements on the page, and ensure that your navigation steps cover a complete user journey through the webpage.

                        Provide your complete JSON output within <json_output> tags.
                      """)
print(response)
save_response_as_json(response, "steps.json")
