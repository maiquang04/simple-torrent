document.addEventListener("DOMContentLoaded", function () {
	const currentDirectory = JSON.parse(document.getElementById("django-current-directory").textContent);

	let downloadLinks = [];

	document.getElementById("file-input").addEventListener("change", () => {
		const downloadMergedLink = document.getElementById("download-merged");
		// Clear the old merged file link when a new file is selected
		downloadMergedLink.style.display = "none";
		downloadMergedLink.href = "";
		downloadMergedLink.textContent = "";
	});

	document.getElementById("slice-file").addEventListener("click", async () => {
		const fileInput = document.getElementById("file-input");
		if (!fileInput.files.length) {
			alert("Please select a file first.");
			return;
		}

		const file = fileInput.files[0];
		const chunkSize = 512 * 1024; // 512KB
		const filePiecesContainer = document.getElementById("file-pieces");

		filePiecesContainer.innerHTML = "";

		for (let start = 0; start < file.size; start += chunkSize) {
			const chunk = file.slice(start, start + chunkSize);
			const arrayBuffer = await chunk.arrayBuffer();
			const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
			const hash = CryptoJS.SHA256(wordArray).toString(CryptoJS.enc.Hex);

			// Create a download link for the piece
			const blob = new Blob([chunk]);
			const fileUrl = URL.createObjectURL(blob);

			downloadLinks.push(fileUrl);
			const fileName = `${hash}.bin`;

			const fileHtml = `
                <li>
                    <a href="${fileUrl}" download="${fileName}">
                        Download ${fileName}
                    </a>
                </li>
			`;

			// Append the HTML to the list
			filePiecesContainer.insertAdjacentHTML("beforeend", fileHtml);

			// Automatically trigger the download
			const link = document.createElement("a");
			link.href = fileUrl;
			link.download = fileName;
			// link.click();

			console.log("Done");
		}

		alert("File sliced into pieces. Ensure they are saved in the directory: " + currentDirectory);
	});

	document.getElementById("merge-file").addEventListener("click", async () => {
		const fileInput = document.getElementById("file-input");
		if (!fileInput.files.length) {
			alert("Please select a file first.");
			return;
		}

		const filePiecesContainer = document.getElementById("file-pieces");
		const pieces = Array.from(filePiecesContainer.querySelectorAll("li a")).map((a) => a.href);

		if (!pieces.length) {
			alert("No pieces available to merge.");
			return;
		}

		// Simulate downloading each piece and merging.
		const mergedArrayBuffers = [];
		for (let i = 0; i < pieces.length; i++) {
			const response = await fetch(pieces[i]);
			const arrayBuffer = await response.arrayBuffer();
			mergedArrayBuffers.push(arrayBuffer);
			console.log("Merge");
		}

		const mergedBlob = new Blob(mergedArrayBuffers, { type: fileInput.files[0].type });
		const mergedLink = document.getElementById("download-merged");
		mergedLink.href = URL.createObjectURL(mergedBlob);
		mergedLink.download = `merged-${fileInput.files[0].name}`;
		mergedLink.style.display = "block";
		mergedLink.textContent = "Download Merged File";
	});
});
