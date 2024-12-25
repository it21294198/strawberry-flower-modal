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

5. Run this if any new package has been added(to update requirements.txt)
   ```
   pip freeze > requirements.txt
   ```