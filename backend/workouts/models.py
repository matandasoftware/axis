from django.db import models
from django.conf import settings

# potential future addition: visibility field for sharing/exposure control (private/unlisted/public)
VISIBILITY_CHOICES = [
    ("private", "Private"),
    ("unlisted", "Unlisted"),
    ("public", "Public"),
]

# Example usage: a workout session could be "private" (only user can see), a custom exercise could be "unlisted" (not in library but can share link), and a system workout type is "public" (available to all).
visibility = models.CharField(
    max_length=20,
    choices=VISIBILITY_CHOICES,
    default="private",
    help_text="Controls who can see/use this item.",
)


class WorkoutType(models.Model):
    """
    Data-driven workout type (no fixed choices).
    Examples: Strength, Cardio, HIIT, Mobility, Yoga, Sport, Custom.

    - System defaults have user=NULL (shared).
    - User-created types have user set.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_types",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FF9500")
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workout_types"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        scope = "system" if self.user_id is None else f"user:{self.user_id}"
        return f"{self.name} ({scope})"


class Equipment(models.Model):
    """
    Data-driven equipment list.
    Examples: Dumbbells, Barbell, Kettlebell, Resistance Band, Treadmill, Bodyweight.

    - System defaults have user=NULL.
    - User can add custom equipment.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="equipment",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "equipment"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name


class MuscleGroup(models.Model):
    """
    Data-driven muscle groups.
    Examples: Chest, Back, Quads, Hamstrings, Shoulders, Core, Full Body.

    System defaults can be user=NULL; users can add more if they want.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="muscle_groups",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "muscle_groups"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """
    Exercise library entry.

    - System exercises can be shared (user=NULL).
    - User can create custom exercises.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercises",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    primary_muscle_group = models.ForeignKey(
        MuscleGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_exercises",
    )
    secondary_muscle_groups = models.ManyToManyField(
        MuscleGroup,
        blank=True,
        related_name="secondary_exercises",
    )

    equipment = models.ManyToManyField(Equipment, blank=True, related_name="exercises")

    # Optional metadata that helps later intelligence/recommendations
    difficulty = models.CharField(max_length=50, blank=True, null=True)  # free text for flexibility
    default_rest_seconds = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exercises"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name


class WorkoutSession(models.Model):
    """
    A performed workout session.

    Can be created manually or inferred/assisted later (e.g. from calendar + motion),
    but initially it’s user-created.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_sessions")
    workout_type = models.ForeignKey(
        WorkoutType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workout_sessions",
    )

    title = models.CharField(max_length=255, blank=True, null=True)

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)

    # Summary metrics (optional)
    duration_minutes = models.IntegerField(blank=True, null=True)
    calories_burned = models.IntegerField(blank=True, null=True)

    # Optional: where workout happened (gym/home/park)
    place = models.ForeignKey(
        "locations.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workout_sessions",
    )

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workout_sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "started_at"]),
        ]

    def __str__(self):
        return self.title or f"Workout {self.started_at}"


class WorkoutSet(models.Model):
    """
    A single set performed inside a session.
    Supports strength and cardio-style sets by keeping fields optional/flexible.
    """

    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="sets")
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True, related_name="sets")

    order = models.IntegerField(default=0)

    reps = models.IntegerField(blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    distance_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    rest_seconds = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "workout_sets"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["session", "order"]),
        ]

    def __str__(self):
        return f"Set {self.order} ({self.session_id})"


class TrainingPlan(models.Model):
    """
    A reusable plan/template (future: scheduler can generate sessions from this).
    Kept flexible: store structure in JSON so you can evolve it without migrations.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="training_plans")
    name = models.CharField(max_length=255)

    # Example JSON:
    # {"days":[{"name":"Day 1","exercises":[{"exercise_id":1,"sets":3,"reps":10}]}]}
    structure = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "training_plans"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return self.name