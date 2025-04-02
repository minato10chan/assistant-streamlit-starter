from typing import List, Dict, Any
from ..config.settings import CHUNK_SIZE

def process_text_file(file_content: str, chunk_size: int = CHUNK_SIZE) -> List[Dict[str, Any]]:
    """テキストファイルをチャンクに分割"""
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in file_content.split('\n'):
        line_size = len(line)
        if current_size + line_size > chunk_size:
            chunks.append({
                "id": f"chunk_{len(chunks)}",
                "text": '\n'.join(current_chunk)
            })
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    if current_chunk:
        chunks.append({
            "id": f"chunk_{len(chunks)}",
            "text": '\n'.join(current_chunk)
        })
    
    return chunks 