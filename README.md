# simple-torrent

## Specification

-   Peer can seed any file.
-   Peer can download file.
-   Must show time downloading file.
-   Must show timestamp to prove downloading concurrently.

-   Slice file into many pieces
-   Merge pieces again and get file
-   When upload file, send json to tracker like

```json
{}
```

## How to run

-   Run `pip install -r requirements.txt`

-   Run ngrok by `ngrok http http://localhost:8000` or
    `ngrok http --url=stag-caring-notably.ngrok-free.app 8000`

## Requirements

-   django
-   bencodepy
-   requests
