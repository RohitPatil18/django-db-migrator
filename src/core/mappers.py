from demoapp import models

from .base import BaseModelMap
from .fields import MethodField, ReferenceField


class TechnologyMapper(BaseModelMap):
    destmodel = models.Technology
    sourcetable = "mst_technology"
    renamed_columns = {"title": "name"}


class DeveloperMapper(BaseModelMap):
    destmodel = models.Developer
    sourcetable = "developer"
    exclude_fields = ["about"]

    status = MethodField()
    technology = ReferenceField(mapper=TechnologyMapper, source="technology_id")

    def get_status_value(self, row):
        if row["status"]:
            return models.DeveloperStatusChoice.active
        return models.DeveloperStatusChoice.inactive


class TeamMapper(BaseModelMap):
    destmodel = models.Team
    sourcetable = "team"


class TeamMember(BaseModelMap):
    destmodel = models.TeamMember
    sourcetable = "team_members"

    developer = ReferenceField(mapper=DeveloperMapper, source="developer_id")
    team = ReferenceField(mapper=TeamMapper, source="team_id")


mappers_list = [TechnologyMapper, DeveloperMapper, TeamMapper, TeamMember]
