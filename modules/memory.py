"""
SEVAGOTH Memory Module
Handles short-term conversation memory and long-term persistent memory
"""

import os
import json
from config import MEMORY_FILE

# ── SHORT-TERM MEMORY ─────────────────────────────────────────────────────────

conversation_memory = {}


def remember_short_term(key: str, value):
    """
    Store data in short-term memory (lost when program closes)
    
    Args:
        key: Memory key identifier
        value: Data to store
    """
    conversation_memory[key] = value


def recall_short_term(key: str):
    """
    Retrieve data from short-term memory
    
    Args:
        key: Memory key identifier
        
    Returns:
        Stored value or None if not found
    """
    return conversation_memory.get(key, None)


def clear_short_term():
    """Clear all short-term memory"""
    global conversation_memory
    conversation_memory = {}


# ── LONG-TERM MEMORY ─────────────────────────────────────────────────────────

def load_memory() -> dict:
    """
    Load long-term memory from file
    
    Returns:
        Dictionary of stored memories
    """
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_memory(data: dict):
    """
    Save long-term memory to file
    
    Args:
        data: Dictionary of data to save
    """
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Load long-term memory on module import
long_term_memory = load_memory()


def remember_long_term(key: str, value):
    """
    Store data in long-term memory (persists to file)
    
    Args:
        key: Memory key identifier
        value: Data to store
    """
    long_term_memory[key] = value
    save_memory(long_term_memory)


def recall_long_term(key: str):
    """
    Retrieve data from long-term memory
    
    Args:
        key: Memory key identifier
        
    Returns:
        Stored value or None if not found
    """
    return long_term_memory.get(key, None)


def delete_long_term(key: str):
    """
    Delete a memory entry from long-term memory
    
    Args:
        key: Memory key identifier
    """
    if key in long_term_memory:
        del long_term_memory[key]
        save_memory(long_term_memory)


def list_long_term_memories() -> dict:
    """
    List all long-term memories
    
    Returns:
        Dictionary of all stored memories
    """
    return long_term_memory.copy()


def clear_long_term():
    """Clear all long-term memory from file"""
    global long_term_memory
    long_term_memory = {}
    save_memory(long_term_memory)


def get_memory_stats() -> dict:
    """
    Get statistics about stored memories
    
    Returns:
        Dictionary with memory stats
    """
    return {
        "short_term_entries": len(conversation_memory),
        "long_term_entries": len(long_term_memory),
        "memory_file_size": os.path.getsize(MEMORY_FILE) if os.path.exists(MEMORY_FILE) else 0,
        "memory_file": MEMORY_FILE
    }