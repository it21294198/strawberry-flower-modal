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

8. Build docker image
   ```
   docker build -t image-backend .
   ```

9. Run the Docker build
    ```
    docker run -d  --name image-backend-container -p 80:80 image-backend
    ```

    ```
    FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/app

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","80"]
    ```