# TikTok KOL Relevance Matcher

The goal of this project is to create a tool for finding and ranking TikTok influencers based on their relevance to a given brand, utilizing Thai and Eng Natural Language Processing (NLP) techniques.

## Key Features

- **Influencer Data Processing:** Reads and manages influencer data from JSON sources.

- **Text Preprocessing:**

  - Removes emojis, numbers, and irrelevant symbols from text (like bios and video descriptions).
  - Converts text to lowercase.

- **Thai NLP (Natural Language Processing):**

  - **Thai Word Tokenization:** Uses `PyThaiNLP` to accurately split Thai text into individual words.
  - **Thai Stop Word Removal:** Filters out common, less meaningful words to highlight key terms.

- **Relevance Scoring:**

  - Employs **TF-IDF (Term Frequency-Inverse Document Frequency)** to transform brand and influencer texts into numerical vectors.
  - Uses **Cosine Similarity** to measure the resemblance between brand and influencer text vectors.

- **Influencer Ranking:**

  - Calculates a `total_score` by weighting the `relevance_score` and `authorMeta.fans` (follower count) to identify influencers who are both relevant and impactful.

- **Data Export:** Converts the final results into a CSV file for further analysis or use.

## How to Use It

1.  **Prep Your API Key:**

    - To get data from Apify, you'll need your personal API token from Settings.

2.  **Define Your Brand's Product Categories/Keywords:**

    _Input 1: Content Type_

    - Specify the type of video you are looking for (e.g., cooking videos, product reviews, travel vlogs). This information helps the system narrow the search to content that matches your interests.

    _Input 2: Brand's Niche_

    - Provide keywords related to your brand or product (e.g., spicy food, drinks, fashion, cosmetics). This helps the system find influencers whose content aligns with your target audience.

3.  **Run the Script!!!**

    - pip install -r requirements.txt
    - And run it

4.  **Check Out the Results:**
    - The script will print a neat table of ranked influencers (sorted by their `total_score`) right there in your console.

So when you run the script, you'll get a super cool table printed out. This table will show you a ranked list of influencers, with the most relevant ones right at the top! Here's what you'll see for each influencer:

- `authorMeta.name`: The influencer's name.

- `authorMeta.fans`: How many followers they've got.

- `relevance_score`: This is super important! It's a score from 0 to 1, telling you how well their content matches your brand. Higher is better.

- `total_score`: This is the final score we use to rank them. It's a mix of how relevant they are and how many fans they have.

Basically, the influencers with the highest `total_score` are your top picks.

## 📞 Get in Touch!

Got any questions or cool suggestions? Feel free to reach out!

- **Name:** Pawee Indulakshana

- **Email:** p.indulakshana@gmail.com
