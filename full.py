from apify_client import ApifyClient
import pandas as pd
import json
from datetime import datetime


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
        desired_language = input("Enter the desired text language (en,es or leave blank for no filter): ").strip().lower()
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