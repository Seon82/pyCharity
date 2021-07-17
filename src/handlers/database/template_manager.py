from typing import AsyncGenerator
from handlers.pxls import Template, Progress
from handlers.database import DatabaseConnector


class TemplateManager(DatabaseConnector):
    """
    An helper used to ease interactions with the templates stored
    in the mongodb databse.
    """

    def __init__(self, mongo_uri: str):
        """
        :param mongo_uri: The mongodb's uri, ie: mongodb://127.0.0.1:27017/
        """
        super().__init__(mongo_uri, "templates")

    def _doc2template(self, document) -> Template:
        """
        Convert a document to a Template.
        """
        array = self._deserialize(document["image"]) if "image" in document else []
        return Template(
            array=array,
            ox=document["ox"],
            oy=document["oy"],
            name=document["name"],
            canvas_code=document["canvas_code"],
            url=document["url"],
            owner=document["owner"],
            scope=document["scope"],
            progress=Progress(**document["progress"]),
        )

    def _template2doc(self, template: Template) -> dict:
        """
        Convert a template to a document.
        """
        data = {
            "name": template.name,
            "owner": template.owner,
            "scope": template.scope,
            "canvas_code": template.canvas_code,
            "ox": template.ox,
            "oy": template.oy,
            "url": template.url,
            "image": self._serialize(template.image),
            "progress": template.progress.to_dict(),
        }
        return data

    async def add_template(self, template: Template):
        """
        Add a template to the database.
        """
        data = self._template2doc(template)
        await self.collection.insert_one(data)

    async def update_template(self, template: Template, data=None):
        """
        Update a template from the database.

        :param data: A dictionary of fields to update. If set to None, updates all fields.
        """
        if data is None:
            data = self._template2doc(template)
        await self.collection.update_one(
            {"name": template.name, "canvas_code": template.canvas_code}, {"$set": data}
        )

    async def check_name_exists(self, name, **query):
        """
        Check if a template name already exists.
        """
        query["name"] = name
        if await self.collection.find_one(query, {"image": False}):
            return True
        return False

    async def get_template(self, no_image=False, **query) -> Template:
        """
        Find a template in the database matching the query.
        ex: self.get_template(name='Seon', owner=123456789)

        :param no_image: If set to True, do not retrieve the image attribute
        for decreased memory usage. The returned template will
        have an empty list as the image attribute instead.
        """
        projection = {"image": False} if no_image else None
        document = await super().find_one(projection=projection, **query)
        if document is None:
            return None
        return self._doc2template(document)

    async def get_templates(
        self, no_image=False, **query
    ) -> AsyncGenerator[Template, None]:
        """
        Get a generator returning templates in the database matching the query.

        :param no_image: If set to True, do not retrieve the image attribute
        for decreased memory usage. The returned template will
        have an empty list as the image attribute instead.
        """
        projection = {"image": False} if no_image else None
        async for document in super().find(projection=projection, **query):
            yield self._doc2template(document)

    async def delete_template(self, **query):
        """
        Delete a template from the database.
        """
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
