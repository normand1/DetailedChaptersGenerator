# Chapter Generator

## Overview

This project is a comprehensive tool for create useful artifacts for podcast episodes. It automates the following tasks:

1. Transcribing audio to text using Whisper
2. Extracting links from episode descriptions
3. Generating timestamped chapters based on discussed links
4. Creating SRT files for subtitles

The project is designed to handle multiple podcasts and episodes, keeping track of processed content to avoid duplication.

## Key Components

- `run_this_first.zsh`: Initial setup script
- `app.py`: Main application script
- `podcastFetcher.py`: Handles podcast episode downloading and processing
- `transcriptToSRT.py`: Converts transcripts to SRT format
- `scrapeLinks.py`: Extracts links from episode descriptions
- `generateDescriptionChaptersV2.py`: Generates timestamped chapters

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/podcast-processing-project.git
   cd podcast-processing-project
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

1. Run the initial setup script:
   ```
   chmod +x run_this_first.zsh
   ./run_this_first.zsh
   ```

   This will add a allMappedChapterPodcasts.json file with a default podcast. Replace the details of this default podcast to process a new podcast. NOTE: This will run continuously until you kill it. Need to add a limit value still. 
   Also, the processed_episodes.json file in each podcast folder will track the GUID of each processed podcast so it isn't processed again unnecessarily. 

2. (a) Run the main application:
   ```
   python app.py
   ```

2. (b) To process a specific podcast episode:
   ```
   python podcastFetcher.py <podcast_name> <rss_url> <episode_guid>
   ```

## Contributing

Contributions to this project are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request

Please ensure your code adheres to the project's coding standards and include tests for new features.

## Contact

Dave Norman - @1davidnorman on X.com