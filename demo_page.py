
def demo_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flower Detection API</title>

    <style>
        :root {
            --primary-color: #2563eb;
            --hover-color: #1d4ed8;
            --bg-color: #f8fafc;
            --text-color: #1e293b;
        }

        body {
            font-family: BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
            background: var(--bg-color);
            color: var(--text-color);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: var(--primary-color);
        }

        .upload-section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            margin-bottom: 2rem;
        }

        .button-group {
            display: flex;
            gap: 1rem;
            margin: 1.5rem 0;
        }

        button {
            padding: 0.75rem 1.5rem;
            border: none;
            background-color: var(--primary-color);
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.2s;
        }

        button:hover:not(:disabled) {
            background-color: var(--hover-color);
        }

        button:disabled {
            background-color: #cbd5e1;
            cursor: not-allowed;
        }

        .result-section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }

        #responseImage {
            max-height: 700px;
            width: auto;
            display: block;
            margin: 1rem 0;
        }

        .json-response {
            margin-top: 1.5rem;
            display: none;
        }

        pre {
            margin: 0;
            border-radius: 6px;
        }

        .file-input-wrapper {
            margin-bottom: 1rem;
        }

        input[type="file"] {
            display: block;
            margin-top: 0.5rem;
        }
    </style>
</head>

<!-- ####################################################################### -->

<body>
    <div class="container">
        <h1>Flower Detection API</h1>

        <div class="upload-section">
            <div class="file-input-wrapper">
                <label for="imageInput">Upload an image:</label>
                <input type="file" id="imageInput" accept="image/*" />
            </div>

            <div class="button-group">
                <button id="cvButton" disabled>Process with OpenCV</button>
                <button id="yoloButton" disabled>Process with YOLO</button>
            </div>
        </div>

        <br>

        <div class="result-section">
            <h2>Result</h2>
            <img id="responseImage" alt="Processed image will appear here" />
            <div id="jsonResponse" class="json-response">
                <h3>Detection Results</h3>
                <pre><code></code></pre>
            </div>
        </div>
    </div>

    <!-- ################################################################### -->

    <script>
        const input = document.getElementById('imageInput');
        const cvButton = document.getElementById('cvButton');
        const yoloButton = document.getElementById('yoloButton');
        const responseImage = document.getElementById('responseImage');
        const jsonResponse = document.getElementById('jsonResponse');
        let base64String = '';

        input.addEventListener('change', async () => {
            const file = input.files[0];
            if (file) {
                base64String = await toBase64(file);
                cvButton.disabled = false;
                yoloButton.disabled = false;
                responseImage.src = '';
                jsonResponse.style.display = 'none';
            }
        });

        cvButton.addEventListener('click', () => sendRequest('/find-flower-cv'));
        yoloButton.addEventListener('click', () => sendRequest('/find-flower-yolo'));

        function toBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
        }

        async function sendRequest(endpoint) {
            try {
                cvButton.disabled = true;
                yoloButton.disabled = true;

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: base64String })
                });

                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

                const data = await response.json();
                responseImage.src = data.image;

                if (endpoint.includes('yolo')) {
                    const displayData = {...data};
                    delete displayData.image;  // remove the base64 image from JSON display

                    jsonResponse.style.display = 'block';
                    const codeElement = jsonResponse.querySelector('code');
                    codeElement.textContent = JSON.stringify(displayData, null, 2);
                } else {
                    jsonResponse.style.display = 'none';
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error processing image');
            } finally {
                cvButton.disabled = false;
                yoloButton.disabled = false;
            }
        }
    </script>
</body>
</html>
"""