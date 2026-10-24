from utils.audio_processor import process_input
from core.transcriber import transcibe_all

source = "https://www.youtube.com/watch?v=VSFuqMh4hus"

chunks = process_input(source)
print(transcibe_all(chunks))