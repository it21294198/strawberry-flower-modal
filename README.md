1. Create virtual ENV(only for first time)
   ```
   python3 -m venv project_env
   ```

2. Activate virtual ENV
   ```
   source project_env/bin/activate
   ```

3. Install all packages
   ```
   pip3 install -r requirements.txt
   ```

4. Run the server
   ```
   fastapi dev main.py 
   ```

5. Before deployment to add uvicorn
   ```
   pip3 install "fastapi[all]"
   ```

6. Run this if any new package has been added(to update requirements.txt)
   ```
   pip freeze > requirements.txt
   ```

7. To run top of uvicorn
   ```
   uvicorn main:app --reload
   ```
   or on another port
   ```
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

8. Build docker image
   ```
   docker build -t image-backend .
   ```

9. Run the Docker build
    ```
    docker run -d  --name image-backend-container -p 80:80 image-backend
    ```

10. [Click to view process of deployment on Azure](https://youtu.be/HyCO6nMdxC0?si=nKh9u1vAdoBHJV13)

11. Login to Remote Docker registry
   ```
   docker login [server_name] -u [user_name] -p [password]
   ```

12. Tagging the docker image
   ```
   docker build -t [server_name]/[any_name]:[built_tag] .
   ```

13. Push above created image tag to Remote Docker registry
    ```
    docker push [above_created_tag_whole_name]
    ```

14. Install Postgres DB
   1.  Add install the pre-compiled binary package
      ```
      pip install psycopg2-binary
      ```
   2. Install PostgreSQL Development Tools
      ```
      brew install postgresql
      ```
   3. Add pg_config to Your PATH: After installing PostgreSQL, ensure that pg_config is in your PATH
      ```
      export PATH="/usr/local/opt/postgresql/bin:$PATH"
      ```
   4. Install package
      ```
      pip install psycopg2
      ```
   5. Check version
      ```
      python -c "import psycopg2; print(psycopg2.__version__)"
      ```
15. To load the .env file in Python.
    ```
    pip install python-dotenv
    ```

16. Create `.env` at root folder and add following
      ```.env
      DB_HOST=
      DB_PORT=
      DB_NAME=
      DB_USER=
      DB_PASSWORD=

      DB_CONNECTION=

      AZURE_STORAGE_CONNECTION_STRING=
      AZURE_STORAGE_CONTAINER_NAME=

      AZURE_STORAGE_ACCOUNT_NAME=
      AZURE_STORAGE_ACCOUNT_KEY=
      ```
   
17. Azure Access issues
   1. [Azure Key issues](https://stackoverflow.com/questions/6985921/where-can-i-find-my-azure-account-name-and-account-key)
   2. [Blob Storage Anonyms access](https://learn.microsoft.com/en-us/answers/questions/453430/help-with-resourcenotfound-error-when-open-image-l)