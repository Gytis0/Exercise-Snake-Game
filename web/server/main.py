from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3, os, time, secrets, asyncio
from ConnectionManager import (
    ConnectionManager,
)  # ensure this has async connect/broadcast/disconnect

DB_PATH = os.environ.get("SCORES_DB", "scores.db")
# ALLOWED_ORIGINS = os.environ.get(
#     "ALLOWED_ORIGINS", "http://localhost:5173,http://raspberrypi.local:8000"
# ).split(",")

app = FastAPI(title="Pi Game Scores API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


with get_conn() as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT,
            score INTEGER NOT NULL,
            created_at REAL NOT NULL,
            claim_token TEXT,
            expires_at REAL
        );
    """
    )
    # helpful index for /scores/top
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_scores_order ON scores (score DESC, created_at ASC);"
    )
    conn.commit()


class ScoreInAnonymous(BaseModel):
    score: int = Field(..., ge=0)


class ScoreClaimIn(BaseModel):
    code: str = Field(..., min_length=4, max_length=64)
    player: str = Field(..., min_length=1, max_length=32)


class ScoreOut(BaseModel):
    id: int
    player: Optional[str]
    score: int
    created_at: float


class NewScoreResp(BaseModel):
    id: int
    claim_token: str


manager = ConnectionManager()


@app.post("/scores", response_model=NewScoreResp)
async def add_score_anon(s: ScoreInAnonymous):
    now = time.time()
    token = secrets.token_urlsafe(16)
    exp = now + 15 * 60
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO scores (player, score, created_at, claim_token, expires_at) VALUES (NULL, ?, ?, ?, ?)",
            (int(s.score), now, token, exp),
        )
        conn.commit()
        new_id = cur.lastrowid
    # Optional: broadcast that a new (unclaimed) score arrived
    await manager.broadcast(
        {
            "type": "new_score",
            "data": {
                "id": new_id,
                "score": int(s.score),
                "player": None,
                "created_at": now,
            },
        }
    )
    return {"id": new_id, "claim_token": token}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/scores/{score_id}/claim", response_model=ScoreOut)
async def claim_score(score_id: int, body: ScoreClaimIn):
    code = body.code.strip()
    player = body.player.strip()
    now = time.time()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM scores WHERE id=?", (score_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Score not found")
        if row["player"]:
            raise HTTPException(409, "Already claimed")
        if row["expires_at"] and row["expires_at"] < now:
            raise HTTPException(410, "Claim window expired")
        short = (row["claim_token"] or "")[-6:]
        if code != row["claim_token"] and code != short:
            raise HTTPException(403, "Invalid code")
        conn.execute(
            "UPDATE scores SET player=?, claim_token=NULL WHERE id=?",
            (player, score_id),
        )
        conn.commit()
        out = conn.execute(
            "SELECT id, player, score, created_at FROM scores WHERE id=?", (score_id,)
        ).fetchone()
    # notify clients
    await manager.broadcast({"type": "claimed", "data": dict(out)})
    return ScoreOut(**dict(out))


@app.get("/scores/top", response_model=List[ScoreOut])
def top_scores(limit: int = 10):
    limit = max(1, min(100, limit))
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, player, score, created_at FROM scores ORDER BY score DESC, created_at ASC LIMIT ?",
            (limit,),
        ).fetchall()
    return [ScoreOut(**dict(r)) for r in rows]


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await manager.connect(ws)
    try:
        # Keep the socket open; we don't expect messages from the client
        while True:
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager.disconnect(ws)
