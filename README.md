# Ingesting External Data into Port: A Complete Guide

This step-by-step guide explains how to model, ingest, and visualize external data in a developer portal using Port.


While we use a YouTube playlist and its videos as our example, the same pattern applies to any operational source, such as microservices, CI/CD pipelines, monitoring systems, or cloud resources.

By the end of this guide, you will know how to:

* **Ingest** data into Port using automated workflows.
* **Organize** it into a structured, relational catalog.
* **Enforce** standards and quality metrics with scorecards.
* **Create** a clear dashboard for actionable insight

## Prerequisites
Before getting started, ensure you have the following:

* **Port Account**: access to your Port instance.
* **GitHub Repository**: used to run the ingestion workflow via GitHub Actions.
* **Youtube Playlist**: we will ingest this playlist: https://www.youtube.com/playlist?list=PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy<br>The workflow only requires the playlist’s unique identifier (`playlistId`), so you can replace it with any playlist later.
* **YouTube API Key**: created in the [Google Cloud Console](https://cloud.google.com/).

### Secure Storage
To keep your credentials safe, add the following as **GitHub Secrets** in your repository settings:
* `PORT_CLIENT_ID` 
* `PORT_CLIENT_SECRET`
* `YOUTUBE_API_KEY`

## Build your software catalog
At Port buildiung your software catalog is comprised of two steps:
1. **Define your data model**
2. **Ingest data to software catalog**

In order to define your data model, Port provides you with no code elements called "blueprints" and "relations".


**Blueprints** are the building blocks of your catalog. Think of them as the "classes" or "schemas" for your data.<br>
For this guide, you will create two blueprints: **YouTube Playlist** and **YouTube Video**.

### Setup Blueprints

Blueprints are completely customizable, but they all follow the same basic structure.
| Field           | Description                                                                              | Notes                                        |
|-----------------|------------------------------------------------------------------------------------------|----------------------------------------------|
| `identifier`    | Used for API calls, programmatic access, and distinguishing between blueprints           | Required (max 100 characters)                |
| `title`         | Human-readable name for the blueprint                                                    | Required (max 100 characters)                |
| `description`   | Visible as a tooltip when hovering over the info icon in the UI                          |                                              |
| `icon`          | Icon for the blueprint and its entities                                                  | You can only use icons from a predefined list|
| `schema`        | Object containing `properties` and `required` fields                                     | Required                                     |
| `properties`    | customizable data fields, used to save and display information from external data sources| See the full [properties list](https://docs.port.io/build-your-software-catalog/customize-integrations/configure-data-model/setup-blueprint/properties#supported-properties)|



> [!IMPORTANT]
> Before defining blueprint properties, decide what questions you want to answer.<br>
> A good data model starts from the use-case, not from the API response.

In our case, we want to create a playlist and assest the "video quality" singals of its videos like readability and engagement.
These are the propeties we want to use:

**YouTube Video Blueprint**
| Property         | Type                   | Required | Why we need it                                                       |
| ---------------  | ---------------------- | -------- | -------------------------------------------------------------------- |
| `title`          | `string (url)`         | Yes      | Primary identifier shown in the catalog and search results.          |
| `titleLength`    | `number`               | No       | Enables quality rules (e.g., detect overly long titles).             | 
| `durationSeconds`| `number`               | No       | Helps evaluate viewing experience and filter very long/short videos. |
| `viewCount`      | `number`               | No       | Enables popularity and ranking visualizations.                       |
| `likeCount`      | `number`               | No       | Measures positive engagement quality.                                |
| `commentCount`   | `number`               | No       | 	Indicates interaction level and audience engagement.                |


**YouTube Playlist Blueprint**
| Property         | Type                   | Required | Why we need it                                                       |
| ---------------  | ---------------------- | -------- | -------------------------------------------------------------------- |
| `link`           | `string (url)`         | Yes      | Direct access to the playlist from Port.                             |
| `playlistId`     | `string`               | Yes      | Stable identifier used for ingestion and upserts.                    |
| `videoCount`     | `number`               | No       | Quick indicator of playlist size and completeness.                   |
| `lastUpdatedAt`  | `string (date-time)`   | No       | Shows when the data was last synced for freshness/debugging.         |



Blueprints describe individual entities, but real systems consist of connected components.<br>
A **relation** links blueprints together so the catalog reflects how the data actually behaves.

In our model, a playlist contains many videos, and each video belongs to exactly one playlist.
We model this using a relation from `youtube_video` → `youtube_playlist`.

Now that we defined the data model conceptually, we can implement it in Port.

In Port, the blueprint configuration is defined using JSON.


You can either configure it through the UI or paste the JSON directly in the blueprint editor.<br>
Go to **Builder → Blueprints → + Blueprint → Edit JSON** and paste the following configuration.

**YouTube Video Blueprint JSON**
The following blueprint defines the video entity and its relation to a playlist:
```json
{
  "identifier": "youtube_video",
  "description": "A video belonging to a YouTube playlist.",
  "title": "YouTube Video",
  "icon": "DevTV",
  "schema": {
    "properties": {
      "link": {
        "type": "string",
        "format": "url",
        "title": "Video Link"
      },
      "titleLength": {
        "type": "number",
        "title": "Title Length"
      },
      "title": {
        "type": "string",
        "title": "Title"
      },
      "durationSeconds": {
        "type": "number",
        "title": "Duration (Seconds)"
      },
      "publishedAt": {
        "type": "string",
        "format": "date-time",
        "title": "Published At"
      },
      "thumbnailUrl": {
        "type": "string",
        "title": "Thumbnail",
        "format": "url"
      },
      "description": {
        "type": "string",
        "title": "Description"
      },
      "channelTitle": {
        "type": "string",
        "title": "Channel"
      },
      "viewCount": {
        "type": "number",
        "title": "View Count"
      },
      "likeCount": {
        "type": "number",
        "title": "Likes"
      },
      "commentCount": {
        "type": "number",
        "title": "Comments"
      }
    },
    "required": [
      "title",
      "link"
    ]
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "aggregationProperties": {},
  "relations": {
    "playlist": {
      "title": "Playlist",
      "target": "youtube_playlist",
      "required": true,
      "many": false
    }
  }
}
```

**YouTube Playlist Blueprint JSON**

The playlist blueprint represents the parent entity that groups videos together.<br>
It serves as the aggregation point for insights such as total videos, freshness, and engagement across the collection.
```json
{
  "identifier": "youtube_playlist",
  "description": "A YouTube playlist that contains many videos.",
  "title": "YouTube Playlist",
  "icon": "Google",
  "schema": {
    "properties": {
      "link": {
        "type": "string",
        "format": "url",
        "title": "Playlist Link"
      },
      "videoCount": {
        "type": "number",
        "title": "Number of Videos"
      },
      "playlistId": {
        "type": "string",
        "title": "Playlist ID"
      },
      "lastUpdatedAt": {
        "type": "string",
        "title": "Last Update",
        "format": "date-time"
      }
    },
    "required": [
      "link",
      "playlistId"
    ]
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "aggregationProperties": {},
  "relations": {}
}
```
<details>
<summary>How the YouTube Video blueprint looks in Port</summary>

![Video Blueprint](assets/bp-video.png)

</details>

<details>
<summary>How the YouTube Playlist blueprint looks in Port</summary>

![Playlist Blueprint](assets/bp-playlist.png)

</details>

<details>
<summary>How the relation between YouTube Video and YouTube Playlist looks in Port</summary>

![Relation](assets/relations-viz.png)

</details>

## Data Ingestion (GitHub Workflow)
We use a GitHub Actions workflow to fetch playlist data from the YouTube Data API and synchronize it with Port.<br>
This turns your external data into living entities within your portal.

The workflow performs three operations:
1. **Fetch** playlist and video metadata from YouTube.
2. **Transform** the response into Port entities.
3. **Upsert** (Update or Insert) the entities into the catalog.

The workflow is triggered manually so you can control when synchronization happens.

### Step 1: Configure authentication
GitHub requires specific permissions to write data to Port and read data from YouTube.

**Create the required secrets**

1. Login to **Port**, go to **Profile → Credentials** and copy your `Client ID` and `Client Secret`.
2. Login to **Google Cloud Console**, create a YouTube Data API key.
3. In your GitHub repository, go to **Settings → Secrets and variables → Actions → New repository secret**
4. Add the following secrets:
   
|Source                | Secret Key          | Description                                       |
| ---------------------| --------------------|---------------------------------------------------|
| [Port](https://www.port.io/)               | `PORT_CLIENT_ID`    | Authenticates the workflow to Port                |
| [Port](https://www.port.io/)               | `PORT_CLIENT_SECRET` | Used to generate a Port access token              |
| [Google Cloud Console](https://cloud.google.com/)        | `YOUTUBE_API_KEY`   | Grants the workflow access to the YouTube Data API|

### Step 2: Create the ingestion workflow
Create a new file at:
```bash
.github/workflows/ingest_youtube.yml
```
Paste the following configuration.

**Important**: Update the `PLAYLIST_URL` in the env section below with the link to the playlist you wish to track.

```yaml
name: Ingest YouTube playlist to Port

on:
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    env:
      PLAYLIST_URL: "https://www.youtube.com/playlist?list=PL5ErBr2d3QJH0kbwTQ7HSuzvBb4zIWzhy"
      YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
      PORT_CLIENT_ID: ${{ secrets.PORT_CLIENT_ID }}
      PORT_CLIENT_SECRET: ${{ secrets.PORT_CLIENT_SECRET }}
      PORT_API_BASE_URL: "https://api.getport.io/v1"

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install requests isodate

      - name: Fetch and transform YouTube data
        id: run_script
        run: |
          python scripts/ingest_youtube.py
          echo "entities=$(cat entities.json | jq -c .)" >> $GITHUB_OUTPUT

      - name: Upsert entities to Port
        uses: port-labs/port-github-action@v1
        with:
          clientId: ${{ secrets.PORT_CLIENT_ID }}
          clientSecret: ${{ secrets.PORT_CLIENT_SECRET }}
          operation: BULK_UPSERT
          entities: ${{ steps.run_script.outputs.entities }}
```
> [!NOTE]
> The `BULK_UPSERT` operation keeps the catalog synchronized.<br>
> Existing entities are updated and new ones are created.

### Step 3: Run the workflow

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select **Ingest YouTube playlist to Port** from the left sidebar.
3. Click **Run workflow → Run workflow**.

If it works, it should look like this:
![workflow success](assets/workflow-success.png)

### Step 4: Verify ingestion in Port
Once the workflow completes, verify that the data has been mapped correctly:

1. Open your Port Catalog.
2. Check the **YouTube Playlists** and **YouTube Videos blueprints**.
   
If ingestion succeeded, Port now contains structured entities populated from YouTube.
<details>
<summary>View playlist entity</summary>

![Playlist entities](assets/catalog-playlist.png)
</details>

<details>
<summary>View videos entities</summary>

![Playlist entities](assets/catalog-videos.png)
</details>

