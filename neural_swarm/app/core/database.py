import json
import os
from .config import DB_FILE

class Database:
    @staticmethod
    def load():
        if not os.path.exists(DB_FILE):
            return {"projects": []}
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"projects": []}

    @staticmethod
    def save(data):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def add_project(project):
        db = Database.load()
        # Verificar si ya existe para evitar duplicados
        db["projects"] = [p for p in db["projects"] if p.get("id") != project.get("id")]
        db["projects"].append(project)
        Database.save(db)

    @staticmethod
    def update_project(updated_project):
        db = Database.load()
        for i, p in enumerate(db["projects"]):
            if p.get("id") == updated_project.get("id"):
                db["projects"][i] = updated_project
                break
        Database.save(db)
        
    @staticmethod
    def delete_project(project_id):
        db = Database.load()
        db["projects"] = [p for p in db["projects"] if p.get("id") != project_id]
        Database.save(db)
