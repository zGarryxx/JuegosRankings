import csv
import io
import json
from urllib.parse import urlencode

from bson.errors import InvalidId
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app.forms import RegistroForm, LoginForm
from app.models import *


def es_admin(user):
    return user.is_superuser

def inicio(request):
    return render(request, 'html/inicio.html')

@login_required(login_url='login/')
@user_passes_test(es_admin, login_url='home')
def admin_view(request):
    return render(request, "html/admin_panel.html")

@login_required(login_url='login/')
def ranking_view(request):
    return render(request, "html/games.html")

@login_required(login_url='login/')
def show_games(request):
    list_games = [g.to_dict() for g in Games.objects.all()]
    return JsonResponse({"games": list_games})

@login_required(login_url='login/')
def home_view(request):
    print(f"Usuario autenticado: {request.user.nombre}")
    return render(request, "html/home.html")


def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])

            usuario.rol = 'cliente'
            usuario.is_staff = False

            usuario.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'html/register.html', {'form': form})
def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(request, email=email, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'html/login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login/')
def lista_juegos(request):

    juegos = Games.objects.using("mongodb").all().order_by('Name')
    nombre = request.GET.get("nombre", "")
    year = request.GET.get("year", "")
    min_players = request.GET.get("min_players", "")
    max_players = request.GET.get("max_players", "")

    if nombre:
        juegos = juegos.filter(Name__icontains=nombre)

    if year:
        juegos = juegos.filter(YearPublished=year)

    if min_players:
        juegos = juegos.filter(MinPlayers__gte=min_players)

    if max_players:
        juegos = juegos.filter(MaxPlayers__lte=max_players)

    paginator = Paginator(juegos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "html/games.html", {
        "page_obj": page_obj,
        "nombre": nombre,
        "year": year,
        "min_players": min_players,
        "max_players": max_players,
    })


@csrf_exempt
@login_required(login_url='login')
def guardar_ranking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            db = connections['mongodb'].database

            cat_id_str = data.get("category_id")
            if not cat_id_str:
                return JsonResponse({"status": "error", "message": "Falta category_id"}, status=400)

            cat_obj_id = ObjectId(cat_id_str)

            nombre_usuario = getattr(request.user, 'nombre', getattr(request.user, 'email', str(request.user)))

            filtro = {
                "user_id": request.user.id,
                "category_id": cat_obj_id
            }

            datos_actualizar = {
                "$set": {
                    "user": nombre_usuario,
                    "category_name": data.get("category_name", "General"),
                    "positions": data["ranking"],
                    "category_id": cat_obj_id
                }
            }

            result = db.ranking.update_one(filtro, datos_actualizar, upsert=True)

            return JsonResponse({"status": "ok"})

        except Exception as e:
            print(f"Error al guardar: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required(login_url='login/')
def elegir_categoria_ranking(request):
    categorias = Categoria.objects.using("mongodb").all()
    categorias_validas = [c for c in categorias if c.lista_juegos]

    return render(request, "html/elegir_categoria.html", {
        "categorias": categorias_validas
    })


@login_required(login_url='login')
def crear_ranking(request, idcat):
    db = connections['mongodb'].database

    try:
        obj_id = ObjectId(idcat)
        categoria = db.categoria.find_one({"_id": obj_id})
        if not categoria:
            return redirect('elegir_categoria_ranking')
    except (InvalidId, TypeError):
        return redirect('elegir_categoria_ranking')

    user_id = request.user.id

    ranking_existente = db.ranking.find_one({
        "user_id": user_id,
        "category_id": obj_id
    })

    if not ranking_existente:
        ranking_existente = db.ranking.find_one({
            "user_id": user_id,
            "category_id": idcat
        })

    ranking_previo_json = "null"
    edit_id = None

    if ranking_existente:
        edit_id = str(ranking_existente['_id'])
        positions_data = ranking_existente.get('positions', {})
        ranking_previo_json = json.dumps(positions_data)

    lista_juegos_ids = categoria.get('lista_juegos', [])
    juegos_base = Games.objects.using("mongodb").filter(BGGId__in=lista_juegos_ids)

    total_juegos_reales = juegos_base.count()
    limit = min(total_juegos_reales, 10)
    positions = list(range(1, limit + 1))

    nombre_busqueda = request.GET.get('nombre', '')
    juegos_filtrados = juegos_base
    if nombre_busqueda:
        juegos_filtrados = juegos_filtrados.filter(Name__icontains=nombre_busqueda)

    juegos_filtrados = juegos_filtrados.order_by('Name')

    paginator = Paginator(juegos_filtrados, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'positions': positions,
        'total_juegos': total_juegos_reales,
        'categoria': {
            'id': str(categoria['_id']),
            'nombre': categoria.get('nombre')
        },
        'page_obj': page_obj,
        'ranking_previo': ranking_previo_json,
        'edit_id': edit_id,
        'nombre': nombre_busqueda
    }

    return render(request, 'html/crear_ranking.html', context)


@login_required(login_url='login/')
@user_passes_test(es_admin, login_url='home')
def cargar_datos(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            Games.objects.using("mongodb").all().delete()

            nuevos_juegos = []
            for row in reader:
                try:
                    bgg_id = int(row.get('BGGId', 0) or 0)
                except ValueError:
                    bgg_id = 0

                juego = Games(
                    BGGId=bgg_id,
                    Name=row.get('Name', ''),
                    Description=row.get('Description', ''),
                    YearPublished=int(row.get('YearPublished', 0) or 0),
                    GameWeight=float(row.get('GameWeight', 0) or 0.0),
                    AvgRating=float(row.get('AvgRating', 0) or 0.0),
                    MinPlayers=int(row.get('MinPlayers', 0) or 0),
                    MaxPlayers=int(row.get('MaxPlayers', 0) or 0),
                    NumUserRatings=int(row.get('NumUserRatings', 0) or 0),
                    NumExpansions=int(row.get('NumExpansions', 0) or 0),
                    ImagePath=row.get('ImagePath', '')
                )
                nuevos_juegos.append(juego)

            if nuevos_juegos:
                Games.objects.using("mongodb").bulk_create(nuevos_juegos)
                messages.success(request,
                                 f"Se han importado {len(nuevos_juegos)} juegos correctamente con sus IDs reales.")

            return redirect('admin_view')

        except Exception as e:
            messages.error(request, f"Error al procesar el CSV: {e}")

    return render(request, "html/cargar_datos.html")

@login_required(login_url='login/')
@user_passes_test(es_admin, login_url='home')
def editar_categoria(request):
    db = connections['mongodb'].database

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            db.categoria.insert_one({
                "nombre": nombre,
                "lista_juegos": []
            })
            messages.success(request, f"Categoría '{nombre}' creada con éxito.")
            return redirect('editar_categoria')

    categorias = Categoria.objects.using("mongodb").all()
    return render(request, 'html/editar_categoria.html', {'categorias': categorias})


from bson import ObjectId
from django.db import connections
from django.shortcuts import redirect
from django.contrib import messages

@login_required(login_url='login/')
@user_passes_test(es_admin, login_url='home')
def eliminar_categoria(request, idcat):
    db = connections['mongodb'].database

    try:
        target_id = ObjectId(idcat) if len(idcat) == 24 else idcat
        resultado = db.categoria.delete_one({"_id": target_id})

        if resultado.deleted_count > 0:
            messages.success(request, "Categoría eliminada correctamente.")
        else:
            messages.error(request, "No se encontró la categoría para eliminar.")

    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        messages.error(request, f"Error técnico al eliminar: {e}")

    return redirect('editar_categoria')

@login_required(login_url='login/')
@user_passes_test(es_admin, login_url='home')
def detalle_categoria(request, idcat):
    db = connections['mongodb'].database
    categoria_obj = None

    try:
        if len(idcat) == 24:
            categoria_obj = Categoria.objects.using("mongodb").get(pk=ObjectId(idcat))
    except:
        try:
            categoria_obj = Categoria.objects.using("mongodb").get(pk=idcat)
        except:
            pass

    if not categoria_obj:
        try:
            query_id = ObjectId(idcat) if len(idcat) == 24 else idcat
            doc = db.categoria.find_one({"_id": query_id})
            if doc:
                categoria_obj = Categoria(
                    id=str(doc['_id']),
                    nombre=doc.get('nombre'),
                    lista_juegos=doc.get('lista_juegos', [])
                )
        except Exception as e:
            print(f"Error en búsqueda nativa: {e}")

    if not categoria_obj:
        messages.error(request, "No se pudo encontrar la categoría.")
        return redirect('editar_categoria')

    if request.method == "POST":
        game_id = request.POST.get("game_id")
        target_id = ObjectId(idcat) if len(idcat) == 24 else idcat

        if "add_game" in request.POST:
            db.categoria.update_one(
                {"_id": target_id},
                {"$addToSet": {"lista_juegos": int(game_id)}}
            )
            messages.success(request, "Juego añadido.")

        elif "remove_game" in request.POST:
            db.categoria.update_one(
                {"_id": target_id},
                {"$pull": {"lista_juegos": int(game_id)}}
            )
            messages.warning(request, "Juego eliminado.")

        params = {
            'nombre': request.POST.get('nombre', ''),
            'year': request.POST.get('year', ''),
            'min_players': request.POST.get('min_players', ''),
            'max_players': request.POST.get('max_players', ''),
            'page': request.POST.get('page', '')
        }

        querystring = urlencode({k: v for k, v in params.items() if v})

        base_url = reverse('detalle_categoria', args=[idcat])

        if querystring:
            return redirect(f"{base_url}?{querystring}")
        else:
            return redirect(base_url)

    nombre = request.GET.get("nombre", "")
    year = request.GET.get("year", "")
    min_p = request.GET.get("min_players", "")
    max_p = request.GET.get("max_players", "")

    filtros = {}
    if nombre: filtros["Name__icontains"] = nombre
    if year: filtros["YearPublished"] = int(year)
    if min_p: filtros["MinPlayers__gte"] = int(min_p)
    if max_p: filtros["MaxPlayers__lte"] = int(max_p)

    lista_actual = categoria_obj.lista_juegos or []

    juegos_busqueda = Games.objects.using("mongodb").filter(**filtros).exclude(BGGId__in=lista_actual)

    paginator = Paginator(juegos_busqueda, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    juegos_actuales = Games.objects.using("mongodb").filter(BGGId__in=lista_actual)

    return render(request, 'html/detalle_categoria.html', {
        'categoria': categoria_obj,
        'juegos_actuales': juegos_actuales,
        'page_obj': page_obj,
        'nombre': nombre,
        'year': year,
        'min_players': min_p,
        'max_players': max_p
    })

@login_required(login_url='login/')
def valorar_juego(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            gid = int(data.get('game_id'))
            user_name = request.user.nombre
            estrellas = int(data.get('estrellas', 0))
            comentario = data.get('comentario', '')

            db = connections['mongodb'].database

            resultado = db.valoraciones.update_one(
                {
                    "game_id": gid,
                    "usuario": user_name
                },
                {
                    "$set": {
                        "estrellas": estrellas,
                        "comentario": comentario,
                    }
                },
                upsert=True
            )

            if resultado.matched_count > 0:
                mensaje = "¡Tu valoración ha sido actualizada!"
            else:
                mensaje = "¡Valoración creada con éxito!"

            return JsonResponse({"status": "success", "message": mensaje})

        except Exception as e:
            print(f"Error en valoración: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)


@login_required(login_url='login/')
def obtener_valoracion(request, game_id):
    db = connections['mongodb'].database

    val = db.valoraciones.find_one({
        "game_id": int(game_id),
        "usuario": request.user.nombre
    })

    if val:
        return JsonResponse({
            "existe": True,
            "estrellas": val.get("estrellas", 0),
            "comentario": val.get("comentario", "")
        })

    return JsonResponse({"existe": False})

@login_required(login_url='login/')
def mis_rankings(request):
    db = connections['mongodb'].database
    user_name = request.user.nombre

    cursor_rankings = db.ranking.find({"user": user_name})
    rankings_finales = []

    for doc in cursor_rankings:
        positions = doc.get('positions', {})
        juegos_lista = []

        for i in range(1, 11):
            pos_key = str(i)
            pos_data = positions.get(pos_key)

            if pos_data and pos_data != "null":
                game_id = pos_data.get('id') if isinstance(pos_data, dict) else pos_data

                if game_id:
                    juego_info = Games.objects.using("mongodb").filter(BGGId=game_id).first()
                    if juego_info:
                        juegos_lista.append({
                            'puesto': i,
                            'nombre': juego_info.Name,
                            'imagen': juego_info.ImagePath
                        })

        cat_id = doc.get('category_id')
        if not cat_id:
            cat_doc = db.categoria.find_one({"nombre": doc.get('category_name')})
            if cat_doc:
                cat_id = str(cat_doc['_id'])

        if juegos_lista:
            rankings_finales.append({
                'ranking_id': str(doc['_id']),
                'categoria_id': cat_id,
                'categoria': doc.get('category_name', 'Ranking Personal'),
                'juegos': juegos_lista
            })

    return render(request, 'html/mis_rankings.html', {'rankings': rankings_finales})

@login_required(login_url='login/')
def eliminar_ranking(request, ranking_id):
    if request.method == "POST":
        db = connections['mongodb'].database
        try:
            resultado = db.ranking.delete_one({"_id": ObjectId(ranking_id)})

            if resultado.deleted_count > 0:
                messages.success(request, "Ranking eliminado correctamente.")
            else:
                messages.error(request, "No se pudo encontrar el ranking a eliminar.")
        except Exception as e:
            messages.error(request, f"Error al eliminar: {e}")

    return redirect('mis_rankings')

@login_required(login_url='login/')
def obtener_comentarios_juego(request, game_id):
    db = connections['mongodb'].database

    cursor = db.valoraciones.find({
        "game_id": int(game_id),
        "comentario": {"$ne": ""}
    })

    comentarios = []
    for doc in cursor:
        comentarios.append({
            "usuario": doc.get("usuario", "Anónimo"),
            "comentario": doc.get("comentario", ""),
            "estrellas": doc.get("estrellas", 0)
        })

    return JsonResponse({"comentarios": comentarios})

@login_required(login_url='login/')
def global_ranking(request):

    db = connections['mongodb'].database

    total_rankings = db.ranking.count_documents({})
    total_votos = db.valoraciones.count_documents({})

    datos_global = {}

    cursor_ranking = db.ranking.find()
    for doc in cursor_ranking:
        positions = doc.get("positions", {})

        for pos_str, game_data in positions.items():
            if not game_data or not isinstance(game_data, dict):
                continue

            g_id = str(game_data.get("id"))

            if not g_id: continue

            if g_id not in datos_global:
                datos_global[g_id] = {
                    "suma_posiciones": 0,
                    "apariciones": 0,
                    "nombre": game_data.get("name", "Sin nombre"),
                    "imagen": game_data.get("image", "")
                }

            try:
                datos_global[g_id]["suma_posiciones"] += int(pos_str)
                datos_global[g_id]["apariciones"] += 1
            except:
                pass

    lista_ranking_global = []
    for g_id, info in datos_global.items():
        media = info["suma_posiciones"] / info["apariciones"]
        lista_ranking_global.append({
            "nombre": info["nombre"],
            "imagen": info["imagen"],
            "apariciones": info["apariciones"],
            "media_posicion": round(media, 2)
        })

    lista_ranking_global = sorted(lista_ranking_global, key=lambda x: (x['media_posicion'], -x['apariciones']))

    datos_votos = {}

    cursor_votos = db.valoraciones.find()
    for voto in cursor_votos:
        try:
            g_id = str(voto.get("game_id"))
            estrellas = float(voto.get("estrellas", 0))
            comentario = voto.get("comentario", "")

            if g_id not in datos_votos:
                juego_info = Games.objects.using("mongodb").filter(BGGId=int(g_id) if g_id.isdigit() else g_id).first()
                nombre = juego_info.Name if juego_info else f"Juego {g_id}"
                img = juego_info.ImagePath if juego_info else ""

                datos_votos[g_id] = {
                    "suma": 0, "count": 0, "comentarios": [],
                    "nombre": nombre, "imagen": img
                }

            datos_votos[g_id]["suma"] += estrellas
            datos_votos[g_id]["count"] += 1
            if comentario:
                datos_votos[g_id]["comentarios"].append(comentario)
        except Exception as e:
            print(f"Error procesando voto: {e}")

    lista_votos = []
    for g_id, info in datos_votos.items():
        media = info["suma"] / info["count"]
        lista_votos.append({
            "nombre": info["nombre"],
            "imagen": info["imagen"],
            "media_usuarios": round(media, 1),
            "total_votos": info["count"],
            "comentarios": info["comentarios"][:2]
        })

    lista_votos = sorted(lista_votos, key=lambda x: x['media_usuarios'], reverse=True)

    return render(request, 'html/estadisticas.html', {
        'ranking_global': lista_ranking_global,
        'juegos_votos': lista_votos
    })




