document.addEventListener("DOMContentLoaded", function () {
	const peer = new Peer();
	const fileInput = document.getElementById("file-input");
	const receivedFiles = document.getElementById("received-files");
	let conn;

	// Display your Peer ID
	peer.on("open", (id) => {
		document.getElementById("peer-id").innerText = id;
	});

	// Handle incoming connections
	peer.on("connection", (connection) => {
		connection.on("data", (data) => {
			if (data.type === "file") {
				const blob = new Blob([data.file]);
				const fileUrl = URL.createObjectURL(blob);

				// Create the HTML string
				const fileHtml = `
                    <li>
                        <a href="${fileUrl}" download="${data.fileName}">
                            Download ${data.fileName}
                        </a>
                    </li>
                `;

				receivedFiles.insertAdjacentHTML("beforeend", fileHtml);
			}
		});
	});

	// Connect to another peer
	document.getElementById("connect").onclick = () => {
		const remotePeerId = document.getElementById("remote-peer-id").value;
		conn = peer.connect(remotePeerId);

		conn.on("open", () => {
			console.log("Connected to:", remotePeerId);
		});

		conn.on("data", (data) => {
			console.log("Received:", data);
		});
	};

	// Send a file
	document.getElementById("send-file").onclick = () => {
		const file = fileInput.files[0];
		if (file && conn) {
			const reader = new FileReader();
			reader.onload = () => {
				conn.send({
					type: "file",
					file: reader.result,
					fileName: file.name,
				});
				console.log("File sent:", file.name);
			};
			reader.readAsArrayBuffer(file);
		}
	};
});
