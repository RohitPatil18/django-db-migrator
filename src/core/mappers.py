from demoapp import models
from .base import BaseModelMap

class TechnologyMapper(BaseModelMap):
    destmodel = models.Technology
    sourcetable = 'technology'

class DeveloperMapper(BaseModelMap):
    destmodel = models.Developer
    sourcetable = 'developer'

class TeamMapper(BaseModelMap):
    destmodel = models.Team
    sourcetable = 'team'

class TeamMember(BaseModelMap):
    destmodel = models.TeamMember
    sourcetable = 'team_members'


mappers_list = [
    TechnologyMapper,
    DeveloperMapper,
    TeamMapper,
    TeamMember
]