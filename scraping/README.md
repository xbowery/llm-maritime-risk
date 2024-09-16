# Data Crawling Setup
This guide walks you through setting up the environment for the scraping part of the project. It includes steps to create and activate a virtual environment, install dependencies, and set up the Jupyter kernel for interactive development.

## Step 1: Create and Activate Your Virtual Environment
Navigate to the scraping folder from the project's root directory.
```bash
cd scraping
```

Using Python 3.11.7, create the virtual environment.
> Make sure you have Python 3.11.7 installed. If not, download it [here](https://www.python.org/downloads/release/python-3117/).
```bash
py -3.11 -m venv scraping_venv
```

To activate the virtual environment, execute the following command based on your operating system.
```bash
# For Linux/Mac users
source scraping_venv/bin/activate  

# For Windows users
scraping_venv/Scripts/activate
```

## Step 2: Install Dependencies
The required dependencies are installed from the `requirements.txt` file when setting up the environment.
```bash
pip install -r requirements.txt
```

## Step 3: Set Up Jupyter Kernel
To use the newly created virtual environment in Jupyter notebooks, you need to install a new kernel. Run the following commands:
```bash
ipython kernel install --user --name=scraping_venv
python -m ipykernel install --user --name=scraping_venv
```

**Note:** Always ensure the virtual environment is activated when working within the scraping project.