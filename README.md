# EPUB to Audiobook Converter

This python script uses OpenAI API Text To Speech (TTS) Voice to convert EPUB books to Audiobooks with the ability to save progress and resume it.

## Key Features

- **EPUB Scanning and Selection**: Scans the current directory for EPUB files and displays them as choices for the user.
- **EPUB to MP3 Conversion**: Converts the selected EPUB file to MP3 format, saving the audio files in a dedicated folder named after the EPUB file within the `audiobooks` directory.
- **Chapter-based Division**: Divides the EPUB content by chapters for organized processing.
- **Chunked Audio Files**: Saves the generated MP3 files in chunks, adhering to the maximum size limit of the OpenAI TTS API.

## Features

- **EPUB Metadata Extraction**: Reads and extracts metadata such as title, author, date, and language from EPUB files.
- **Chapter-wise Text Extraction**: Extracts text content from each chapter of the EPUB file and cleans it for processing.
- **Text Splitting**: Splits extracted text into smaller chunks suitable for speech synthesis, based on a specified maximum text length.
- **Speech Synthesis**: Utilizes OpenAI's Text-to-Speech (TTS) API to convert text chunks into audio files.
- **Parallel Processing**: Uses multiprocessing to convert text chunks to audio in parallel, improving efficiency.
- **Batch Processing**: Uses batch size for efficient parallel processing of text chunks during conversion.
- **Progress Saving and Resuming**: Saves progress during conversion to a JSON file, allowing users to resume conversion from where they left off.
- **User-Friendly CLI**: Provides a command-line interface for selecting EPUB files, specifying output directories, and configuring batch sizes.
- **Error Handling**: Includes error handling to manage issues during audio synthesis and chunk processing.

## Installation

- Clone the repository:
    ```bash
    git clone https://github.com/fairy-root/epub-to-audiobook.git
    cd epub-to-audiobook
    ```

- Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

- Install the requirements

    ```bash
    pip install -r requirements.txt
    ```
    - Usage
        Ensure you have your OpenAI API key set up. You can set it in the environment variable OPENAI_API_KEY.

- Run the script:

    ```bash
    python main.py
    ```

- Follow the prompts to select the EPUB file and other options.

## Donation

Your support is appreciated:

- USDt (TRC20): `TGCVbSSJbwL5nyXqMuKY839LJ5q5ygn2uS`
- BTC: `13GS1ixn2uQAmFQkte6qA5p1MQtMXre6MT`
- ETH (ERC20): `0xdbc7a7dafbb333773a5866ccf7a74da15ee654cc`
- LTC: `Ldb6SDxUMEdYQQfRhSA3zi4dCUtfUdsPou`

## Author and Contact

- GitHub: [FairyRoot](https://github.com/fairy-root)
- Telegram: [@FairyRoot](https://t.me/FairyRoot)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or features.
