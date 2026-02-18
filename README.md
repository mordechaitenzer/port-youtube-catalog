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

* **Port Account**: Access to your Port instance.
* **GitHub Repository**: To host your ingestion workflow.
* **YouTube API Key**: From the [Google Cloud Console](https://cloud.google.com/).
* **Playlist Identifier**: The unique `playlistId` you wish to track.

### Secure Storage
To keep your credentials safe, add the following as **GitHub Secrets** in your repository settings:
* `PORT_CLIENT_ID` 
* `PORT_CLIENT_SECRET`
* `YOUTUBE_API_KEY`

## Build your software catalog
At Port buildiung your softwarew catalog is comprised of two steps:
1. **Define your data model**
2. **Ingest data to software catalog**

In order to define your data model, Port provides you with no code elements called "blueprints" and "relations".


**Blueprints** are the building blocks of your catalog. Think of them as the "classes" or "schemas" for your data. 
For this guide, you will create two blueprints: **YouTube Playlist** and **YouTube Video**.

### Setup Blueprints

All blueprints follow the same structure.
| Field           | Description                                                                               | Notes                                        |
|-----------------|-------------------------------------------------------------------------------------------|----------------------------------------------|
| `identifier`    | Used for API calls, programmatic access, and distinguishing between blueprints            | Required (max 100 characters)                |
| `title`         | Human-readable name for the blueprint                                                     | Required (max 100 characters)                |
| `description`   | Visible as a tooltip when hovering over the info icon in the UI                           |                                              |
| `icon`          | Icon for the blueprint and its entities                                                   | You can only use icons from a predefined list|
| `schema`        | Object containing `properties` and `required` fields                                      | Required (see schema structure)              |
| `properties`    | customizable data fields, used to save and display information from external data sources.| See ownership section for details            |


An entity is an instance of a blueprint, it represents the data defined by a blueprint's properties.
After installing an integration, a page will be created in your catalog, populated with entities representing the ingested data.
In our case, each video populated in the Youtube Videos is an entity. 

