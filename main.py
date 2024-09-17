import os
import json
import ebooklib
import multiprocessing
from pathlib import Path, PureWindowsPath
from typing import List, Tuple, Dict
from ebooklib import epub
from bs4 import BeautifulSoup
from openai import OpenAI

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# Initialize OpenAI client
client = OpenAI()

# Global variables
audiobook_path = Path(PureWindowsPath("./audiobooks/"))
sample_rate = 22050
progress_file = "conversion_progress.json"
max_text_length = 4096

# EPUB Metadata and Content Reading
def read_epub_metadata(epub_path: str) -> Tuple[str, str, str, str]:
    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Unknown Title'
    author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else 'Unknown Author'
    date = book.get_metadata('DC', 'date')[0][0] if book.get_metadata('DC', 'date') else 'Unknown Date'
    language = book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else 'Unknown Language'
    return title, author, date, language

def read_epub_text_by_chapter(epub_path: str) -> List[str]:
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_body_content()
        soup = BeautifulSoup(content, 'lxml')
        text = soup.get_text(separator=' ')
        cleaned_text = clean_text(text)
        chapters.append(cleaned_text)
    return chapters

def clean_text(text: str) -> str:
    lines = text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text

def get_epub_files_with_metadata(directory: str) -> List[Tuple[str, str, str, int, str, str]]:
    epub_files = [file for file in os.listdir(directory) if file.endswith('.epub')]
    epub_files_with_metadata = []

    for epub_file in epub_files:
        epub_path = os.path.join(directory, epub_file)
        title, author, date, language = read_epub_metadata(epub_path)
        book = epub.read_epub(epub_path)
        page_count = sum(1 for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        epub_files_with_metadata.append((epub_file, title, author, page_count, date, language))

    return epub_files_with_metadata

def display_choices(epub_files_with_metadata: List[Tuple[str, str, str, int, str, str]]) -> str:
    print("Available EPUB files:")
    for index, (file, title, author, count, date, language) in enumerate(epub_files_with_metadata, start=1):
        print(f"{index}. {title} by {author} ({count} pages, {date}, {language})")
    while True:
        choice = input("Enter the number of the EPUB file you want to convert to an audiobook: ").strip()
        try:
            choice = int(choice)
            if 1 <= choice <= len(epub_files_with_metadata):
                break
            else:
                print("Invalid choice. Please enter a number corresponding to the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    return epub_files_with_metadata[choice - 1][0]

# Split text into parts using full stops within the max length limit
def split_text_into_parts(text: str, max_length: int) -> List[str]:
    parts = []
    current_part = ""
    sentences = text.split('.')
    for sentence in sentences:
        if len(current_part) + len(sentence) + 1 > max_length:
            parts.append(current_part.strip())
            current_part = sentence + '.'
        else:
            current_part += sentence + '.'
    if current_part:
        parts.append(current_part.strip())
    return parts

# Synthesize Chunk of Text using OpenAI TTS
def synthesize_chunk(text_chunk: str, output_dir: str, chunk_index: int):
    response = client.audio.speech.create(
        model="tts-1", # OpenAI TTS model ("tts-1-hd" provides better quality)
        voice="shimmer", # OpenAI TTS voice ("shimmer", "alloy", "echo", "fable", "onyx", "nova")
        input=text_chunk
    )
    output_filename = f"chunk_{chunk_index + 1:03d}.mp3"
    path = os.path.join(output_dir, output_filename)
    response.stream_to_file(path)
    print(f"Audio for chunk {chunk_index + 1} saved to {path}")
    return path

# Parallel Processing for Efficiency
def process_chunk(args):
    text_chunk, output_dir, chunk_index = args
    try:
        synthesize_chunk(text_chunk, output_dir, chunk_index)
        return True
    except Exception as e:
        print(f"Error processing chunk {chunk_index}: {e}")
        return False

def convert_epub_to_audiobook(epub_path: str, output_dir: str, batch_size: int = 4, resume: bool = False):
    book_id = get_book_id(epub_path)
    book_output_dir = os.path.join(output_dir, book_id)
    os.makedirs(book_output_dir, exist_ok=True)
    
    chapters = read_epub_text_by_chapter(epub_path)

    # Print the cleaned text by chapter
    for idx, chapter in enumerate(chapters):
        print(f"Chapter {idx + 1}:\n{chapter}\n")

    all_parts = []
    for idx, chapter in enumerate(chapters):
        parts = split_text_into_parts(chapter, max_text_length)
        all_parts.extend([(part, book_output_dir, len(all_parts) + i) for i, part in enumerate(parts)])

    if resume and os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            completed_chunks = progress.get(book_id, [])
    else:
        completed_chunks = []

    part_args = [args for args in all_parts if args[2] not in completed_chunks]

    with multiprocessing.Pool(batch_size) as pool:
        results = pool.map(process_chunk, part_args)
    
    completed_chunks.extend(idx for _, _, idx in part_args if results[idx])
    
    with open(progress_file, 'w') as f:
        json.dump({book_id: completed_chunks}, f)
    
    print(f"Audiobook conversion for '{book_id}' completed.")

# Helper Function to Get Book ID
def get_book_id(epub_path: str) -> str:
    return os.path.splitext(os.path.basename(epub_path))[0]

# Main Function and CLI
def main():
    epub_files_with_metadata = get_epub_files_with_metadata('.')
    if not epub_files_with_metadata:
        print("No EPUB files found in the directory.")
        return
    
    chosen_epub = display_choices(epub_files_with_metadata)
    
    output_dir = input(f"Enter output directory (default: {audiobook_path}): ") or str(audiobook_path)
    batch_size = int(input("Enter batch size (default: 4): ") or 4)
    resume = input("Resume previous conversion (yes/no, default: no): ").strip().lower() == "yes"

    epub_path = os.path.join('.', chosen_epub)
    convert_epub_to_audiobook(epub_path, output_dir, batch_size, resume)

if __name__ == "__main__":
    main()
