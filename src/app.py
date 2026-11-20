import json
import time
from collections import defaultdict, deque

from flask import Flask, jsonify
from flask import request, Response

from config import CHUNK_DATA_SEPARATOR, CHUNK_SEPARATOR, AUDIO_CHUNK_LIFETIME
from models.audio_chunk import AudioChunk

app = Flask(__name__)

ROOMS = defaultdict(deque[AudioChunk])


@app.get("/api/time")
def get_time():
    return jsonify({"timestamp": time.time()})


@app.post("/api/<room_id>/sync")
def sync_call(room_id: str):
    server_timestamp = time.time()

    for key in ROOMS.keys():
        room = ROOMS[key]
        while room and server_timestamp - room[0].timestamp > AUDIO_CHUNK_LIFETIME:
            room.popleft()

    metadata: dict[str, any] = json.loads(request.form["metadata"])
    audio = request.files["audio"]
    requested_timestamp: float = metadata["requested_timestamp"]

    chunk = AudioChunk(**{**metadata["chunk"], "data": audio.read()})
    room = ROOMS[room_id]
    room.append(chunk)

    return_chunks = [
        CHUNK_DATA_SEPARATOR.join((json.dumps(x.metadata()).encode("utf-8"), x.data))
        for x in room
        if x.timestamp > requested_timestamp and x.user_id != chunk.user_id
    ]

    return Response(
        CHUNK_SEPARATOR.join(return_chunks),
        mimetype="application/octet-stream",
    )


if __name__ == "__main__":
    app.run()
