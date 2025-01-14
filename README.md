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