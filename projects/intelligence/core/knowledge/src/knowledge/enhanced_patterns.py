#!/usr/bin/env python3
"""
Enhanced pattern library with comprehensive domain coverage.
Modular implementation split across multiple files for maintainability.
"""

from typing import List
from .db_manager import Pattern
from .patterns import get_enhanced_patterns


def populate_enhanced_patterns(db):
    """Populate database with enhanced pattern library."""
    patterns = get_enhanced_patterns()
    
    for pattern in patterns:
        # Check if pattern already exists
        existing = db.conn.execute(
            "SELECT id FROM patterns WHERE name = ? AND language = ?",
            (pattern.name, pattern.language)
        ).fetchone()
        
        if not existing:
            db.add_pattern(pattern)
    
    return len(patterns)