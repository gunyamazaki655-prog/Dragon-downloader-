    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range:
        try:
            range_val = range.replace("bytes=", "").split("-")
            start = int(range_val[0])
            if range_val[1]:
                end = int(range_val[1])
            status_code = status.HTTP_206_PARTIAL_CONTENT
        except ValueError:
            pass

    chunk_length = (end - start) + 1

    async def file_stream():
        async with aiofiles.open(file_path, "rb") as f:
            await f.seek(start)
            remaining = chunk_length
            while remaining > 0:
                to_read = min(CHUNK_SIZE, remaining)
                data = await f.read(to_read)
                if not data:
                    break
                remaining -= len(data)
                yield data

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_length),
    }

    return StreamingResponse(
        file_stream(),
        status_code=status_code,
        headers=headers,
        media_type="application/octet-stream"
    )

