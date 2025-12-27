
# Excel Regression Analyzer

This is an interactive web application built with React and TypeScript that allows users to upload Excel or CSV files, visualize the data as a scatter plot, and perform a simple linear regression analysis.

The application is designed to be deployed easily on [Streamlit Cloud](https://share.streamlit.io/).



## Features

- **File Upload**: Drag-and-drop or browse to upload `.xlsx` or `.csv` files.
- **Interactive Scatter Plot**: Visualizes the relationship between two selected data columns.
- **Dynamic Variable Selection**: Choose which columns to use for the X and Y axes from a dropdown of numeric columns.
- **Simple Linear Regression**: Automatically calculates and displays:
  - The regression line on the plot.
  - The regression equation (`y = mx + b`).
  - R-Squared value to indicate model fit.
- **Modern UI**: Clean, responsive, and dark-themed interface built with Tailwind CSS.

## How to Deploy on Streamlit Cloud

Follow these steps to deploy your own instance of this application.

### 1. Create a GitHub Repository

Create a new **public** GitHub repository.

### 2. Add Files to the Repository

Add all the files from this project to your new repository. The essential files are:

- `metadata.json`
- `index.html`
- `index.tsx`
- `App.tsx`
- `types.ts`
- `components/icons.tsx`
- `streamlit_app.py`  *(This file)*
- `requirements.txt`  *(This file)*
- `README.md`         *(This file)*

You can do this by cloning the repository and pushing the files, or by using the "Add file" -> "Upload files" feature on GitHub.

### 3. Deploy on Streamlit

1.  Go to the [Streamlit Cloud dashboard](https://share.streamlit.io/deploy).
2.  Click **"New app"** and then select **"Deploy from an existing repository"**.
3.  **Connect your GitHub account** if you haven't already.
4.  Select your newly created repository.
5.  Ensure the **"Main file path"** is set to `streamlit_app.py`.
6.  Click **"Deploy!"**.

Streamlit will install the dependencies from `requirements.txt` and run the `streamlit_app.py` script, which serves the React application. Your app will be live in a few minutes.

## Local Development & Testing

While the primary goal is Streamlit deployment, you can also run this project locally.

### Prerequisites

- [Node.js](https://nodejs.org/) (which includes `npm`)
- [Python 3.8+](https://www.python.org/downloads/)

### Running the React App Directly (for UI development)

This project uses a modern setup without a traditional build step for development. You just need a simple local server.

1.  Install a simple server like `serve`:
    ```bash
    npm install -g serve
    ```
2.  From the project's root directory, run:
    ```bash
    serve .
    ```
3.  Open your browser to the URL provided (usually `http://localhost:3000`). The `index.html` file will load the React application.

### Testing the Streamlit Deployment Locally

This method simulates how the app will run on Streamlit Cloud.

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Streamlit app:**
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Your browser will open with the Streamlit interface, which will display the React application inside an iframe.
