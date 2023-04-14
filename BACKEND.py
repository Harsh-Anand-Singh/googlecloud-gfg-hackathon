import os
import json
from google.cloud import storage, language_v1
from flask import Flask, request

app = Flask(__name__)

# Set up the Google Cloud Storage client and bucket name
bucket_name = '<your-bucket-name>'
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Set up the Google Cloud Natural Language API client and language type
language_client = language_v1.LanguageServiceClient()
language_type = language_v1.Document.Type.PLAIN_TEXT


@app.route('/')
def index():
    """
    Display the index page with a form for entering the name of the file to analyze.
    """
    return """
        <html>
            <body>
                <h1>Feedback Analysis Dashboard</h1>
                <p>Welcome to the Feedback Analysis Dashboard! This dashboard displays the results of sentiment analysis and entity extraction on customer feedback data.</p>
                <form method="POST" action="/analyze">
                    <label for="bucket">Bucket:</label>
                    <input type="text" name="bucket" id="bucket"><br>
                    <label for="file">File:</label>
                    <input type="text" name="file" id="file"><br>
                    <input type="submit" value="Analyze Feedback">
                </form>
            </body>
        </html>
    """


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze the customer feedback data in the specified file and return the sentiment analysis and entity extraction results.
    """
    bucket_name = request.form['bucket']
    file_name = request.form['file']
    blob = bucket.blob(file_name)

    # Download the feedback data from the specified file in the bucket
    feedback_data = json.loads(blob.download_as_string())

    # Analyze the feedback data using the Google Cloud Natural Language API
    document = {'content': json.dumps(feedback_data), 'type': language_type}
    response = language_client.analyze_sentiment(request={'document': document})
    sentiment = response.document_sentiment.score

    document = {'content': json.dumps(feedback_data), 'type': language_type}
    response = language_client.analyze_entities(request={'document': document})
    entities = [{'name': entity.name, 'type': language_v1.Entity.Type(entity.type).name} for entity in response.entities]

    # Return the sentiment analysis and entity extraction results as JSON
    return json.dumps({'sentiment': sentiment, 'entities': entities})


if __name__ == '__main__':
    # Start the Flask server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
