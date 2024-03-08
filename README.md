
# FastAPI application

This is a FastAPI application to serve as the backend for an Asset Performance Analytics Dashboard (consider sample widgets of 3-4 different types). This application will interact with a MongoDB database to analyse/ collate data related to various assets'
performance.
## Setup
1. Clone the Repository
2. Change the directory in terminal to where the Repository is located
3. Type the following command  to create a virtual environment
    ```bash
    python -m venv <ENV_NAME>
    ```
    
4. Activate virtual environment
    ```bash
    <ENV_NAME>\Scripts\activate
    ```

5. Select the python interpreter in the virtual env as the default interpreter. Use the latest python interpreter

6. Install dependencies:
    ```bash
    pip install "fastapi[all]"
    pip install pymongo
    pip install motor
    pip install "python-jose[cryptography]" "passlib[bcrypt]" python-multipart
    ```

7. Create a .env file
8. Create a new database in MongoDB. Create 3 Collections: assets, performance_metrics and users in that database

9. Make the following additions in the .env file
    
    a. Set the **MONGO_URI**
    
    b. Set the **DB_NAME** to the database name created
    
    c. Set **JWT_SECRET_KEY** and **JWT_REFRESH_SECRET_KEY**
10. Run the following command
    ```bash
    uvicorn index:app --host 127.0.0.1 --port 8000
    ```
11. In your browser open: http://127.0.0.1:8000/docs to use the APIs

    