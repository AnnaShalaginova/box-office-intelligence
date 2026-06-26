# Box Office Intelligence

Interactive Streamlit dashboard for exploring box office performance from 2000 through 2024.

## Run Locally

```bash
streamlit run app.py
```

The app reads data from `movies.db`, which must stay in the project folder next to `app.py`.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app from that repository.
3. Set the main file path to:

```text
app.py
```

4. Deploy the app.

Required deployment files:

```text
app.py
movies.db
requirements.txt
.streamlit/config.toml
```

