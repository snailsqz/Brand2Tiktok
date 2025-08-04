#REMOVE DUPE
from apify_client import ApifyClient
import pandas as pd
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords

def get_data(apikey, search_queries):
    client = ApifyClient(apikey)

    #Prepare the Actor input
    run_input = {
        #"hashtags": ["fyp"],
        "searchQueries": search_queries,
        "resultsPerPage": 10,
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "excludePinnedPosts": False,
        "searchSection": "",
        "maxProfilesPerQuery": 10,
        "scrapeRelatedVideos": False,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadMusicCovers": False,
        "proxyCountryCode": "None",
    }

    # Run the Actor and wait for it to finish
    run = client.actor("OtzYfK1ndEGdwWFKQ").call(run_input=run_input)

    data_items = []
    print("Fetching results from dataset...")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        data_items.append(item)
    print(f"Collected {len(data_items)} items.")

    # --- Data Processing Start ---
    if data_items:
        # 1. Create initial DataFrame
        global df
        df = pd.DataFrame(data_items)
        # 2. Ensure 'authorMeta' values are proper dictionaries. now it's a blob that contain more details of author.
        def parse_json_if_string(data):
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse authorMeta string: {data[:50]}...")
                    return {} # Return an empty dict if parsing fails
            elif isinstance(data, dict):
                return data
            else:
                return {} # Handle other unexpected types

        df['authorMeta'] = df['authorMeta'].apply(parse_json_if_string)

        # 3. Flatten 'authorMeta' into a new DataFrame
        author_meta_df = pd.json_normalize(df['authorMeta'])

        # IMPORTANT: Rename columns in author_meta_df to avoid conflicts with existing columns
        # and to clearly distinguish author-related fields.
        author_meta_df = author_meta_df.add_prefix('author_')

        # 4. Concatenate the original DataFrame (without the nested 'authorMeta' column)
        final_df = pd.concat([df.drop('authorMeta', axis=1), author_meta_df], axis=1)
        
        #this is the part you get the column u want
        desired_columns = [
                'text',              # From the original video data
                'author_id',         # From authorMeta, renamed by add_prefix
                'author_name',
                'author_nickName',
                'author_verified',
                'author_signature',
                'author_fans',
                'author_video',
                'textLanguage'
            ]
        df = final_df[desired_columns]
        # Display the first few rows and columns of the combined DataFrame
        print("\nFirst 5 rows of the combined DataFrame:")
        print(df.head())
        print("\nColumns in the combined DataFrame:")
        print(df.columns.tolist())
        
        #Apply Language Filter
        global desired_language
        print("\nLanguage Filter:")
        print("You can filter the text language by entering 'en' for English, 'th' for Thai, or leave it blank to keep all languages.")
        # Prompt user for desired language
        desired_language = input("Enter the desired text language: ").strip().lower()
        if desired_language: # Check if the user actually provided a language
            print(f"Filtering for text language: '{desired_language}'")
            df = df[
                df['textLanguage'].str.lower() == desired_language
            ]
            print(f"After filtering, {len(df)} rows remain.")
        else:
            print("No language filter applied. Keeping all languages.")
            

        save = input("Do you want to save to CSV? (Y,N): ").strip().upper()
        if save != 'Y':
            print("Data not saved to CSV.")
            return
        # Define the CSV file name
        output_csv_file = f"{search_queries[0]}.csv"

        # Save the final DataFrame to a CSV file
        df.to_csv(output_csv_file, index=False, encoding='utf-8')
        print(f"Combined data successfully saved to {output_csv_file}")
    else:
        print("No data items were retrieved from the Apify dataset.")

def preprocess_data(df):
    if(desired_language == 'en'):
        nltk.download('stopwords')
        nltk.download('wordnet')
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        def preprocess_text(text):
            if not isinstance(text, str): # Handle non-string inputs like None
                return ""
            text = text.lower()
            text = re.sub(r'[^a-z0-9\s]', '', text) # Remove punctuation
            tokens = text.split()
            tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
            return " ".join(tokens)

        # Apply to influencer data
        df['processed_signature'] = df['author_signature'].apply(preprocess_text)
        df['processed_text'] = df['text'].apply(preprocess_text)

        # Combine relevant influencer text for comparison
        df['influencer_combined_text'] = df['processed_signature'] + " " + df['processed_text']

        brand_description_text = "luxury Italian sports car manufacturer renowned for its high-performance vehicles"
        processed_brand_text = preprocess_text(brand_description_text)

    elif(desired_language == 'th'):
        # Load Thai stopwords once
        thai_stop_words = set(thai_stopwords())

        def preprocess_text(text):
            if not isinstance(text, str): # Handle non-string inputs like None
                return ""

            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U00002702-\U000027B0"  # Dingbats
                "\U000024C2-\U0001F251"
                "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                "\U00002600-\U000026FF"  # Miscellaneous Symbols
                "\U00002500-\U000025FF"  # Box Drawing, Block Elements
                "]+", flags=re.UNICODE
            )
            text = emoji_pattern.sub(r'', text)
            # Remove characters that are NOT Thai letters, numbers, #, @, or spaces
            text = re.sub(r'[^\u0E00-\u0E7F\s]', '', text)

            tokens = word_tokenize(text, keep_whitespace=False)


            tokens = [word for word in tokens if word not in thai_stop_words and word.strip() != '']

            return " ".join(tokens)

    df['processed_signature'] = df['author_signature'].apply(preprocess_text)
    df['processed_text'] = df['text'].apply(preprocess_text)

    df['influencer_combined_text'] = df['processed_signature'] + " " + df['processed_text']

    brand_description_text = (
        "โค้ก กินกับอะไรก็อร่อย อาหารเผ็ดๆยิ่งต้องกินกับโค้กเลย"
    )
    processed_brand_text = preprocess_text(brand_description_text)

    print("Processed Brand Text:")
    print(processed_brand_text)
    print("\nProcessed Influencer Texts (first 2 rows):")
    print(df[['author_name', 'influencer_combined_text']].head(2).to_string())
    

def main():
    print("Welcome to the TikTok Data Scraper!")
    print("This script will scrape TikTok data using the Apify Actor.")
    global search_queries
    search_queries = input("Enter search queries (comma-separated): ").split(',')
    search_queries = [query.strip() for query in search_queries if query.strip()]  # Clean up input
    if not search_queries:
        print("No valid search queries provided. Exiting.")
        return
    print(f"Search queries: {search_queries}")
    apikey = input("Enter your Apify API key: ").strip()
    if not apikey:
        print("No API key provided. Exiting.")
        return
    get_data(apikey, search_queries)
    
    
if __name__ == "__main__":
    main()