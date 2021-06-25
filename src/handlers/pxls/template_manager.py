import pickle
from bson.binary import Binary
import numpy as np
from pymongo import MongoClient
from .template import Template


class TemplateManager:
    def __init__(self, mongo_uri: str):
        mongo_client = MongoClient(mongo_uri)
        self.collection = mongo_client.pycharity.templates

    @staticmethod
    def serialize(array: np.ndarray) -> Binary:
        return Binary(pickle.dumps(array, protocol=2), subtype=128)

    @staticmethod
    def deserialize(data: Binary) -> np.ndarray:
        return pickle.loads(data)

    def add_template(self, template: Template):
        """
        Add a template to the database.
        """
        data = {
            "name": template.name,
            "owner": template.owner,
            "ox": template.ox,
            "oy": template.oy,
            "url": template.url,
            "image": self.serialize(template.image),
        }
        self.collection.insert_one(data)

    def get_template(self, **query) -> Template:
        """
        Find a template in the database matching the query.
        ex: self.get_template(name='Seon', owner=123456789)
        """
        document = self.collection.find_one(query, {"_id": False})
        if document is None:
            return None
        array = self.deserialize(document.pop("image"))
        return Template(
            array=array,
            ox=document["ox"],
            oy=document["oy"],
            name=document["name"],
            url=document["url"],
            owner=document["owner"],
        )

    def check_name_exists(self, name, **query):
        """
        Check if a template name already exists.
        """
        query["name"] = name
        if self.collection.find_one(query, {"image": False}):
            return True
        return False

    def get_templates(self, **query):
        """
        Get a generator returning templates in the database matching the query.
        """
        for document in self.collection.find(query, {"_id": False}):
            array = self.deserialize(document.pop("image"))
            yield Template(
                array=array,
                ox=document["ox"],
                oy=document["oy"],
                name=document["name"],
                url=document["url"],
                owner=document["owner"],
            )

    def delete_template(self, **query):
        """
        Delete a template from the database.
        """
        return self.collection.delete_one(query).deleted_count > 0
