import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class ChatHistory:
    """Store and retrieve chat history"""
    
    def __init__(self, db_path: str = "./data/chat_history.db"):
        self.db_path = db_path
        # Ensure data directory exists
        Path("./data").mkdir(exist_ok=True)
        self._create_table()
    
    def _create_table(self):
        """Create the history table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                confidence REAL,
                agents_used TEXT,
                is_favorite INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_chat(self, question: str, answer: str, confidence: float, agents_used: List[str] = None):
        """Save a chat to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history (question, answer, confidence, agents_used, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            question,
            answer,
            confidence,
            json.dumps(agents_used or []),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, answer, confidence, agents_used, timestamp
            FROM chat_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "confidence": row[3] or 0.0,
                "agents_used": json.loads(row[4]) if row[4] else [],
                "timestamp": row[5]
            })
        
        return history
    
    def get_history_by_question(self, search_term: str) -> List[Dict[str, Any]]:
        """Search history by question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, answer, confidence, agents_used, timestamp
            FROM chat_history
            WHERE question LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{search_term}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "confidence": row[3] or 0.0,
                "agents_used": json.loads(row[4]) if row[4] else [],
                "timestamp": row[5]
            })
        
        return history
    
    def delete_history(self, chat_id: int):
        """Delete a specific chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history WHERE id = ?', (chat_id,))
        
        conn.commit()
        conn.close()
    
    def clear_all(self):
        """Clear all history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history')
        
        conn.commit()
        conn.close()
    
    def get_by_id(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific chat by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, answer, confidence, agents_used, timestamp
            FROM chat_history
            WHERE id = ?
        ''', (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "confidence": row[3] or 0.0,
                "agents_used": json.loads(row[4]) if row[4] else [],
                "timestamp": row[5]
            }
        return None