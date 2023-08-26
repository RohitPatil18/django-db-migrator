```python
from django.db import models


class Technology(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'mst_technology'


class Developer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'developer'


class Team(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(
        Developer,
        through='TeamMember'
    )

    class Meta:
        db_table = 'team'


class TeamMember(models.Model):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        db_table = 'team_members'
```