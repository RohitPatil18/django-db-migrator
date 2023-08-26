from django.db import models

# Note: Check to `previousmodels` in docs folder to refer
# previous models.


class Technology(models.Model):
    """
    Previous model: Technology

    Changes:
    - `name` column is renamed to `title`
    - Table name is changed from `mst_technology` to `technology`
    """

    title = models.CharField(max_length=100)

    class Meta:
        db_table = "technology"


class DeveloperStatusChoice(models.IntegerChoices):
    active = 1, "Active"
    inactive = 2, "Inactive"


class Developer(models.Model):
    """
    Previous model: Developer

    Changes:
    - `status` column is changed from `boolean` to `integer`. Instead of
    boolean value, we are now using `IntegerChoices`.
    - In previous models, `about` field was not available so it needs to be nullable
    or we need to provide some default value.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    about = models.TextField(null=True)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    status = models.SmallIntegerField(
        choices=DeveloperStatusChoice.choices,
        default=DeveloperStatusChoice.active,
    )

    class Meta:
        db_table = "developer"


class Team(models.Model):
    """
    Previous model: Team
    """

    title = models.CharField(max_length=100)
    members = models.ManyToManyField(Developer, through="TeamMember")

    class Meta:
        db_table = "team"


class TeamMember(models.Model):
    """
    Previous model: TeamMember
    """

    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        db_table = "team_members"
