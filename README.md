# MA_CORE
This is mainly for migration of projects repos it's metadata and prs from bitbucket server to bitbucket cloud


#### Folder structure
```bash
  project_root/
|-- src/
|   |-- controller/
|   |   |-- __init__.py 
|   |   |-- bitbucket_controller.py
|   |
|   |-- service/
|   |   |-- __init__.py 
|   |   |-- bitbucket_service.py
|   |
|   |-- util/
|   |   |-- __init__.py 
|   |   |-- bitbucket_util.py
|   |
|   |-- __init__.py
| 
|-- .gitignore
|-- README.md
|-- app.py
|-- requirements.txt
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python app.py
```
access the server

```bash
  http://localhost:5000
```
