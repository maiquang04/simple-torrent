import hashlib
import bencodepy

from .models import Torrent, Piece, UserTorrent, UserProfile


def store_torrent_data(torrent_data):
    # Extract info from torrent_data
    info = torrent_data.get("info")
    user_data = torrent_data.get("user")

    # Find the user profile using peer_id
    user_profile = UserProfile.objects.filter(
        peer_id=user_data.get("peer id")
    ).first()
    if not user_profile:
        raise ValueError(
            f"User with peer_id {user_data.get('peer id')} not found"
        )

    # Create the Torrent object
    info_hash = hashlib.sha1(bencodepy.encode(info)).hexdigest()
    torrent = Torrent.objects.create(
        name=info["name"],
        file_length=info["length"],
        piece_length=info["piece length"],
        info_hash=info_hash,
        uploaded_by=user_profile,  # Associating with the user profile found using peer_id
    )

    # Create Piece objects for each piece in the 'pieces' list
    for index, piece_hash in enumerate(info["pieces"]):
        Piece.objects.create(
            torrent=torrent,
            index=index,
            hash_value=piece_hash,
        )

    # Create UserTorrent object to link user with the torrent
    UserTorrent.objects.create(
        user=user_profile,  # The user found using the peer_id
        torrent=torrent,
        current_directory=user_data.get("current directory", ""),
        file_path=user_data.get("file path", ""),
        is_available=True,  # Assuming the file is available for seeding initially
    )

    return torrent
