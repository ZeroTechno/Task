My first CRUD API

<img width="1440" height="900" alt="Screenshot 2026-07-14 at 2 54 55 PM" src="https://github.com/user-attachments/assets/8cf4e311-5a9c-4cf5-8584-70777b9d6e4e" />
This image is Basically the 5th stage

Aside from the resources given, this is also an additional resource I used that helped me (https://www.youtube.com/watch?v=Lw-zLopB3o0&start=0)


Connecting to the database Stage 5 — Database Documentation

1. Why SQLite Was Chosen
SQLite was selected for this project because:
It is a serverless, self-contained database that requires no external database server or background services (like Docker or PostgreSQL) to run.
It runs directly inside Python's built-in standard library (`sqlite3`), making setup instant across any machine.
Data is stored in a single cross-platform file, making it ideal for local testing and lightweight backend applications while demonstrating true persistent storage across server restarts.

2. Where the Database File Is Stored
`./tasks.db` (stored in the root directory of the project folder).
The file is ignored by Git (`.gitignore`) so each environment maintains its own instance. On the application's first boot, the startup hook automatically detects if `tasks.db` exists; if missing, it creates the file, builds the `tasks` schema, and seeds the initial 3 example records.

3. How to Start the Project
First you have to clone the repository and enter the directory:
   ```bash
   git clone [https://github.com/ZeroTechno/Task.git](https://github.com/ZeroTechno/Task.git)
   cd Task


4. Screenshots of my database viewer
<img width="1040" height="658" alt="Screenshot 2026-07-21 at 1 32 07 PM" src="https://github.com/user-attachments/assets/7934d2da-81c8-4f7e-a7fc-380e25161acb" />


<img width="1044" height="660" alt="Screenshot 2026-07-21 at 1 31 22 PM" src="https://github.com/user-attachments/assets/a178f166-44c3-4a63-872d-d07ed3d647ed" />

5. One example SQL query you executed
SELECT * FROM tasks WHERE done = 1;
I used it to retrieve all completed tasks from the database during the manual inspection.
