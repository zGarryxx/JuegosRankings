from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django_mongodb_backend.models import EmbeddedModel


class Games(models.Model):
    BGGId = models.IntegerField(default=0)
    Name = models.CharField(max_length=100)
    Description = models.TextField()
    YearPublished = models.IntegerField()
    GameWeight = models.FloatField()
    AvgRating = models.FloatField()
    MinPlayers = models.IntegerField()
    MaxPlayers = models.IntegerField()
    NumUserRatings = models.IntegerField()
    NumExpansions = models.IntegerField()
    Family = models.CharField(max_length=100, blank=True, null=True)
    ImagePath = models.URLField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "games"
        managed = False

    def __str__(self):
        return f"{self.Name} - ({self.YearPublished})"

    def to_dict(self):
        return {
            "BGId": self.BGGId,
            "Name": self.Name,
            "Description": self.Description,
            "YearPublished": self.YearPublished,
            "GameWeight": self.GameWeight,
            "AvgRating": self.AvgRating,
            "MinPlayers": self.MinPlayers,
            "MaxPlayers": self.MaxPlayers,
            "NumUserRatings": self.NumUserRatings,
            "NumExpansions": self.NumExpansions,
            "Family": self.Family,
            "ImagePath": self.ImagePath,
        }


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, rol, password=None):
        if not email:
            raise ValueError("El usuario debe tener un email")

        email = self.normalize_email(email)
        usuario = self.model(email=email, nombre=nombre, rol=rol)

        if rol == 'admin':
            usuario.is_staff = True

        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, password=None):
        usuario = self.create_user(
            email=email,
            nombre=nombre,
            rol='admin',
            password=password
        )

        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Ranking(models.Model):
    user = models.CharField(max_length=100)
    positions = models.JSONField()
    user_id = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "ranking"
        managed = False


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, default='cliente')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email

class Categoria(models.Model):
    id = models.CharField(primary_key=True, db_column='_id', max_length=100)
    nombre = models.CharField(max_length=100)
    lista_juegos = models.JSONField(default=list)

    class Meta:
        managed = False
        db_table = 'categoria'


class Valoracion(models.Model):
    game_id = models.IntegerField()
    usuario = models.CharField(max_length=100)
    estrellas = models.IntegerField()
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'valoraciones'